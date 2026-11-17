"""Make the faceplate label overlay for the 777 replica (print at 100% on sticker paper or vinyl).
Writes ../docs/faceplate_overlay.svg. Positions match make_parts.py and the real Gables G7131 panel."""
import math
import os
import importlib.util

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mp", os.path.join(here, "make_parts.py"))
mp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mp)

W, H = mp.W, mp.H
BG, FG, CUT = "#8b7b55", "#ffffff", "#ff2d55"     # Boeing brown (approx. BAC 8328), white legends
FONT = "'Arial Narrow', 'Helvetica Neue Condensed', 'Roboto Condensed', Arial, sans-serif"


def Y(y):
    return H - y


o = []
a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}" font-family="{FONT}" font-weight="bold">')
a(f'<rect width="{W}" height="{H}" rx="1.5" fill="{BG}"/>')


def text(x, y, s, size=2.7, anchor="middle"):
    a(f'<text x="{x:.2f}" y="{Y(y) + size * 0.36:.2f}" font-size="{size}" fill="{FG}" text-anchor="{anchor}">{s}</text>')


def tick(c, ang, r1, r2, w=0.4):
    t = math.radians(ang)
    a(f'<line x1="{c[0] + r1 * math.cos(t):.2f}" y1="{Y(c[1] + r1 * math.sin(t)):.2f}" '
      f'x2="{c[0] + r2 * math.cos(t):.2f}" y2="{Y(c[1] + r2 * math.sin(t)):.2f}" stroke="{FG}" stroke-width="{w}"/>')


def cut_circle(xy, d):
    a(f'<circle cx="{xy[0]}" cy="{Y(xy[1])}" r="{d / 2}" fill="#000" stroke="{CUT}" stroke-width="0.15"/>')


# ---- holes to cut (black with red outline) ----
for c in mp.CORNERS:
    cut_circle(c, mp.CORNER_HOLE)
for e in (mp.CODE_L, mp.CODE_R, mp.MODE):
    cut_circle(e, mp.ENC_HOLE)
for xy in mp.SELECTORS.values():
    cut_circle(xy, mp.SEL_HOLE)
wx, wy = mp.WINDOW
a(f'<rect x="{mp.DISPLAY[0] - wx / 2}" y="{Y(mp.DISPLAY[1] + wy / 2)}" width="{wx}" height="{wy}" fill="#000" stroke="{CUT}" stroke-width="0.15"/>')
for d in mp.DZUS:   # fastener heads glue on top of the sticker here
    a(f'<circle cx="{d[0]}" cy="{Y(d[1])}" r="4.3" fill="none" stroke="#6f6243" stroke-width="0.2"/>')
a(f'<circle cx="{mp.CENTER_SCREW[0]}" cy="{Y(mp.CENTER_SCREW[1])}" r="1.8" fill="#6f6243"/>')

S = mp.SELECTORS
# ABV / N / BLW (left knob: labels on the left, right knob: labels on the right)
c = S["abv_n_blw_left"]
for ang in (135, 180, 225):
    tick(c, ang, 5.4, 6.8)
text(12.4, 49.6, "ABV"); text(11.9, 43.3, "N"); text(12.4, 37.3, "BLW")
c = S["abv_n_blw_right"]
for ang in (45, 0, -45):
    tick(c, ang, 5.4, 6.8)
text(112.4, 49.6, "ABV"); text(111.7, 43.3, "N"); text(112.4, 37.3, "BLW")
# ABS / REL
for key, x1, x2 in (("abs_rel_left", 39.0, 47.2), ("abs_rel_right", 120.6, 128.6)):
    c = S[key]
    tick(c, 112, 5.4, 6.8); tick(c, 68, 5.4, 6.8)
    text(x1, 52.4, "ABS"); text(x2, 52.4, "REL")
# NORM / ALT SOURCE / ALTN
c = S["alt_source"]
tick(c, 115, 5.4, 6.8); tick(c, 65, 5.4, 6.8)
text(23.0, 33.6, "NORM"); text(40.6, 33.6, "ALTN")
text(21.4, 29.6, "ALT"); text(20.8, 25.9, "SOURCE")
# L / R XPNDR
c = S["xpndr_l_r"]
tick(c, 120, 5.4, 6.8); tick(c, 60, 5.4, 6.8)
text(15.2, 19.4, "L"); text(26.2, 19.4, "R"); text(27.4, 12.1, "XPNDR", anchor="start")
# Mode selector (36 degrees apart, 2 encoder clicks per position)
c = mp.MODE
for ang in (162, 126, 90, 54, 18):
    tick(c, ang, 9.4, 11.2, 0.45)
text(105.4, 22.6, "STBY", 2.5)
text(108.8, 32.2, "ALT", 2.5); text(105.9, 28.6, "RPTG  OFF", 2.5)
text(118.9, 31.6, "XPNDR", 2.5)
text(131.2, 28.6, "TA  ONLY", 2.5)
text(133.4, 22.6, "TA/RA", 2.5)
# Vertical ATC (left) and TCAS (right)
for ch, y in zip("ATC", (32.9, 28.7, 24.5)):
    text(3.9, y, ch, 3.4)
for ch, y in zip("TCAS", (34.6, 30.6, 26.6, 22.6)):
    text(141.8, y, ch, 3.4)
a(f'<text x="{W / 2}" y="{H - 0.6}" font-size="1.4" fill="#cfc6ad" text-anchor="middle" font-weight="normal">'
  f'Print at 100% scale. Cut the black holes along the red lines.</text>')
a('</svg>')
p = os.path.join(here, "..", "docs", "faceplate_overlay.svg")
open(p, "w").write("\n".join(o))
print("wrote", p)
