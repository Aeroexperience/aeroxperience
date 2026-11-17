"""Draw a flat front preview of the finished panel (../docs/panel_preview.png): label sheet + knobs + display."""
import importlib.util, math, os
from PIL import Image, ImageDraw, ImageFont
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mp", os.path.join(here, "make_parts.py")); mp = importlib.util.module_from_spec(spec); spec.loader.exec_module(mp)
base = Image.open(os.path.join(here, "..", "docs", "faceplate_overlay.png")).convert("RGB")
S = base.width / mp.W
d = ImageDraw.Draw(base)
P = lambda x, y: (x * S, (mp.H - y) * S)
def circ(c, r, fill, outline=None, w=2):
    x, y = P(*c); d.ellipse([x - r * S, y - r * S, x + r * S, y + r * S], fill=fill, outline=outline, width=w)
def font(sz, bold=True):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(f): return ImageFont.truetype(f, int(sz))
    return ImageFont.load_default()
for dz in mp.DZUS:
    circ(dz, 4.3, "#7d6e4b", "#5e5236", 3); x, y = P(*dz); d.rectangle([x - 4.0 * S, y - 0.6 * S, x + 4.0 * S, y + 0.6 * S], fill="#4a4029")
for c in mp.CORNERS: circ(c, 1.9, "#a99a74", "#5e5236", 2)
bx, by = mp.BEZEL; wx, wy = mp.WINDOW; cx, cy = mp.DISPLAY
x0, y0 = P(cx - bx / 2, cy + by / 2); x1, y1 = P(cx + bx / 2, cy - by / 2); d.rounded_rectangle([x0, y0, x1, y1], radius=8, fill="#151515")
x0, y0 = P(cx - wx / 2, cy + wy / 2); x1, y1 = P(cx + wx / 2, cy - wy / 2); d.rectangle([x0, y0, x1, y1], fill="#050505")
# OLED content: same layout as the firmware (128 x 64 px across the active area)
ax0, ay0 = P(cx - 29.4 / 2, cy + 14.7 / 2); px = 29.4 * S / 128
def oled_rect(a, b, c_, e): d.rectangle([ax0 + a * px, ay0 + b * px, ax0 + c_ * px, ay0 + e * px], fill="#f2efe4")
DW, DH, T, GAP = 22, 38, 5, 6; X0 = 128 - (4 * DW + 3 * GAP) - 1; Y0 = 22
SEGS = {0: "abcdef", 1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc", 5: "afgcd", 6: "afgedc", 7: "abc"}
def digit(x, y, n):
    h2 = DH // 2
    box = {"a": (x + T, y, x + DW - T, y + T), "b": (x + DW - T, y + T + 1, x + DW, y + h2 - 1), "c": (x + DW - T, y + h2 + 1, x + DW, y + DH - T - 1),
           "d": (x + T, y + DH - T, x + DW - T, y + DH), "e": (x, y + h2 + 1, x + T, y + DH - T - 1), "f": (x, y + T + 1, x + T, y + h2 - 1),
           "g": (x + T, y + h2 - T // 2, x + DW - T, y + h2 - T // 2 + T)}
    for s in SEGS[n]: oled_rect(*box[s])
for i, n in enumerate([1, 2, 0, 0]): digit(X0 + i * (DW + GAP), Y0, n)
d.text((ax0 + 2 * px, ay0 + 1 * px), "ATC L", fill="#f2efe4", font=font(16 * px))
def knurled(c, r, n, col, edge):
    circ(c, r, col, edge, 2); x, y = P(*c)
    for i in range(n):
        a = 2 * math.pi * i / n; d.line([x + (r - 0.7) * S * math.cos(a), y + (r - 0.7) * S * math.sin(a), x + r * S * math.cos(a), y + r * S * math.sin(a)], fill=edge, width=2)
for e in (mp.CODE_L, mp.CODE_R):
    knurled(e, 8.15, 40, "#e3dcc0", "#a69f86"); knurled(e, 6.8, 34, "#ece6cd", "#b3ac93")
knurled(mp.MODE, 8.75, 44, "#e3dcc0", "#a69f86"); circ((mp.MODE[0], mp.MODE[1] + 6.6), 0.8, "#ffffff")
circ(mp.MODE, 4.0, "#f6f3e8", "#8f887a", 3); x, y = P(*mp.MODE)
f = font(2.0 * S); w = d.textlength("IDENT", font=f); d.text((x - w / 2, y - 1.2 * S), "IDENT", fill="#222", font=f)
angles = {"abv_n_blw_left": 200, "abs_rel_left": 105, "abv_n_blw_right": 20, "abs_rel_right": 100, "alt_source": 100, "xpndr_l_r": 110}
for nm, xy in mp.SELECTORS.items():
    circ(xy, 4.9, "#e7e0c5", "#9d9680", 2); x, y = P(*xy); a = math.radians(angles[nm])
    d.line([x - 3.6 * S * math.cos(a), y + 3.6 * S * math.sin(a), x + 4.4 * S * math.cos(a), y - 4.4 * S * math.sin(a)], fill="#1d1d1d", width=int(0.8 * S))
out = os.path.join(here, "..", "docs", "panel_preview.png"); base.save(out); print("wrote", out)
