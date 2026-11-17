#!/usr/bin/env python3
"""Squawk sim bridge: passes live flight data from FS2EFB to the Squawk web app.

How the data flows:
  MSFS on Xbox (FS2EFB add-on)  ->  FS2EFB app on your phone  ->  this program on your Mac  ->  Squawk in Chrome

The FS2EFB phone app sends standard GPS sentences (NMEA, plus the XGPS/XATT lines ForeFlight uses)
over your Wi-Fi. This program listens for them on port 49002 (UDP and TCP), and Squawk reads the
result from http://127.0.0.1:49080/state about once a second.

Run it:   python3 squawk_sim_bridge.py
Options:  --port 49002      port the phone app sends to
          --http 49080      port Squawk reads from
          --phone 192.168.1.23   also connect to the phone as a TCP client (only if the app is in a
                                 mode where it waits for connections)
Needs only Python 3 (no extra packages). Press Ctrl+C to stop.
"""
import argparse
import json
import math
import socket
import socketserver
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

M_TO_FT = 3.28084
STATE = {"lat": None, "lon": None, "alt": None, "gs": None, "trk": None, "hdg": None,
         "pitch": None, "roll": None, "ias": None, "vs": None, "t": 0.0, "src": "", "count": 0}
LOCK = threading.Lock()
_alt_hist = []          # (time, altitude ft) for vertical speed


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _latlon(v, hemi):
    """NMEA ddmm.mmmm -> decimal degrees."""
    v = _f(v)
    if v is None:
        return None
    deg = int(v / 100)
    d = deg + (v - deg * 100) / 60
    return -d if hemi in ("S", "W") else d


def _set(**kw):
    now = time.time()
    with LOCK:
        for k, v in kw.items():
            if isinstance(v, str):
                STATE[k] = v
            elif v is not None and not math.isnan(v):
                STATE[k] = round(v, 6) if k in ("lat", "lon") else round(v, 1)
        if kw.get("alt") is not None:
            _alt_hist.append((now, kw["alt"]))
            while _alt_hist and now - _alt_hist[0][0] > 4:
                _alt_hist.pop(0)
            if len(_alt_hist) >= 2 and _alt_hist[-1][0] - _alt_hist[0][0] > 0.8:
                (t0, a0), (t1, a1) = _alt_hist[0], _alt_hist[-1]
                STATE["vs"] = round((a1 - a0) / (t1 - t0) * 60)     # feet per minute
        STATE["t"] = now
        STATE["count"] += 1


def parse_line(line):
    """Handle one sentence. Unknown lines are ignored."""
    line = line.strip()
    if not line:
        return
    if line[0] in "$!":
        line = line[1:]
    line = line.split("*")[0]
    p = line.split(",")
    tag = p[0]
    try:
        if tag.endswith("GGA") and len(p) > 9:          # position + altitude (metres)
            alt = _f(p[9])
            _set(lat=_latlon(p[2], p[3]), lon=_latlon(p[4], p[5]),
                 alt=alt * M_TO_FT if alt is not None else None, src="NMEA")
        elif tag.endswith("RMC") and len(p) > 8:        # ground speed (knots) + track
            _set(lat=_latlon(p[3], p[4]), lon=_latlon(p[5], p[6]), gs=_f(p[7]), trk=_f(p[8]), src="NMEA")
        elif tag.startswith("XGPS") and len(p) >= 6:    # XGPSname,lon,lat,alt m,track,ground speed m/s
            gs = _f(p[5])
            alt = _f(p[3])
            _set(lon=_f(p[1]), lat=_f(p[2]), alt=alt * M_TO_FT if alt is not None else None,
                 trk=_f(p[4]), gs=gs * 1.94384 if gs is not None else None, src="XGPS")
        elif tag.startswith("XATT") and len(p) >= 4:    # XATTname,heading,pitch,roll
            _set(hdg=_f(p[1]), pitch=_f(p[2]), roll=_f(p[3]))
        elif tag == "LXWP0" and len(p) > 3:              # glider sentence: IAS km/h, baro alt m, vario
            ias = _f(p[2])
            _set(ias=ias / 1.852 if ias is not None else None)
    except Exception:
        pass


def feed(data, buf):
    buf += data.decode("ascii", "ignore")
    *lines, buf = buf.replace("\r", "\n").split("\n")
    for ln in lines:
        parse_line(ln)
    if len(buf) > 2000:
        buf = ""
    return buf


def udp_loop(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", port))
    while True:
        data, _ = s.recvfrom(65535)
        feed(data + b"\n", "")


class TCPIn(socketserver.BaseRequestHandler):
    def handle(self):
        print(f"  phone connected over TCP from {self.client_address[0]}")
        buf = ""
        while True:
            data = self.request.recv(4096)
            if not data:
                break
            buf = feed(data, buf)


def tcp_client_loop(host, port):
    while True:
        try:
            with socket.create_connection((host, port), timeout=5) as s:
                print(f"  connected to the phone at {host}:{port}")
                s.settimeout(30)
                buf = ""
                while True:
                    data = s.recv(4096)
                    if not data:
                        break
                    buf = feed(data, buf)
        except OSError:
            time.sleep(3)


class Http(BaseHTTPRequestHandler):
    def _headers(self, code=200, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_OPTIONS(self):
        self._headers(204)

    def do_GET(self):
        with LOCK:
            st = dict(STATE)
        st["age"] = round(time.time() - st["t"], 1) if st["t"] else None
        st["ok"] = st["age"] is not None and st["age"] < 5
        if self.path.startswith("/state"):
            self._headers()
            self.wfile.write(json.dumps(st).encode())
        else:
            self._headers(ctype="text/html; charset=utf-8")
            msg = ("Getting data from FS2EFB." if st["ok"] else "Waiting for FS2EFB data...")
            self.wfile.write(f"<meta http-equiv=refresh content=1><h2>Squawk sim bridge</h2><p>{msg}</p>"
                             f"<pre>{json.dumps(st, indent=1)}</pre>".encode())

    def log_message(self, *a):
        pass


def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "your Mac's IP address"


def main():
    ap = argparse.ArgumentParser(description="Pass FS2EFB flight data to Squawk.")
    ap.add_argument("--port", type=int, default=49002, help="port the FS2EFB app sends to (default 49002)")
    ap.add_argument("--http", type=int, default=49080, help="port Squawk reads from (default 49080)")
    ap.add_argument("--phone", help="phone IP, if the FS2EFB app waits for a TCP connection")
    a = ap.parse_args()

    threading.Thread(target=udp_loop, args=(a.port,), daemon=True).start()
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    tcp = socketserver.ThreadingTCPServer(("0.0.0.0", a.port), TCPIn)
    tcp.daemon_threads = True
    threading.Thread(target=tcp.serve_forever, daemon=True).start()
    if a.phone:
        threading.Thread(target=tcp_client_loop, args=(a.phone, a.port), daemon=True).start()
    http = ThreadingHTTPServer(("127.0.0.1", a.http), Http)
    threading.Thread(target=http.serve_forever, daemon=True).start()

    print("Squawk sim bridge is running.")
    print(f"  In the FS2EFB phone app, send to:  {lan_ip()}  port {a.port}")
    print(f"  Squawk reads from:  http://127.0.0.1:{a.http}/state")
    print("  Leave this window open while you fly. Ctrl+C to stop.\n")
    last = None
    try:
        while True:
            time.sleep(2)
            with LOCK:
                st = dict(STATE)
            fresh = st["t"] and time.time() - st["t"] < 5
            line = (f"  receiving: {st['alt'] or 0:7.0f} ft  {st['gs'] or 0:4.0f} kt  hdg {st['hdg'] or st['trk'] or 0:3.0f}"
                    if fresh else "  waiting for data from the phone...")
            if line != last:
                print(line)
                last = line
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
