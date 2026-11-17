"""Draw the wiring diagram (../docs/wiring.svg). Matches firmware/settings.py."""
import os

W, H = 1000, 700
o = []
a = o.append
wires = []
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif">')
a(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
a('<text x="500" y="34" font-size="22" font-weight="bold" text-anchor="middle">Squawk 777 transponder replica wiring (no soldering)</text>')

COL = {"3V3": "#d62728", "GND": "#222222", "SDA": "#1f77b4", "SCL": "#17becf", "CLK": "#2ca02c", "DT": "#ff7f0e", "SW": "#9467bd", "BTN": "#8c564b"}

WIRES_HERE = len(o)
# ESP32 board with screw terminal breakout in the middle
bx, by, bw, bh = 420, 80, 170, 480
a(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10" fill="#1d3b2a" stroke="#0d1f15" stroke-width="2"/>')
a(f'<text x="{bx+bw/2}" y="{by+26}" font-size="15" fill="#fff" text-anchor="middle" font-weight="bold">ESP32-S3-DevKitC-1</text>')
a(f'<text x="{bx+bw/2}" y="{by+44}" font-size="12" fill="#cfe" text-anchor="middle">on screw-terminal breakout</text>')
a(f'<rect x="{bx+bw/2-22}" y="{by+bh-28}" width="44" height="22" rx="4" fill="#bbb"/><text x="{bx+bw/2}" y="{by+bh-13}" font-size="11" text-anchor="middle">USB</text>')
a('<text x="500" y="58" font-size="14" text-anchor="middle">Plug the board&#39;s "USB" port (not "UART") into the Xbox. Each colored line is one jumper wire.</text>')

pins_left = ["3V3", "GND", "IO8", "IO9", "IO4", "IO5", "IO6", "GND"]
pins_right = ["3V3", "GND", "IO15", "IO16", "IO17", "IO10", "IO11", "IO13"]
pin_y = {}
for i, p in enumerate(pins_left):
    y = by + 80 + i * 46
    pin_y[("L", p, i)] = y
    a(f'<circle cx="{bx}" cy="{y}" r="6" fill="#e8c35a" stroke="#7a5d00"/><text x="{bx+12}" y="{y+5}" font-size="13" fill="#fff">{p}</text>')
for i, p in enumerate(pins_right):
    y = by + 80 + i * 46
    pin_y[("R", p, i)] = y
    a(f'<circle cx="{bx+bw}" cy="{y}" r="6" fill="#e8c35a" stroke="#7a5d00"/><text x="{bx+bw-12}" y="{y+5}" font-size="13" fill="#fff" text-anchor="end">{p}</text>')


def module(x, y, w, title, pins):
    h = 30 + 26 * len(pins)
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#f2f4f7" stroke="#555" stroke-width="1.5"/>')
    a(f'<text x="{x+w/2}" y="{y+20}" font-size="14" font-weight="bold" text-anchor="middle">{title}</text>')
    return {p: y + 42 + 26 * i for i, p in enumerate(pins)}


def wire(x1, y1, x2, y2, color, label=""):
    mx = (x1 + x2) / 2
    wires.append(f'<path d="M{x1} {y1} C{mx} {y1} {mx} {y2} {x2} {y2}" stroke="{color}" stroke-width="3" fill="none" opacity="0.9"/>')


def pin_dot(x, y, name, right_side):
    a(f'<circle cx="{x}" cy="{y}" r="5" fill="#888"/>')
    a(f'<text x="{x + (-10 if right_side else 10)}" y="{y+5}" font-size="12" text-anchor="{"end" if right_side else "start"}">{name}</text>')


# Left side modules
oled = module(60, 70, 200, "OLED 1.3 in (SH1106)", ["VCC", "GND", "SCL", "SDA"])
enL = module(60, 250, 200, "LEFT knob (KY-040)", ["CLK", "DT", "SW", "+", "GND"])
# Right side modules
enR = module(740, 70, 200, "RIGHT knob (KY-040)", ["CLK", "DT", "SW", "+", "GND"])
enM = module(740, 300, 200, "MODE knob + IDENT (KY-040)", ["CLK", "DT", "SW", "+", "GND"])

for m in (oled, enL):
    for p, y in m.items():
        pin_dot(260, y, p, True)
for m in (enR, enM):
    for p, y in m.items():
        pin_dot(740, y, p, False)

# power bus boxes (Wago lever connectors)
a('<rect x="300" y="636" width="110" height="40" rx="6" fill="#fff3d6" stroke="#c90"/><text x="355" y="652" font-size="11" text-anchor="middle">Wago #1: all 3V3</text><text x="355" y="667" font-size="11" text-anchor="middle">(red wires)</text>')
a('<rect x="600" y="636" width="110" height="40" rx="6" fill="#eee" stroke="#555"/><text x="655" y="652" font-size="11" text-anchor="middle">Wago #2: all GND</text><text x="655" y="667" font-size="11" text-anchor="middle">(black wires)</text>')

L = lambda name, i: pin_y[("L", name, i)]
R = lambda name, i: pin_y[("R", name, i)]
# signals
wire(260, oled["SDA"], bx, L("IO8", 2), COL["SDA"])
wire(260, oled["SCL"], bx, L("IO9", 3), COL["SCL"])
wire(260, enL["CLK"], bx, L("IO4", 4), COL["CLK"])
wire(260, enL["DT"], bx, L("IO5", 5), COL["DT"])
wire(260, enL["SW"], bx, L("IO6", 6), COL["SW"])
wire(740, enR["CLK"], bx + bw, R("IO15", 2), COL["CLK"])
wire(740, enR["DT"], bx + bw, R("IO16", 3), COL["DT"])
wire(740, enR["SW"], bx + bw, R("IO17", 4), COL["SW"])
wire(740, enM["CLK"], bx + bw, R("IO10", 5), COL["CLK"])
wire(740, enM["DT"], bx + bw, R("IO11", 6), COL["DT"])
wire(740, enM["SW"], bx + bw, R("IO13", 7), COL["SW"])
def poly(pts, color):
    d = "M" + " L".join(f"{x} {y}" for x, y in pts)
    wires.append(f'<path d="{d}" stroke="{color}" stroke-width="3" fill="none" stroke-linejoin="round"/>')
# power, routed around the board like a bus
poly([(bx, L("3V3", 0)), (400, L("3V3", 0)), (400, 600), (370, 600), (370, 636)], COL["3V3"])
poly([(bx, L("GND", 1)), (405, L("GND", 1)), (405, 612), (640, 612), (640, 636)], COL["GND"])
for y in (oled["VCC"], enL["+"]):
    poly([(260, y), (290, y), (290, 590), (330, 590), (330, 636)], COL["3V3"])
for y in (oled["GND"], enL["GND"]):
    poly([(260, y), (310, y), (310, 624), (620, 624), (620, 636)], COL["GND"])
for y in (enR["+"], enM["+"]):
    poly([(740, y), (725, y), (725, 580), (390, 580), (390, 636)], COL["3V3"])
for y in (enR["GND"], enM["GND"]):
    poly([(740, y), (705, y), (705, 636)], COL["GND"])
a('<text x="745" y="470" font-size="12">Pushing the MODE knob = IDENT</text>')
o[WIRES_HERE:WIRES_HERE] = wires
a('</svg>')
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "wiring.svg")
open(p, "w").write("\n".join(o))
print("wrote", p)
