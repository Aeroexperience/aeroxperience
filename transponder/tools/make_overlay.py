"""Make the faceplate label overlay (print at 100% scale on sticker paper or vinyl, then cut the holes).
Writes ../docs/faceplate_overlay.svg. Positions match make_parts.py."""
import math, os
W, H = 146.0, 104.8
DISPLAY, WINDOW = (73.0, 84.0), (26.0, 15.0)
KNOBS = [(26.0, 58.0), (120.0, 58.0)]
IDENT, IDENT_HOLE = (73.0, 58.0), 16.2
MODE, ENC_HOLE = (73.0, 22.0), 7.4
CORNER = 6.0
MODES = ["STBY", "ALT OFF", "XPNDR", "TA ONLY", "TA/RA"]
BG, FG, CUT = "#4a4f55", "#ffffff", "#ff2d55"

def Y(y): return H - y

out = []
a = out.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif">')
a(f'<rect width="{W}" height="{H}" rx="3" fill="{BG}"/>')
def text(x, y, s, size=2.6, anchor="middle", weight="bold"):
    a(f'<text x="{x:.2f}" y="{Y(y):.2f}" font-size="{size}" fill="{FG}" text-anchor="{anchor}" font-weight="{weight}">{s}</text>')
def cut_circle(x, y, d):
    a(f'<circle cx="{x}" cy="{Y(y)}" r="{d/2}" fill="#000" stroke="{CUT}" stroke-width="0.2"/>')
# holes to cut out (black with red outline)
for (x, y) in [(CORNER, CORNER), (W - CORNER, CORNER), (CORNER, H - CORNER), (W - CORNER, H - CORNER)]:
    cut_circle(x, y, 3.4)
wx, wy = WINDOW
a(f'<rect x="{DISPLAY[0]-wx/2}" y="{Y(DISPLAY[1]+wy/2)}" width="{wx}" height="{wy}" fill="#000" stroke="{CUT}" stroke-width="0.2"/>')
for (x, y) in KNOBS + [MODE]:
    cut_circle(x, y, ENC_HOLE)
cut_circle(IDENT[0], IDENT[1], IDENT_HOLE)
# legends
text(10, H - 12, "ATC", 3.2, "start")
text(DISPLAY[0], DISPLAY[1] + wy / 2 + 2.5, "CODE", 2.2)
text(IDENT[0], IDENT[1] - IDENT_HOLE / 2 - 3.2, "IDENT", 2.6)
for (x, y), lab in zip(KNOBS, ["1 · 2", "3 · 4"]):
    # tick marks around the code knobs
    for i in range(16):
        ang = 2 * math.pi * i / 16
        r1, r2 = 15.5, 17.0
        a(f'<line x1="{x+r1*math.cos(ang):.2f}" y1="{Y(y+r1*math.sin(ang)):.2f}" x2="{x+r2*math.cos(ang):.2f}" y2="{Y(y+r2*math.sin(ang)):.2f}" stroke="{FG}" stroke-width="0.35"/>')
    text(x, y - 21, lab, 2.4)
for i, lab in enumerate(MODES):
    ang = math.radians(162 - 36 * i)
    r = 17.0
    x, y = MODE[0] + r * math.cos(ang), MODE[1] + r * math.sin(ang)
    text(x, y - 0.9, lab, 2.3)
    r1, r2 = 12.0, 14.0
    a(f'<line x1="{MODE[0]+r1*math.cos(ang):.2f}" y1="{Y(MODE[1]+r1*math.sin(ang)):.2f}" x2="{MODE[0]+r2*math.cos(ang):.2f}" y2="{Y(MODE[1]+r2*math.sin(ang)):.2f}" stroke="{FG}" stroke-width="0.4"/>')
text(MODE[0], 4.5, "TRANSPONDER", 2.2)
text(W - 4, 2.2, "Print at 100% scale. Cut out the black holes along the red lines.", 1.6, "end", "normal")
a('</svg>')
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "faceplate_overlay.svg")
open(p, "w").write("\n".join(out))
print("wrote", p)
