"""Generate the 3D-printable parts for the Squawk 777 transponder panel.

Every part fits a 180 x 180 mm printer bed. Units are millimetres.
Run:  python3 make_parts.py   (needs: pip install manifold3d trimesh numpy)
Change the numbers in the PARAMETERS section to fit your parts, then run again.
"""
import math
import os
import numpy as np
import trimesh
from manifold3d import Manifold, set_circular_segments

set_circular_segments(96)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "stl")

# ---------------- PARAMETERS ----------------
W, H = 146.0, 104.8          # Boeing panel width (5.75 in) x 11 rail units (0.375 in each)
PLATE_T = 3.0                # faceplate thickness
CORNER = 6.0                 # screw hole distance from the edges
SCREW_HOLE = 3.4             # M3 clearance hole in the faceplate
BOSS_HOLE = 2.6              # M3 self-tapping hole in the box

# Part positions on the faceplate (from the bottom-left corner, looking at the front)
DISPLAY = (73.0, 84.0)       # OLED window centre
WINDOW = (26.0, 15.0)        # OLED window size (active area is about 21.7 x 10.9)
OLED_PCB = 28.6              # pocket for the OLED board (most 0.96 in boards are 27-28 mm)
KNOB_L = (26.0, 58.0)        # left code knob
KNOB_R = (120.0, 58.0)       # right code knob
IDENT = (73.0, 58.0)         # IDENT button
IDENT_HOLE = 16.2            # 16 mm panel push button
MODE = (73.0, 22.0)          # mode selector knob
ENC_HOLE = 7.4               # KY-040 encoder bushing (M7 thread)
ENC_RECESS = (16.0, 1.2)     # thinner spot behind each encoder so the nut reaches

BOX_DEPTH = 52.0             # outside depth of the box behind the faceplate
WALL = 2.4
USB_SLOT = (14.0, 8.0)       # cable slot in the back

SHAFT_D = 6.0                # encoder shaft diameter
SHAFT_FLAT = 4.6             # D-shaft: distance from the flat to the far side
SHAFT_FIT = 0.15             # extra clearance (raise if knobs are too tight)


def cyl(h, r, r2=None, center=False):
    return Manifold.cylinder(h, r, r if r2 is None else r2, 0, center)


def box(x, y, z, center=False):
    return Manifold.cube([x, y, z], center)


def save(m, name):
    mesh = m.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    f = np.asarray(mesh.tri_verts)
    t = trimesh.Trimesh(vertices=v, faces=f, process=False)
    path = os.path.join(OUT, name + ".stl")
    t.export(path)
    b = t.bounds
    size = b[1] - b[0]
    print(f"{name:22s} {size[0]:6.1f} x {size[1]:6.1f} x {size[2]:5.1f} mm  watertight={t.is_watertight}")
    return t


def corners():
    return [(CORNER, CORNER), (W - CORNER, CORNER), (CORNER, H - CORNER), (W - CORNER, H - CORNER)]


# ---------------- faceplate ----------------
def faceplate():
    p = box(W, H, PLATE_T)
    # rounded corners
    r = 3.0
    for (cx, cy, sx, sy) in [(0, 0, 1, 1), (W, 0, -1, 1), (0, H, 1, -1), (W, H, -1, -1)]:
        cut = box(r, r, PLATE_T + 2).translate([cx - (r if sx < 0 else 0), cy - (r if sy < 0 else 0), -1])
        keep = cyl(PLATE_T + 2, r).translate([cx + sx * r, cy + sy * r, -1])
        p = p - (cut - keep)
    for (x, y) in corners():
        p = p - cyl(PLATE_T + 2, SCREW_HOLE / 2).translate([x, y, -1])
        p = p - cyl(1.6, 3.2, 1.7).translate([x, y, PLATE_T - 1.6 + 0.001])   # countersink look
    # OLED window, slightly bevelled
    wx, wy = WINDOW
    p = p - box(wx, wy, PLATE_T + 2).translate([DISPLAY[0] - wx / 2, DISPLAY[1] - wy / 2, -1])
    p = p - box(wx + 2, wy + 2, 0.8).translate([DISPLAY[0] - wx / 2 - 1, DISPLAY[1] - wy / 2 - 1, PLATE_T - 0.8 + 0.001])
    # encoders: through hole + thinner area behind for the nut
    for (x, y) in (KNOB_L, KNOB_R, MODE):
        p = p - cyl(PLATE_T + 2, ENC_HOLE / 2).translate([x, y, -1])
        p = p - cyl(ENC_RECESS[1] + 0.001, ENC_RECESS[0] / 2).translate([x, y, -0.001])
    # IDENT button
    p = p - cyl(PLATE_T + 2, IDENT_HOLE / 2).translate([IDENT[0], IDENT[1], -1])
    # OLED pocket frame on the back (z below 0)
    fo = OLED_PCB + 3.2
    frame = box(fo, fo, 4.0).translate([DISPLAY[0] - fo / 2, DISPLAY[1] - fo / 2, -4.0])
    frame = frame - box(OLED_PCB, OLED_PCB, 6).translate([DISPLAY[0] - OLED_PCB / 2, DISPLAY[1] - OLED_PCB / 2, -5])
    # two screw bosses beside the frame for the OLED clamp
    for sx in (-1, 1):
        bx = DISPLAY[0] + sx * (fo / 2 + 3.0)
        b = cyl(4.0, 3.0).translate([bx, DISPLAY[1], -4.0]) - cyl(5, 0.85).translate([bx, DISPLAY[1], -4.5])
        frame = frame + b
    p = p + frame
    # small stiffening ribs along the top and bottom edges, clear of the box walls
    for y in (WALL + 1.0, H - WALL - 3.0):
        p = p + box(W - 2 * (WALL + 12), 2.0, 3.0).translate([WALL + 12, y, -3.0])
    return p


def oled_clamp():
    fo = OLED_PCB + 3.2
    span = fo + 6.0
    c = box(span + 6, 30, 2.0).translate([-(span + 6) / 2, -15, 0])
    c = c - box(20, 18, 4).translate([-10, -9, -1])           # room for parts on the back of the OLED
    c = c - box(13, 5, 4).translate([-6.5, 10, -1])           # header pins
    for sx in (-1, 1):
        c = c - cyl(4, 1.15).translate([sx * span / 2, 0, -1])
    return c


# ---------------- box ----------------
def back_box():
    b = box(W, H, BOX_DEPTH)
    b = b - box(W - 2 * WALL, H - 2 * WALL, BOX_DEPTH).translate([WALL, WALL, WALL])
    for (x, y) in corners():
        boss = cyl(BOX_DEPTH - WALL, 4.0).translate([x, y, WALL])
        b = b + boss
        b = b - cyl(BOX_DEPTH, BOSS_HOLE / 2).translate([x, y, WALL + 6])
    # USB cable slot in the back, near the bottom edge
    ux, uy = USB_SLOT
    b = b - box(ux, uy, WALL + 2).translate([W / 2 - ux / 2, WALL + 4, -1])
    # vent slots
    for i in range(6):
        x = 30 + i * 15
        b = b - box(3.0, 30.0, WALL + 2).translate([x, H - WALL - 40, -1])
    return b


# ---------------- knobs ----------------
def shaft_hole(depth, d_shaft):
    hole = cyl(depth, SHAFT_D / 2 + SHAFT_FIT)
    if d_shaft:
        flat_cut = box(SHAFT_D + 2, SHAFT_D + 2, depth).translate(
            [-(SHAFT_D + 2) / 2, -(SHAFT_D / 2) + SHAFT_FLAT + SHAFT_FIT, 0])
        hole = hole - flat_cut
    return hole


def flutes(m, r, h, n, z0=0.0, depth=0.9):
    for i in range(n):
        a = 2 * math.pi * i / n
        m = m - cyl(h + 0.2, depth).translate([r * math.cos(a), r * math.sin(a), z0 - 0.1])
    return m


def code_knob(d_shaft):
    # Looks like the 777's two-part concentric knob: wide skirt + taller centre grip.
    skirt = cyl(5.0, 14.0, 13.0)
    skirt = flutes(skirt, 14.0, 5.0, 36, depth=0.8)
    grip = cyl(11.0, 8.5, 8.0).translate([0, 0, 5.0])
    grip = flutes(grip, 8.5, 11.0, 18, z0=5.0, depth=0.9)
    k = skirt + grip
    k = k - shaft_hole(13.0, d_shaft).translate([0, 0, -0.01])
    k = k - cyl(0.6, 6.0).translate([0, 0, 15.5])            # shallow dish on top
    return k


def mode_knob(d_shaft):
    # Bar-style selector knob with a pointer line.
    base = cyl(4.0, 11.0, 10.5)
    bar = box(20.0, 7.0, 10.0).translate([-10.0, -3.5, 4.0])
    k = base + bar + cyl(10.0, 5.0).translate([0, 0, 4.0])
    # pointer groove on top of the bar, pointing at +Y
    k = k - box(1.2, 9.0, 1.0).translate([-0.6, 1.5, 13.01])
    k = k - box(1.2, 4.0, 1.0).translate([-0.6, 10.0, 3.01])
    k = k.rotate([0, 0, 90])   # bar along Y so the pointer is on the bar
    k = k - shaft_hole(12.0, d_shaft).translate([0, 0, -0.01])
    return k


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fp = faceplate()
    save(fp.rotate([180, 0, 0]).translate([0, H, PLATE_T]), "faceplate")   # print face-down
    save(oled_clamp(), "oled_clamp")
    save(back_box(), "back_box")
    for d, tag in ((True, "Dshaft"), (False, "knurled")):
        save(code_knob(d), f"code_knob_{tag}")
        save(mode_knob(d), f"mode_knob_{tag}")
