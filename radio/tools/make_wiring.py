"""Draw the wiring diagram (../docs/wiring.svg). Matches firmware/settings.py."""
import os

W, H = 1000, 760
o = []
a = o.append
wires = []
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif">')
a(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
a('<text x="500" y="34" font-size="22" font-weight="bold" text-anchor="middle">Squawk 777 radio panel wiring (no soldering)</text>')
a('<text x="500" y="58" font-size="14" text-anchor="middle">Plug the board&#39;s "USB" port (not "UART") into the Xbox. Each colored line is one jumper wire.</text>')
COL = {"3V3": "#d62728", "GND": "#222222", "SDA": "#1f77b4", "SCL": "#17becf", "CLK": "#2ca02c", "DT": "#ff7f0e",
       "SW": "#9467bd", "BTN": "#8c564b"}
WIRES_HERE = len(o)

bx, by, bw, bh = 420, 80, 170, 540
a(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10" fill="#1d3b2a" stroke="#0d1f15" stroke-width="2"/>')
a(f'<text x="{bx + bw / 2}" y="{by + 26}" font-size="15" fill="#fff" text-anchor="middle" font-weight="bold">ESP32-S3-DevKitC-1</text>')
a(f'<text x="{bx + bw / 2}" y="{by + 44}" font-size="12" fill="#cfe" text-anchor="middle">on screw-terminal breakout</text>')
a(f'<rect x="{bx + bw / 2 - 22}" y="{by + bh - 28}" width="44" height="22" rx="4" fill="#bbb"/>'
  f'<text x="{bx + bw / 2}" y="{by + bh - 13}" font-size="11" text-anchor="middle">USB</text>')

pins_left = ["3V3", "GND", "IO8", "IO9", "IO1", "IO2", "IO4", "IO5", "IO6"]
pins_right = ["GND", "IO7", "IO15", "IO16", "IO17"]
PY = {}
for i, p in enumerate(pins_left):
    y = by + 80 + i * 46
    PY[("L", p)] = y
    a(f'<circle cx="{bx}" cy="{y}" r="6" fill="#e8c35a" stroke="#7a5d00"/><text x="{bx + 12}" y="{y + 5}" font-size="13" fill="#fff">{p}</text>')
for i, p in enumerate(pins_right):
    y = by + 80 + (i + 2) * 46 if i else by + 80 + 46
    PY[("R", p)] = y
    a(f'<circle cx="{bx + bw}" cy="{y}" r="6" fill="#e8c35a" stroke="#7a5d00"/><text x="{bx + bw - 12}" y="{y + 5}" font-size="13" fill="#fff" text-anchor="end">{p}</text>')


def module(x, y, w, title, pins, sub=""):
    h = 30 + 26 * len(pins) + (14 if sub else 0)
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#f2f4f7" stroke="#555" stroke-width="1.5"/>')
    a(f'<text x="{x + w / 2}" y="{y + 20}" font-size="14" font-weight="bold" text-anchor="middle">{title}</text>')
    if sub:
        a(f'<text x="{x + w / 2}" y="{y + 34}" font-size="11" text-anchor="middle" fill="#555">{sub}</text>')
    off = 14 if sub else 0
    return {p: y + 42 + off + 26 * i for i, p in enumerate(pins)}


def wire(x1, y1, x2, y2, color):
    mx = (x1 + x2) / 2
    wires.append(f'<path d="M{x1} {y1} C{mx} {y1} {mx} {y2} {x2} {y2}" stroke="{color}" stroke-width="3" fill="none" opacity="0.9"/>')


def poly(pts, color):
    d = "M" + " L".join(f"{x} {y}" for x, y in pts)
    wires.append(f'<path d="{d}" stroke="{color}" stroke-width="3" fill="none" stroke-linejoin="round"/>')


def pin_dot(x, y, name, right_side):
    a(f'<circle cx="{x}" cy="{y}" r="5" fill="#888"/>')
    a(f'<text x="{x + (-10 if right_side else 10)}" y="{y + 5}" font-size="12" text-anchor="{"end" if right_side else "start"}">{name}</text>')


act = module(60, 70, 200, "ACTIVE screen (0.91 in)", ["VCC", "GND", "SCL", "SDA"])
sby = module(60, 220, 200, "STANDBY screen (0.91 in)", ["VCC", "GND", "SCL", "SDA"], "mounted upside down")
knob = module(60, 384, 200, "Tuning knob (KY-040)", ["CLK", "DT", "SW", "+", "GND"])
tfr = module(740, 120, 200, "Transfer button (KY-004)", ["S", "-"])
vl = module(740, 230, 200, "VHF L button (KY-004)", ["S", "-"])
vc = module(740, 340, 200, "VHF C button (KY-004)", ["S", "-"])
vr = module(740, 450, 200, "VHF R button (KY-004)", ["S", "-"])
for m in (act, sby, knob):
    for p, y in m.items():
        pin_dot(260, y, p, True)
for m in (tfr, vl, vc, vr):
    for p, y in m.items():
        pin_dot(740, y, p, False)
a('<text x="745" y="580" font-size="12">KY-004 middle pin: leave it empty</text>')

# Wago lever connectors
a('<rect x="250" y="690" width="120" height="44" rx="6" fill="#fff3d6" stroke="#c90"/><text x="310" y="707" font-size="11" text-anchor="middle">Wago A: all 3V3</text><text x="310" y="723" font-size="11" text-anchor="middle">(red wires)</text>')
a('<rect x="440" y="690" width="120" height="44" rx="6" fill="#eee" stroke="#555"/><text x="500" y="707" font-size="11" text-anchor="middle">Wago B: GND</text><text x="500" y="723" font-size="11" text-anchor="middle">(screens, knob, TFR)</text>')
a('<rect x="640" y="690" width="120" height="44" rx="6" fill="#eee" stroke="#555"/><text x="700" y="707" font-size="11" text-anchor="middle">Wago C: GND</text><text x="700" y="723" font-size="11" text-anchor="middle">(VHF buttons)</text>')

L = lambda p: PY[("L", p)]
R = lambda p: PY[("R", p)]
wire(260, act["SDA"], bx, L("IO8"), COL["SDA"])
wire(260, act["SCL"], bx, L("IO9"), COL["SCL"])
wire(260, sby["SDA"], bx, L("IO1"), COL["SDA"])
wire(260, sby["SCL"], bx, L("IO2"), COL["SCL"])
wire(260, knob["CLK"], bx, L("IO4"), COL["CLK"])
wire(260, knob["DT"], bx, L("IO5"), COL["DT"])
wire(260, knob["SW"], bx, L("IO6"), COL["SW"])
wire(740, tfr["S"], bx + bw, R("IO7"), COL["BTN"])
wire(740, vl["S"], bx + bw, R("IO15"), COL["BTN"])
wire(740, vc["S"], bx + bw, R("IO16"), COL["BTN"])
wire(740, vr["S"], bx + bw, R("IO17"), COL["BTN"])
# power buses
poly([(bx, L("3V3")), (398, L("3V3")), (398, 660), (350, 660), (350, 690)], COL["3V3"])
poly([(bx, L("GND")), (406, L("GND")), (406, 668), (480, 668), (480, 690)], COL["GND"])
poly([(bx + bw, R("GND")), (612, R("GND")), (612, 660), (680, 660), (680, 690)], COL["GND"])
for i, y in enumerate((act["VCC"], sby["VCC"], knob["+"])):
    poly([(260, y), (282 + i * 6, y), (282 + i * 6, 690)], COL["3V3"])
for i, y in enumerate((act["GND"], sby["GND"], knob["GND"])):
    poly([(260, y), (318 + i * 6, y), (318 + i * 6, 652), (450 + i * 10, 652), (450 + i * 10, 690)], COL["GND"])
poly([(740, tfr["-"]), (720, tfr["-"]), (720, 640), (540, 640), (540, 690)], COL["GND"])
for i, m in enumerate((vl, vc, vr)):
    poly([(740, m["-"]), (700 + i * 8, m["-"]), (700 + i * 8, 690)], COL["GND"])
o[WIRES_HERE:WIRES_HERE] = wires
a('</svg>')
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "wiring.svg")
open(p, "w").write("\n".join(o))
print("wrote", p)
