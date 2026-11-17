# Squawk sim bridge

Gets live altitude, speed, heading and position from MSFS 2024 on Xbox into Squawk, using the
FS2EFB add-on. With it, Squawk can make the position calls for you ("Airborne", "Leaving departure
airspace", "Top of descent", "Near the arrival airport", "Established on final", "Landed and clear
of the runway") at the right moment.

```
MSFS on Xbox (FS2EFB add-on)  ->  FS2EFB app on your phone  ->  squawk_sim_bridge.py on your Mac  ->  Squawk in Chrome
```

FS2EFB doesn't send radio frequencies or the transponder code, so those still come from your panels.

## Setup (once)

1. Buy and install **FS2EFB** (TouchingCloud) from the MSFS 2024 Marketplace on the Xbox.
2. Install the **FS2EFB** app on your phone (QR code is in the add-on's panel).
3. On your Mac, open Terminal and run `python3 --version`. If macOS offers to install the
   command line developer tools, say yes and wait for it to finish.
4. Download `squawk_sim_bridge.py` to your Mac (from this folder of the repo).

## Every flight

1. Put the Xbox, phone and Mac on the same Wi-Fi.
2. On the Mac, open Terminal and run:
   `python3 ~/Downloads/squawk_sim_bridge.py`
   It prints a line like `send to: 192.168.1.42 port 49002`. Leave that window open.
3. In the FS2EFB phone app, choose the **CUSTOM** preset, set the mode to **UDP Client**, type the
   Mac's address from step 2 into **NMEA Server IP**, and leave **NMEA Server Port** at 49002.
4. In MSFS, open the FS2EFB panel (toolbar, or the EFB app in MSFS 2024) and connect it to the phone.
   The bridge window should switch from "waiting for data" to "receiving: ... ft ... kt".
5. In Squawk (the GitHub version, in Chrome), start your flight and click **Connect** next to
   **SIM DATA**. If Chrome asks to let the page access devices on your network, click **Allow**.

Turn off **Auto calls** in the SIM DATA bar if you'd rather tap the calls yourself while still
seeing the live numbers.

## If it doesn't work

- Bridge says "waiting for data": check the phone app's IP and port, and that the phone and Mac
  are on the same Wi-Fi (not a guest network). Some routers block devices from talking to each
  other; a phone hotspot that both the Xbox and Mac join works around that.
- Squawk says it can't reach the bridge: make sure the Terminal window is still running, and that
  Chrome was allowed to access local network devices (the lock icon next to the address shows it).
- The FS2EFB app modes are named from its own side. If **UDP Client** doesn't work, try
  **TCP Client** (the bridge also listens for TCP on 49002). If the app only offers a mode where it
  waits for connections, run the bridge with `--phone <phone IP>`.
