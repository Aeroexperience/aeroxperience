"""Make the label sheet for the 777 radio tuning panel replica (print at 100% on sticker paper or vinyl).
Writes ../docs/label_sheet.svg with three parts: the faceplate sticker, the button plate sticker,
and the eight button-cap labels. Also writes ../docs/panel_preview.svg, a picture of the finished panel.
Positions match make_parts.py."""
import math
import os
import importlib.util

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mp", os.path.join(here, "make_parts.py"))
mp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mp)

W, H = mp.W, mp.H
BG, PLATE, FG, CUT = "#8b7b55", "#94845d", "#ffffff", "#ff2d55"     # Boeing brown (approx. BAC 8328)
FONT = "'Arial Narrow', 'Helvetica Neue Condensed', 'Roboto Condensed', Arial, sans-serif"
x1, y1, x2, y2 = mp.SURROUND
PW, PH = x2 - x1, y2 - y1


def faceplate_sticker(a, cut=True):
    """Faceplate legends in panel coordinates (origin top-left in SVG)."""
    Y = lambda y: H - y
    def text(x, y, s, size=2.7, anchor="middle"):
        a(f'<text x="{x:.2f}" y="{Y(y) + size * 0.36:.2f}" font-size="{size}" fill="{FG}" text-anchor="{anchor}">{s}</text>')
    a(f'<rect width="{W}" height="{H}" rx="1.5" fill="{BG}"/>')
    def hole_rect(cx, cy, w, h):
        a(f'<rect x="{cx - w / 2:.2f}" y="{Y(cy + h / 2):.2f}" width="{w:.2f}" height="{h:.2f}" fill="#000" '
          f'stroke="{CUT if cut else "none"}" stroke-width="0.15"/>')
    def hole_circ(c, d):
        a(f'<circle cx="{c[0]}" cy="{Y(c[1])}" r="{d / 2}" fill="#000" stroke="{CUT if cut else "none"}" stroke-width="0.15"/>')
    for c in mp.CORNERS:
        hole_circ(c, mp.CORNER_HOLE)
    hole_circ(mp.KNOB, mp.ENC_HOLE)
    for win in (mp.ACTIVE, mp.STANDBY):
        hole_rect(win[0], win[1], *mp.WINDOW)
    tx, ty = mp.TFR_CAP
    hole_rect(mp.TFR[0], mp.TFR[1], tx + 0.5, ty + 0.5)
    if cut:
        hole_rect(mp.TFR[0] - 3, mp.TFR[1] + ty / 2 + 0.5, 2.0, 1.6)
    if cut:   # the button plate covers this area; cut the button holes through both stickers
        for (x, y, _) in mp.BUTTONS.values():
            hole_rect(x, y, mp.CAP[0] + 0.5, mp.CAP[1] + 0.5)
        a(f'<rect x="{x1}" y="{Y(y2)}" width="{PW}" height="{PH}" rx="2" fill="none" stroke="#6f6243" stroke-width="0.2"/>')
    for d in mp.DZUS:
        a(f'<circle cx="{d[0]}" cy="{Y(d[1])}" r="4.3" fill="none" stroke="#6f6243" stroke-width="0.2"/>')
    a(f'<circle cx="{mp.LIGHT[0]}" cy="{Y(mp.LIGHT[1])}" r="4.6" fill="none" stroke="#6f6243" stroke-width="0.2"/>')
    text(49.0, 42.9, "ACTIVE", 2.6)
    text(93.0, 42.9, "STANDBY", 2.6)
    a(f'<polyline points="100.4,{Y(42.9)} 103.4,{Y(42.9)} 107.4,{Y(40.9)}" fill="none" stroke="{FG}" stroke-width="0.4"/>')


def plate_sticker(a, ox, oy, cut=True):
    """Button plate legends; (ox, oy) = top-left corner in the SVG."""
    def P(x, y):   # panel coords -> svg
        return ox + x - x1, oy + (y2 - y)
    a(f'<rect x="{ox}" y="{oy}" width="{PW}" height="{PH}" rx="2" fill="{PLATE}"/>')
    for (x, y, _) in mp.BUTTONS.values():
        px, py = P(x - (mp.CAP[0] + 0.5) / 2, y + (mp.CAP[1] + 0.5) / 2)
        a(f'<rect x="{px:.2f}" y="{py:.2f}" width="{mp.CAP[0] + 0.5}" height="{mp.CAP[1] + 0.5}" fill="#000" '
          f'stroke="{CUT if cut else "none"}" stroke-width="0.15"/>')
    def text(x, y, s, size=2.6):
        px, py = P(x, y)
        a(f'<text x="{px:.2f}" y="{py + size * 0.36:.2f}" font-size="{size}" fill="{FG}" text-anchor="middle">{s}</text>')
    text(24.7, 26.4, "HF SENS")
    for ch, y in zip("PNL", (21.2, 17.7, 14.2)):
        text(13.6, y, ch, 2.8)
    if cut:
        px, py = P(*mp.HF_SENS)
        a(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="6" fill="none" stroke="#6f6243" stroke-width="0.2"/>')


CAP_NAMES = ["VHF L", "VHF C", "VHF R", "HF L", "AM", "HF R", ""]


def cap_label(a, x, y, name, w=mp.CAP[0] - 0.5, h=mp.CAP[1] - 0.5, size=3.0, cut=True):
    a(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="0.8" fill="#151515" '
      f'stroke="{CUT if cut else "none"}" stroke-width="0.15"/>')
    if name == "TFR":
        cx, cy = x + w / 2, y + h / 2
        a(f'<path d="M{cx - 3.6},{cy} l1.6,-1.3 v0.8 h4 v-0.8 l1.6,1.3 l-1.6,1.3 v-0.8 h-4 v0.8 z" fill="{FG}"/>')
    elif name:
        a(f'<text x="{x + w / 2:.2f}" y="{y + h * 0.42 + size * 0.36:.2f}" font-size="{size}" fill="{FG}" text-anchor="middle">{name}</text>')


def label_sheet():
    o = []
    a = o.append
    margin = 8
    sheet_w, sheet_h = W + 2 * margin, H + PH + 40 + 2 * margin
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{sheet_w}mm" height="{sheet_h}mm" viewBox="0 0 {sheet_w} {sheet_h}" '
      f'font-family="{FONT}" font-weight="bold">')
    a(f'<g transform="translate({margin},{margin})">')
    faceplate_sticker(a)
    a('</g>')
    plate_sticker(a, margin, margin + H + 6)
    cx0, cy0 = margin + PW + 6, margin + H + 6
    for i, n in enumerate(CAP_NAMES):
        cap_label(a, cx0 + (i % 3) * 17.6, cy0 + (i // 3) * 12.0, n)
    cap_label(a, cx0 + 1 * 17.6, cy0 + 2 * 12.0, "TFR", w=mp.TFR_CAP[0] - 0.5, h=mp.TFR_CAP[1] - 0.5)
    a(f'<text x="{margin}" y="{sheet_h - 3}" font-size="2.2" fill="#444" font-weight="normal">'
      f'Print at 100% scale (no "fit to page"). The faceplate sticker must measure {W} mm wide. '
      f'Cut along the red lines and cut out the black holes.</text>')
    a('</svg>')
    p = os.path.join(here, "..", "docs", "label_sheet.svg")
    open(p, "w").write("\n".join(o))
    print("wrote", p)


SEGS = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd",
        "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg"}


def lcd(a, win, freq, letter=None):
    """Draw the screen content the way the firmware does (128 x 32 px across 22.4 x 5.6 mm)."""
    ax, ay = win[0] - 22.4 / 2, H - win[1] - 5.6 / 2
    px = 22.4 / 128
    DW, DH, T, GAP, DOT = 14, 28, 3, 4, 5
    X0 = 128 - (6 * DW + 5 * GAP + DOT) - 1
    def r(x, y, w, h):
        a(f'<rect x="{ax + x * px:.3f}" y="{ay + y * px:.3f}" width="{w * px:.3f}" height="{h * px:.3f}" fill="#f4f1e6"/>')
    digits = freq.replace(".", "")
    for i, ch in enumerate(digits):
        x = X0 + i * (DW + GAP) + (DOT if i >= 3 else 0)
        h2 = DH // 2
        bx = {"a": (x + T, 1, DW - 2 * T, T), "b": (x + DW - T, 1 + T, T, h2 - T), "c": (x + DW - T, 1 + h2, T, h2 - T),
              "d": (x + T, 1 + DH - T, DW - 2 * T, T), "e": (x, 1 + h2, T, h2 - T), "f": (x, 1 + T, T, h2 - T),
              "g": (x + T, 1 + h2 - T // 2, DW - 2 * T, T)}
        for s in SEGS[ch]:
            r(*bx[s])
    dx = X0 + 2 * (DW + GAP) + DW + (GAP + DOT) // 2 - 2
    r(dx, 1 + DH - 3, 3, 3)
    if letter:
        a(f'<text x="{ax + 2 * px:.2f}" y="{ay + 18 * px:.2f}" font-size="{16 * px:.2f}" fill="#f4f1e6" '
          f'font-family="monospace">{letter}</text>')


def knurled(a, c, r, n, fill, edge):
    a(f'<circle cx="{c[0]}" cy="{H - c[1]}" r="{r}" fill="{fill}" stroke="{edge}" stroke-width="0.3"/>')
    for i in range(n):
        t = 2 * math.pi * i / n
        a(f'<line x1="{c[0] + (r - 0.8) * math.cos(t):.2f}" y1="{H - c[1] + (r - 0.8) * math.sin(t):.2f}" '
          f'x2="{c[0] + r * math.cos(t):.2f}" y2="{H - c[1] + r * math.sin(t):.2f}" stroke="{edge}" stroke-width="0.25"/>')


def preview():
    o = []
    a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W * 8}" height="{H * 8}" viewBox="0 0 {W} {H}" '
      f'font-family="{FONT}" font-weight="bold">')
    a('<defs><radialGradient id="g" cx="40%" cy="35%"><stop offset="0" stop-color="#b8ffb0"/>'
      '<stop offset="0.5" stop-color="#22c03a"/><stop offset="1" stop-color="#0b5c18"/></radialGradient></defs>')
    faceplate_sticker(a, cut=False)
    # button plate (raised)
    a(f'<rect x="{x1 + 0.4}" y="{H - y2 + 0.5}" width="{PW}" height="{PH}" rx="2" fill="#5e5236" opacity="0.5"/>')
    plate_sticker(a, x1, H - y2, cut=False)
    for (x, y, _), n in zip(mp.BUTTONS.values(), ["VHF L", "VHF C", "VHF R", "", "HF L", "AM", "HF R"]):
        cap_label(a, x - mp.CAP[0] / 2, H - y - mp.CAP[1] / 2, n, w=mp.CAP[0], h=mp.CAP[1], cut=False)
    cap_label(a, mp.TFR[0] - mp.TFR_CAP[0] / 2, H - mp.TFR[1] - mp.TFR_CAP[1] / 2, "TFR",
              w=mp.TFR_CAP[0], h=mp.TFR_CAP[1], cut=False)
    for win in (mp.ACTIVE, mp.STANDBY):
        bx, by = mp.BEZEL
        a(f'<rect x="{win[0] - bx / 2}" y="{H - win[1] - by / 2}" width="{bx}" height="{by}" rx="1" fill="#141414" '
          f'stroke="#3a3a3a" stroke-width="0.4"/>')
        a(f'<rect x="{win[0] - 12}" y="{H - win[1] - 3.5}" width="24" height="7" fill="#050505"/>')
    lcd(a, mp.ACTIVE, "121.900", "L")
    lcd(a, mp.STANDBY, "118.300")
    for d in mp.DZUS:
        a(f'<circle cx="{d[0]}" cy="{H - d[1]}" r="4.3" fill="#7d6e4b" stroke="#5e5236" stroke-width="0.4"/>')
        a(f'<rect x="{d[0] - 4}" y="{H - d[1] - 0.6}" width="8" height="1.2" fill="#4a4029"/>')
    for c in mp.CORNERS:
        a(f'<circle cx="{c[0]}" cy="{H - c[1]}" r="1.9" fill="#a99a74" stroke="#5e5236" stroke-width="0.3"/>')
    a(f'<circle cx="{mp.LIGHT[0]}" cy="{H - mp.LIGHT[1]}" r="4.6" fill="#6b5d3e" stroke="#4a4029" stroke-width="0.4"/>')
    a(f'<circle cx="{mp.LIGHT[0]}" cy="{H - mp.LIGHT[1]}" r="3.0" fill="url(#g)"/>')
    # HF SENS knob
    c = mp.HF_SENS
    a(f'<circle cx="{c[0]}" cy="{H - c[1]}" r="6" fill="#e7e0c5" stroke="#9d9680" stroke-width="0.3"/>')
    a(f'<rect x="{c[0] - 1.6}" y="{H - c[1] - 5.5}" width="3.2" height="11" rx="1" fill="#efe9d3" stroke="#b3ac93" '
      f'stroke-width="0.25" transform="rotate(-35 {c[0]} {H - c[1]})"/>')
    a(f'<line x1="{c[0]}" y1="{H - c[1] - 1}" x2="{c[0]}" y2="{H - c[1] - 5}" stroke="#222" stroke-width="0.6" '
      f'transform="rotate(-35 {c[0]} {H - c[1]})"/>')
    knurled(a, mp.KNOB, 10.2, 48, "#e3dcc0", "#a69f86")
    knurled(a, mp.KNOB, 6.8, 34, "#ece6cd", "#b3ac93")
    a('</svg>')
    p = os.path.join(here, "..", "docs", "panel_preview.svg")
    open(p, "w").write("\n".join(o))
    print("wrote", p)


if __name__ == "__main__":
    label_sheet()
    preview()
