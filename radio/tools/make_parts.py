"""Generate the 3D-printable parts for the Squawk 777 radio tuning panel.

A replica of the Boeing 777 Radio Tuning Panel (RTP): 5.735 in wide x 2.61 in tall, the
standard size for Boeing pedestal radio panels. Layout measured from photos of the real panel.
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
W, H = 145.7, 66.3           # real panel: 5.735 x 2.61 in
PLATE_T = 3.0                # faceplate thickness
SURROUND_T = 1.2             # raised plate around the buttons (glues on the front)

# Positions on the faceplate, from the bottom-left corner looking at the front (mm)
ACTIVE = (39.3, 51.7)        # ACTIVE window centre
STANDBY = (106.4, 51.7)      # STANDBY window centre
BEZEL = (46.4, 12.1)         # black LCD frame (outer size)
WINDOW = (24.0, 7.0)         # opening for the screen (0.91 in OLED shows 22.4 x 5.6)
LIGHT = (73.0, 57.3)         # green OFFSIDE TUNING light (look only)
TFR = (73.4, 45.3)           # transfer button
TFR_CAP = (11.8, 6.2)
KNOB = (119.4, 33.8)         # tuning knob
HF_SENS = (26.0, 38.1)       # HF SENS knob (look only)
BUTTONS = {                  # name: (x, y, wired?)
    "VHF L": (43.5, 31.3, True), "VHF C": (62.5, 31.3, True), "VHF R": (81.4, 31.3, True),
    "PNL OFF": (24.7, 17.7, False), "HF L": (43.5, 17.7, False), "AM": (62.5, 17.7, False),
    "HF R": (81.4, 17.7, False),
}
CAP = (16.7, 11.1)           # button cap face
SURROUND = (9.9, 7.9, 96.5, 40.7)   # x1, y1, x2, y2 of the raised button plate
DZUS = [(4.9, 53.8), (4.9, 17.3), (140.8, 53.8), (140.8, 17.3)]   # fastener heads (look only)
CORNERS = [(4.9, 5.5), (140.8, 5.5), (4.9, 60.8), (140.8, 60.8)]  # real screws: faceplate to box (M2)

ENC_HOLE = 7.4               # KY-040 bushing (M7 thread)
ENC_RECESS = (17.5, 1.2)     # thinner spot behind the encoder so its nut reaches
ENC_ANGLE = 210              # direction the KY-040 pins point (degrees, 0 = right, 270 = down)
CORNER_HOLE = 2.4            # M2 clearance
BOSS_HOLE = 1.7              # M2 self-tapping
CAP_GAP = 0.25               # clearance around each button cap

# 0.91 in 128x32 OLED module (measure yours: most are 38 x 12)
OLED_PCB = (38.0, 12.0)
OLED_STACK = 2.6             # glass + board thickness
OLED_OFFSET = 2.5            # screen centre sits this far right of the board centre (pins on the left)
OLED_SLOP = 2.0              # room to slide the screen left/right to centre it in the window

# KY-004 button module (measure yours: most are 15 x 19.2, switch 5 mm from one end)
KY004 = (15.0, 19.2, 1.6)
KY004_SW = 5.0               # switch centre to the near end of the board
SWITCH_H = 5.0               # tact switch height above the board (6 x 6 x 5 switch)
TAPE = 1.0                   # foam tape thickness
VHF_TIP = -3.5               # where the VHF button stems end (z, 0 = back of faceplate)
TFR_TIP = -10.5              # the transfer button sits deeper, under the VHF wires
TFR_STEM_DX = -1.7           # its stem sits a little left of centre, between the VHF boards
TFR_STEM = 3.0

BOX_DEPTH = 100.0
WALL = 1.8
WALL_TOP = 1.2               # thinner top wall: the button plugs need the room
USB_SLOT = (14.0, 8.0)

SHAFT_D = 6.0                # encoder shaft diameter
SHAFT_FLAT = 4.6             # D-shaft: distance from the flat to the far side
SHAFT_FIT = 0.15             # extra clearance (raise if the knob is too tight)
SHAFT_DEPTH = 9.0


def cyl(h, r, r2=None, center=False):
    return Manifold.cylinder(h, r, r if r2 is None else r2, 0, center)


def box(x, y, z, center=False):
    return Manifold.cube([x, y, z], center)


def cbox(cx, cy, sx, sy, z1, z2):
    """Box centred on (cx, cy) in x/y, from z1 to z2."""
    return box(sx, sy, z2 - z1).translate([cx - sx / 2, cy - sy / 2, z1])


def rbox(sx, sy, h, r):
    """Rounded-corner plate, corner at the origin."""
    m = box(sx - 2 * r, sy, h).translate([r, 0, 0]) + box(sx, sy - 2 * r, h).translate([0, r, 0])
    for x in (r, sx - r):
        for y in (r, sy - r):
            m = m + cyl(h, r).translate([x, y, 0])
    return m


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


# ---------------- positions of the hidden parts ----------------
def vhf_backer_z():
    return VHF_TIP - SWITCH_H - KY004[2] - TAPE        # front face of the backer bar


def tfr_backer_z():
    return TFR_TIP - SWITCH_H - KY004[2] - TAPE


VHF_POSTS = [(31.3, 31.3), (93.4, 31.3)]
TFR_POST = (73.4, 58.5)
CLAMP_DX = 24.5              # screen clamp screws, either side of the window centre


# The STANDBY screen is mounted upside down (pins on the right) so its plug clears the VHF R wires.
FLIPPED = {STANDBY}


def oled_center(win):
    return (win[0] + (OLED_OFFSET if win in FLIPPED else -OLED_OFFSET), win[1])


def oled_pin_x(win):
    cx = oled_center(win)[0]
    return cx + OLED_PCB[0] / 2 - 1.3 if win in FLIPPED else cx - OLED_PCB[0] / 2 + 1.3


# ---------------- faceplate ----------------
def faceplate():
    p = box(W, H, PLATE_T)
    r = 1.5
    for (cx, cy, sx, sy) in [(0, 0, 1, 1), (W, 0, -1, 1), (0, H, 1, -1), (W, H, -1, -1)]:
        cut = box(r, r, PLATE_T + 2).translate([cx - (r if sx < 0 else 0), cy - (r if sy < 0 else 0), -1])
        keep = cyl(PLATE_T + 2, r).translate([cx + sx * r, cy + sy * r, -1])
        p = p - (cut - keep)
    for c in CORNERS:
        p = p - at(cyl(PLATE_T + 2, CORNER_HOLE / 2), c, -1)
    # The front stays flat so it prints face-down and smooth. Raised details glue on;
    # shallow marks show where they go.
    for d in DZUS:
        p = p - at(cyl(0.4, 4.4), d, PLATE_T - 0.4)
    p = p - at(cyl(0.4, 4.8), LIGHT, PLATE_T - 0.4)
    p = p - at(cyl(0.4, 6.2), HF_SENS, PLATE_T - 0.4) if not inside_surround(HF_SENS) else p
    for win in (ACTIVE, STANDBY):
        p = p - cbox(win[0], win[1], WINDOW[0], WINDOW[1], -1, PLATE_T + 1)
        p = p - cbox(win[0], win[1], BEZEL[0] + 0.6, BEZEL[1] + 0.6, PLATE_T - 0.4, PLATE_T + 1)
    # buttons
    for (x, y, _) in BUTTONS.values():
        p = p - cbox(x, y, CAP[0] + 2 * CAP_GAP, CAP[1] + 2 * CAP_GAP, -1, PLATE_T + 1)
    p = p - cbox(TFR[0], TFR[1], TFR_CAP[0] + 2 * CAP_GAP, TFR_CAP[1] + 2 * CAP_GAP, -1, PLATE_T + 1)
    p = p - cbox(TFR[0] - 3, TFR[1] + TFR_CAP[1] / 2 + 0.5, 2.0, 1.6, -1, PLATE_T + 1)   # key: the cap only fits one way
    # surround outline mark
    x1, y1, x2, y2 = SURROUND
    p = p - (rbox(x2 - x1 + 0.6, y2 - y1 + 0.6, 0.4, 2.3).translate([x1 - 0.3, y1 - 0.3, PLATE_T - 0.4]) -
             rbox(x2 - x1 - 1.4, y2 - y1 - 1.4, 0.6, 1.3).translate([x1 + 0.7, y1 + 0.7, PLATE_T - 0.5]))
    # encoder: through hole + thin spot behind for the nut
    p = p - at(cyl(PLATE_T + 2, ENC_HOLE / 2), KNOB, -1)
    p = p - at(cyl(ENC_RECESS[1] + 0.01, ENC_RECESS[0] / 2), KNOB, -0.01)
    # screens: side stops (left/right with slop) and two clamp bosses each
    for win in (ACTIVE, STANDBY):
        cx, cy = oled_center(win)
        px, py = OLED_PCB
        for sy in (-1, 1):   # top and bottom rails
            p = p + cbox(cx, cy + sy * (py / 2 + 0.9), px + 2 * OLED_SLOP, 1.2, -OLED_STACK, 0)
        for sx in (-1, 1):
            bx = win[0] + sx * CLAMP_DX
            p = p + at(cyl(OLED_STACK, 2.8), (bx, cy), -OLED_STACK) - at(cyl(5, 0.85), (bx, cy), -OLED_STACK - 1)
    # posts for the button backers
    for post in VHF_POSTS:
        p = p + cbox(post[0], post[1], 5.0, 5.0, vhf_backer_z(), 0) - at(cyl(8, 0.85), post, vhf_backer_z() - 1)
    p = p + cbox(TFR_POST[0], TFR_POST[1], 5.0, 5.0, tfr_backer_z(), 0) - at(cyl(8, 0.85), TFR_POST, tfr_backer_z() - 1)
    return p


def inside_surround(xy):
    x1, y1, x2, y2 = SURROUND
    return x1 < xy[0] < x2 and y1 < xy[1] < y2


# ---------------- glue-on front parts ----------------
def surround():
    """Raised plate around the buttons (print in the panel colour, glue on the front)."""
    x1, y1, x2, y2 = SURROUND
    s = rbox(x2 - x1, y2 - y1, SURROUND_T, 2.0).translate([x1, y1, 0])
    for (x, y, _) in BUTTONS.values():
        s = s - cbox(x, y, CAP[0] + 2 * CAP_GAP, CAP[1] + 2 * CAP_GAP, -1, SURROUND_T + 1)
    return s.translate([-x1, -y1, 0])


def lcd_bezel():
    """Black frame around each window (print 2 in black)."""
    bx, by = BEZEL
    wx, wy = WINDOW
    return box(bx, by, 1.2).translate([-bx / 2, -by / 2, 0]) - box(wx, wy, 3).translate([-wx / 2, -wy / 2, -1])


def dzus_head():
    return cyl(1.8, 4.3, 4.1) - box(8.6, 1.2, 1.0).translate([-4.3, -0.6, 1.0])


def offside_light():
    """The green OFFSIDE TUNING light (look only). Print in green, or paint the dome."""
    return cyl(1.2, 4.6) + cyl(1.6, 3.0, 2.6).translate([0, 0, 1.2])


def hf_sens_knob():
    """Small bar knob (look only). Glues flat onto the button plate."""
    k = cyl(5.0, 6.0, 5.6) + box(3.2, 11.0, 4.0).translate([-1.6, -5.5, 5.0])
    return k - box(0.8, 4.5, 0.8).translate([-0.4, 0.8, 8.6])     # pointer line (fill with black marker)


# ---------------- button caps ----------------
def cap(face, tip_z, stem=True, stem_dx=0.0, stem_w=4.0):
    """Printed face-down. Front face at z=0 of the print; the stem points up."""
    fx, fy = face
    front = (PLATE_T + SURROUND_T + 2.3) if face == CAP else (PLATE_T + 2.0)   # how far the face is above the back of the faceplate
    flange = (min(fx + 1.7, 18.4), min(fy + 1.7, 12.8)) if face == CAP else (fx + 2.4, fy + 2.4)
    c = rbox(fx, fy, front, 0.8).translate([-fx / 2, -fy / 2, 0])                 # face + body (z 0..front)
    c = c + rbox(flange[0], flange[1], 1.2, 1.0).translate([-flange[0] / 2, -flange[1] / 2, front])
    if face == TFR_CAP:   # key tab (matches the notch in the faceplate)
        c = c + box(1.6, 1.4, PLATE_T - 0.2).translate([3 - 0.8, fy / 2 - 0.4, front - PLATE_T + 0.2])
    if stem:
        c = c + box(stem_w, stem_w, -tip_z - 1.2).translate([stem_dx - stem_w / 2, -stem_w / 2, front + 1.2])
    return c


def vhf_backer():
    """Bar behind the three VHF buttons. Stick each KY-004 to its pad with foam tape."""
    x0, x1 = VHF_POSTS[0][0], VHF_POSTS[1][0]
    b = rbox(x1 - x0 + 6, 6.0, 2.5, 1.5).translate([x0 - 3, -3, 0])
    for name in ("VHF L", "VHF C", "VHF R"):
        x = BUTTONS[name][0]
        b = b + rbox(10, 10, 2.5, 1.5).translate([x - 5, -5, 0])
        b = b - box(6.0, 0.6, 0.4).translate([x - 3, -0.3, -0.01]) - box(0.6, 6.0, 0.4).translate([x - 0.3, -3, -0.01])   # cross = switch centre
    for post in VHF_POSTS:
        b = b - at(cyl(5, 1.15), (post[0], 0), -1)
    return b


def tfr_backer():
    """Arm from the post above the transfer button down to a pad behind its switch."""
    px, py = TFR_POST
    px -= TFR[0] + TFR_STEM_DX
    ln = py - TFR[1] + 5
    b = rbox(6.0, ln + 3, 2.5, 1.5).translate([-3, -5, 0]) + rbox(10, 10, 2.5, 1.5).translate([-5, -5, 0])
    b = b - box(6.0, 0.6, 0.4).translate([-3, -0.3, -0.01]) - box(0.6, 6.0, 0.4).translate([-0.3, -3, -0.01])
    b = b + rbox(8, 8, 2.5, 1.5).translate([px - 4, py - TFR[1] - 4, 0])
    return b - at(cyl(5, 1.15), (px, py - TFR[1]), -1)


def oled_clamp():
    """Holds a screen against the back of the faceplate (print 2). The gap clears the pins."""
    w = 2 * CLAMP_DX + 6
    c = rbox(w, 14, 2.0, 2.0).translate([-w / 2, -7, 0])
    c = c - box(OLED_PCB[0] - 10, 8, 4).translate([-(OLED_PCB[0] - 10) / 2 + 3, -4, -1])   # parts on the back of the screen
    c = c - box(7.0, 11, 4).translate([-OLED_PCB[0] / 2 - OLED_OFFSET - 1.5, -5.5, -1])       # header pins
    for sx in (-1, 1):
        c = c - at(cyl(4, 1.15), (sx * CLAMP_DX, 0), -1)
    return c


# ---------------- box ----------------
def back_box():
    b = box(W, H, BOX_DEPTH)
    b = b - box(W - 2 * WALL, H - WALL - WALL_TOP, BOX_DEPTH).translate([WALL, WALL, WALL])
    for c in CORNERS:
        b = b + at(cyl(BOX_DEPTH - WALL, 3.0), c, WALL)
        b = b - at(cyl(BOX_DEPTH, BOSS_HOLE / 2), c, BOX_DEPTH - 12)
    ux, uy = USB_SLOT
    b = b - box(ux, uy, WALL + 2).translate([W / 2 - ux / 2, WALL + 6, -1])
    for i in range(7):
        b = b - box(3.0, 26.0, WALL + 2).translate([28 + i * 14, H - WALL - 34, -1])
    return b


# ---------------- tuning knob ----------------
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


def tuning_knob(d_shaft):
    # 777 RTP knob: wide knurled outer ring (MHz on the real one) with a taller inner knob (kHz)
    outer = knurl(cyl(6.0, 10.2, 9.9), 10.2, 6.0, 48)
    inner = knurl(cyl(7.0, 6.8, 6.5).translate([0, 0, 6.0]), 6.8, 7.0, 34, z0=6.0)
    k = outer + inner
    return k - shaft_hole(SHAFT_DEPTH, d_shaft).translate([0, 0, -0.01])


# ---------------- fit check ----------------
def fit_check():
    """Solid models of the parts behind the panel. z = 0 is the back of the faceplate, negative = into the box."""
    parts = {}
    # encoder: body at the shaft, board and plug rotated toward ENC_ANGLE
    kx, ky = KNOB
    parts["knob encoder"] = cbox(kx, ky, 12.5, 12.5, -6.6, 0)
    a = ENC_ANGLE
    board = cbox(6.5, 0, 26.0, 19.0, -8.2, -6.6).translate([-13.0, 0, 0])   # pins end at -19.5
    board = box(26.0, 19.0, 1.6).translate([-19.5, -9.5, -8.2])
    plug = box(20.0, 13.0, 3.0).translate([-39.5, -6.5, -8.9])            # pins + dupont plugs
    parts["knob board"] = board.rotate([0, 0, a - 180]).translate([kx, ky, 0])
    parts["knob wires"] = plug.rotate([0, 0, a - 180]).translate([kx, ky, 0])
    # screens
    for name, win in (("active", ACTIVE), ("standby", STANDBY)):
        cx, cy = oled_center(win)
        px, py = OLED_PCB
        parts[name + " screen"] = cbox(cx, cy, px + 2 * OLED_SLOP, py, -OLED_STACK, 0)
        parts[name + " clamp"] = cbox(win[0], cy, 2 * CLAMP_DX + 6, 14, -OLED_STACK - 2, -OLED_STACK)
        pin_x = oled_pin_x(win)
        parts[name + " wires"] = cbox(pin_x, cy, 3.2, 10.5, -30, -OLED_STACK)
    # button modules, pins up (in line with the board), plugs going up.
    # A plug reaches about 18 mm past the board edge (header spacer + 14 mm plug + wire bend).
    def module(name, x, y, tip, horizontal=False):
        z_front = tip - SWITCH_H
        if not horizontal:
            parts[name + " switch"] = cbox(x, y, 6.2, 6.2, z_front, tip)
            y0 = y - KY004_SW
            parts[name + " board"] = box(KY004[0], KY004[1], KY004[2]).translate([x - KY004[0] / 2, y0, z_front - KY004[2]])
            parts[name + " wires"] = box(8.0, 18.0, 2.6).translate([x - 4, y0 + KY004[1], z_front - KY004[2] / 2 - 1.3])
        else:   # transfer button: pins point left
            parts[name + " switch"] = cbox(x, y, 6.2, 6.2, z_front, tip)
            x0 = x + KY004_SW
            parts[name + " board"] = box(KY004[1], KY004[0], KY004[2]).translate([x0 - KY004[1], y - KY004[0] / 2, z_front - KY004[2]])
            parts[name + " wires"] = box(18.0, 8.0, 2.6).translate([x0 - KY004[1] - 18, y - 4, z_front - KY004[2] / 2 - 1.3])
    for name in ("VHF L", "VHF C", "VHF R"):
        x, y, _ = BUTTONS[name]
        module(name, x, y, VHF_TIP)
        parts[name + " stem"] = cbox(x, y, 4, 4, VHF_TIP, -1.2)
    module("TFR", TFR[0] + TFR_STEM_DX, TFR[1], TFR_TIP, horizontal=True)
    parts["TFR stem"] = cbox(TFR[0] + TFR_STEM_DX, TFR[1], TFR_STEM, TFR_STEM, TFR_TIP, -1.2)
    for name, (x, y, _) in BUTTONS.items():
        fl = (min(CAP[0] + 1.7, 18.4), min(CAP[1] + 1.7, 12.8))
        parts[name + " cap flange"] = cbox(x, y, fl[0], fl[1], -1.2, 0)
    parts["TFR cap flange"] = cbox(TFR[0], TFR[1], TFR_CAP[0] + 2.4, TFR_CAP[1] + 2.4, -1.2, 0)
    # backers
    vz = vhf_backer_z()
    parts["VHF backer"] = vhf_backer().translate([0, VHF_POSTS[0][1], vz - 2.5])
    parts["TFR backer"] = tfr_backer().translate([TFR[0] + TFR_STEM_DX, TFR[1], tfr_backer_z() - 2.5])
    for i, post in enumerate(VHF_POSTS):
        parts[f"VHF post {i + 1}"] = cbox(post[0], post[1], 5, 5, vz, 0)
    parts["TFR post"] = cbox(TFR_POST[0], TFR_POST[1], 5, 5, tfr_backer_z(), 0)
    for i, c in enumerate(CORNERS):
        parts[f"corner post {i + 1}"] = cbox(c[0], c[1], 6, 6, -BOX_DEPTH, 0)

    # things that are meant to touch
    ok_pairs = set()
    def same(a, b, *names):
        return any(a.startswith(n) and b.startswith(n) for n in names)
    inside = Manifold.cube([W - 2 * WALL, H - WALL - WALL_TOP, BOX_DEPTH]).translate([WALL, WALL, -BOX_DEPTH])
    problems = []
    names = list(parts)
    for n in names:
        if n.startswith("corner"):
            continue
        out = parts[n] - inside
        if out.volume() > 0.01:
            problems.append(f"{n} touches the box wall")
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if same(a, b, "knob", "active", "standby", "VHF L", "VHF C", "VHF R", "TFR", "corner"):
                continue
            if {a, b} & {"VHF backer"} and ("post" in a + b or "board" in a + b):
                continue     # backer screws to its posts, and the boards are taped to it
            if {a, b} & {"TFR backer"} and (("TFR" in a and "TFR" in b) or "TFR post" in (a, b)):
                continue
            v = (parts[a] ^ parts[b]).volume()
            if v > 0.01:
                problems.append(f"{a} hits {b} ({v:.1f} mm3)")
    print("fit check:", "everything fits" if not problems else "\n  " + "\n  ".join(problems))
    return problems, parts


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".stl"):
            os.remove(os.path.join(OUT, f))
    fit_check()
    fp = faceplate()
    save(fp.rotate([180, 0, 0]).translate([0, H, PLATE_T]), "faceplate")      # print face-down
    save(surround(), "button_plate")
    save(lcd_bezel(), "lcd_bezel")
    save(dzus_head(), "dzus_head")
    save(offside_light(), "offside_light")
    save(hf_sens_knob(), "hf_sens_knob")
    save(cap(CAP, VHF_TIP), "button_cap")
    save(cap(CAP, VHF_TIP, stem=False), "button_cap_dummy")
    save(cap(TFR_CAP, TFR_TIP, stem_dx=-TFR_STEM_DX, stem_w=TFR_STEM), "transfer_cap")   # printed face-down, so left/right flip
    save(vhf_backer(), "vhf_backer")
    save(tfr_backer(), "transfer_backer")
    save(oled_clamp(), "screen_clamp")
    save(back_box(), "back_box")
    for d, tag in ((True, "Dshaft"), (False, "knurled")):
        save(tuning_knob(d), f"tuning_knob_{tag}")
