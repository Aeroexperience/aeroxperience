"""Generate the 3D-printable parts for the Squawk 777 transponder panel.

A replica of the Gables Engineering G7131 ATC/TCAS panel used in the Boeing 777
(5.735 in wide x 2.235 in tall). Layout measured from Gables' product photo.
Every part fits a 180 x 180 mm printer bed. Units are millimetres.

Run:  python3 make_parts.py   (needs: pip install manifold3d trimesh numpy)
Change the numbers in the PARAMETERS section to fit your parts, then run again.
It also checks that the electronics fit behind the panel without touching.
"""
import math
import os
import numpy as np
import trimesh
from manifold3d import Manifold, set_circular_segments

set_circular_segments(96)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "stl")

# ---------------- PARAMETERS ----------------
W, H = 145.7, 56.8           # real panel: 5.735 x 2.235 in
PLATE_T = 3.0                # faceplate thickness

# Positions on the faceplate, from the bottom-left corner looking at the front (mm)
DISPLAY = (72.5, 36.4)       # display window centre
BEZEL = (38.3, 22.6)         # black bezel around the window (outer size)
WINDOW = (31.0, 16.5)        # opening for the screen (1.3 in OLED active area is about 29.4 x 14.7)
CODE_L = (51.3, 11.7)        # left code knob
CODE_R = (86.6, 11.7)        # right code knob
MODE = (118.9, 16.3)         # mode selector (IDENT is its push button)
SELECTORS = {                # small selector knobs (they turn, but are not wired)
    "abv_n_blw_left": (20.4, 43.3),
    "abs_rel_left": (43.1, 43.3),
    "abv_n_blw_right": (102.0, 43.3),
    "abs_rel_right": (124.7, 43.3),
    "alt_source": (31.7, 26.9),
    "xpndr_l_r": (20.7, 12.1),
}
DZUS = [(5.2, 42.0), (5.2, 14.6), (140.5, 42.0), (140.5, 14.6)]   # quarter-turn fastener heads (look only)
CORNERS = [(5.2, 5.5), (140.5, 5.5), (5.2, 51.7), (140.5, 51.7)]  # real screws: faceplate to box (M2)
CENTER_SCREW = (69.4, 12.5)  # small screw between the code knobs (look only)

ENC_HOLE = 7.4               # KY-040 bushing (M7 thread)
ENC_RECESS = (17.5, 1.2)     # thinner spot behind each encoder so its nut reaches
SEL_HOLE = 4.4               # hole for the selector axles
CORNER_HOLE = 2.4            # M2 clearance
BOSS_HOLE = 1.7              # M2 self-tapping

# 1.3 in SH1106 OLED module (measure yours: most are 35.4 x 33.5)
OLED_PCB = (35.4, 33.5)
OLED_STACK = 3.2             # glass + board thickness
OLED_SLOP_Y = 1.5            # room to slide the screen up/down to centre it in the window

BOX_DEPTH = 100.0            # real panel is 5 in deep; 100 mm holds the board comfortably
WALL = 1.8
USB_SLOT = (14.0, 8.0)

SHAFT_D = 6.0                # encoder shaft diameter
SHAFT_FLAT = 4.6             # D-shaft: distance from the flat to the far side
SHAFT_FIT = 0.15             # extra clearance (raise if knobs are too tight)
SHAFT_DEPTH = 9.0            # how far the knob goes onto the shaft


def cyl(h, r, r2=None, center=False):
    return Manifold.cylinder(h, r, r if r2 is None else r2, 0, center)


def box(x, y, z, center=False):
    return Manifold.cube([x, y, z], center)


def save(m, name):
    mesh = m.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    f = np.asarray(mesh.tri_verts)
    t = trimesh.Trimesh(vertices=v, faces=f, process=False)
    t.export(os.path.join(OUT, name + ".stl"))
    s = t.bounds[1] - t.bounds[0]
    print(f"{name:22s} {s[0]:6.1f} x {s[1]:6.1f} x {s[2]:5.1f} mm  watertight={t.is_watertight}")
    return t


def at(m, xy, z=0.0):
    return m.translate([xy[0], xy[1], z])


# ---------------- faceplate ----------------
def clamp_boss_dx():
    return OLED_PCB[0] / 2 + 0.3 + 1.2 + 3.4


def faceplate():
    p = box(W, H, PLATE_T)
    r = 1.5
    for (cx, cy, sx, sy) in [(0, 0, 1, 1), (W, 0, -1, 1), (0, H, 1, -1), (W, H, -1, -1)]:
        cut = box(r, r, PLATE_T + 2).translate([cx - (r if sx < 0 else 0), cy - (r if sy < 0 else 0), -1])
        keep = cyl(PLATE_T + 2, r).translate([cx + sx * r, cy + sy * r, -1])
        p = p - (cut - keep)
    # corner screws (real) and the small centre screw (look only)
    for c in CORNERS:
        p = p - at(cyl(PLATE_T + 2, CORNER_HOLE / 2), c, -1)
    # The front stays flat so it prints face-down and smooth. Raised details (fastener heads,
    # display bezel) are separate parts that glue on; shallow marks show where they go.
    cross = box(3.0, 0.5, 0.8, True) + box(0.5, 3.0, 0.8, True)
    p = p - at(cyl(0.5, 1.8), CENTER_SCREW, PLATE_T - 0.5) - at(cross, CENTER_SCREW, PLATE_T - 0.4)
    for d in DZUS:
        p = p - at(cyl(0.4, 4.4), d, PLATE_T - 0.4)
    wx, wy = WINDOW
    p = p - box(wx, wy, PLATE_T + 2).translate([DISPLAY[0] - wx / 2, DISPLAY[1] - wy / 2, -1])
    # encoders: through hole + thin spot behind for the nut
    for e in (CODE_L, CODE_R, MODE):
        p = p - at(cyl(PLATE_T + 2, ENC_HOLE / 2), e, -1)
        p = p - at(cyl(ENC_RECESS[1] + 0.01, ENC_RECESS[0] / 2), e, -0.01)
    for xy in SELECTORS.values():
        p = p - at(cyl(PLATE_T + 2, SEL_HOLE / 2), xy, -1)
    # OLED guides behind the window: side rails + two screw bosses for the clamp
    px, py = OLED_PCB
    rail_h = py - 6
    for sx in (-1, 1):
        rx = DISPLAY[0] + sx * (px / 2 + 0.9) - 0.6
        p = p + box(1.2, rail_h, OLED_STACK + 0.6).translate([rx, DISPLAY[1] - rail_h / 2, -(OLED_STACK + 0.6)])
        bxx = DISPLAY[0] + sx * clamp_boss_dx()
        boss = at(cyl(OLED_STACK, 3.0), (bxx, DISPLAY[1]), -OLED_STACK) - at(cyl(5, 0.85), (bxx, DISPLAY[1]), -OLED_STACK - 1)
        p = p + boss
    return p


def oled_clamp():
    dx = clamp_boss_dx()
    c = box(2 * dx + 7, 24, 2.0).translate([-(2 * dx + 7) / 2, -12, 0])
    c = c - box(OLED_PCB[0] - 6, 16, 4).translate([-(OLED_PCB[0] - 6) / 2, -8, -1])   # parts on the back of the screen
    for sx in (-1, 1):
        c = c - at(cyl(4, 1.15), (sx * dx, 0), -1)
    return c


# ---------------- box ----------------
def back_box():
    b = box(W, H, BOX_DEPTH)
    b = b - box(W - 2 * WALL, H - 2 * WALL, BOX_DEPTH).translate([WALL, WALL, WALL])
    for c in CORNERS:
        b = b + at(cyl(BOX_DEPTH - WALL, 3.0), c, WALL)
        b = b - at(cyl(BOX_DEPTH, BOSS_HOLE / 2), c, BOX_DEPTH - 12)
    ux, uy = USB_SLOT
    b = b - box(ux, uy, WALL + 2).translate([W / 2 - ux / 2, WALL + 6, -1])
    for i in range(7):
        b = b - box(3.0, 22.0, WALL + 2).translate([28 + i * 14, H - WALL - 30, -1])
    return b


# ---------------- knobs ----------------
def shaft_hole(depth, d_shaft):
    hole = cyl(depth, SHAFT_D / 2 + SHAFT_FIT)
    if d_shaft:
        hole = hole - box(SHAFT_D + 2, SHAFT_D + 2, depth).translate(
            [-(SHAFT_D + 2) / 2, -(SHAFT_D / 2) + SHAFT_FLAT + SHAFT_FIT, 0])
    return hole


def knurl(m, r, h, n, z0=0.0, depth=0.6):
    for i in range(n):
        a = 2 * math.pi * i / n
        m = m - cyl(h + 0.2, depth).translate([r * math.cos(a), r * math.sin(a), z0 - 0.1])
    return m


def code_knob(d_shaft):
    # 777 code knob: knurled skirt with a slightly smaller knurled cap on top
    skirt = knurl(cyl(5.0, 8.15), 8.15, 5.0, 40)
    cap = knurl(cyl(6.0, 6.8, 6.4).translate([0, 0, 5.0]), 6.8, 6.0, 34, z0=5.0)
    k = skirt + cap
    return k - shaft_hole(SHAFT_DEPTH, d_shaft).translate([0, 0, -0.01])


def mode_knob(d_shaft):
    # mode selector: knurled ring with a pointer dot and a pocket for the IDENT cap
    h = 11.0
    k = knurl(cyl(h, 8.75, 8.4), 8.75, h, 44)
    k = k - cyl(2.6, 4.25).translate([0, 0, h - 2.5])                 # IDENT cap pocket
    k = k + cyl(0.6, 0.8).translate([0, 6.6, h])                      # pointer dot at 12 o'clock
    return k - shaft_hole(SHAFT_DEPTH - 1, d_shaft).translate([0, 0, -0.01])


def dzus_head():
    # quarter-turn fastener head (print 4), glue into the round marks on the faceplate
    return cyl(1.8, 4.3, 4.1) - box(8.6, 1.2, 1.0).translate([-4.3, -0.6, 1.0])


def display_bezel():
    # print in black: the raised frame around the display window
    bx, by = BEZEL
    wx, wy = WINDOW
    return box(bx, by, 1.2).translate([-bx / 2, -by / 2, 0]) - box(wx, wy, 3).translate([-wx / 2, -wy / 2, -1])


def ident_cap():
    return cyl(3.3, 4.0) + cyl(0.5, 4.0, 3.6).translate([0, 0, 3.3])


def selector_knob():
    # small bar-pointer knob (ABV/N/BLW, ABS/REL, ALT SOURCE, XPNDR L/R)
    k = cyl(7.2, 4.9) + cyl(0.8, 4.9, 4.2).translate([0, 0, 7.2])
    k = k - box(1.0, 4.6, 1.0).translate([-0.5, 0.2, 7.4])             # pointer line (fill with black marker)
    return k - cyl(6.0, 1.95).translate([0, 0, -0.01])                # press-fit onto the axle


def selector_axle():
    # goes through the panel from behind; the knob presses onto the front end
    return cyl(1.6, 3.5) + cyl(PLATE_T + 0.4 + 5.6, 2.0).translate([0, 0, 1.6])


# ---------------- fit check ----------------
def fit_check():
    """Rough boxes for the parts behind the panel. z = 0 is the back of the faceplate, negative = into the box."""
    parts = []

    def add(name, x1, x2, y1, y2, z1, z2):
        parts.append((name, x1, x2, y1, y2, z1, z2))
    for nm, e in (("code-L", CODE_L), ("code-R", CODE_R), ("mode", MODE)):
        x, y = e
        add(nm + " encoder", x - 6, x + 6, y - 6, y + 6, -6.6, 0)
        add(nm + " board", x - 9.5, x + 9.5, y - 7, y + 19, -8.2, -6.6)            # KY-040, pins pointing up
        add(nm + " wires", x - 6.5, x + 6.5, y + 19, y + 33, -10.5, -6.8)
    px, py = OLED_PCB
    add("screen glass+board", DISPLAY[0] - px / 2, DISPLAY[0] + px / 2, DISPLAY[1] - py / 2 - OLED_SLOP_Y,
        DISPLAY[1] + py / 2 + OLED_SLOP_Y, -OLED_STACK, 0)
    dx = clamp_boss_dx()
    add("screen clamp", DISPLAY[0] - dx - 3.5, DISPLAY[0] + dx + 3.5, DISPLAY[1] - 12, DISPLAY[1] + 12,
        -OLED_STACK - 2.0, -OLED_STACK)
    add("screen wires", DISPLAY[0] - 5.5, DISPLAY[0] + 5.5, DISPLAY[1] + py / 2 - 3, DISPLAY[1] + py / 2 + OLED_SLOP_Y,
        -30, -OLED_STACK)
    for nm, xy in SELECTORS.items():
        add(nm + " axle", xy[0] - 3.5, xy[0] + 3.5, xy[1] - 3.5, xy[1] + 3.5, -1.6, 0)
    for c in CORNERS:
        add("corner post", c[0] - 3, c[0] + 3, c[1] - 3, c[1] + 3, -BOX_DEPTH, 0)
    problems = []
    for i in range(len(parts)):
        a = parts[i]
        if "corner" not in a[0] and (a[1] < WALL or a[2] > W - WALL or a[3] < WALL or a[4] > H - WALL):
            problems.append(f"{a[0]} touches the box wall")
        for j in range(i + 1, len(parts)):
            b = parts[j]
            ga, gb = a[0].split()[0], b[0].split()[0]
            if ga == gb and ga in ("code-L", "code-R", "mode", "screen"):
                continue
            ov = (min(a[2], b[2]) - max(a[1], b[1]), min(a[4], b[4]) - max(a[3], b[3]), min(a[6], b[6]) - max(a[5], b[5]))
            if all(o > 0 for o in ov):
                problems.append(f"{a[0]} hits {b[0]}")
    print("fit check:", "everything fits" if not problems else "; ".join(problems))
    return problems


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".stl"):
            os.remove(os.path.join(OUT, f))
    fit_check()
    fp = faceplate()
    save(fp.rotate([180, 0, 0]).translate([0, H, PLATE_T]), "faceplate")      # print face-down
    save(dzus_head(), "dzus_head")
    save(display_bezel(), "display_bezel")
    save(back_box(), "back_box")
    save(oled_clamp(), "oled_clamp")
    for d, tag in ((True, "Dshaft"), (False, "knurled")):
        save(code_knob(d), f"code_knob_{tag}")
        save(mode_knob(d), f"mode_knob_{tag}")
    save(ident_cap(), "ident_cap")
    save(selector_knob(), "selector_knob")
    save(selector_axle(), "selector_axle")
