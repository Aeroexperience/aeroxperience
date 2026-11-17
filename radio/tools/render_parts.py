"""Render ../docs/parts_preview.png (every printed part) and ../docs/back_view.png
(the back of the faceplate with the screens, knob, buttons and wires in place)."""
import importlib.util, os, numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mp", os.path.join(here, "make_parts.py")); mp = importlib.util.module_from_spec(spec); spec.loader.exec_module(mp)
LIGHT = np.array([0.3, 0.4, 0.85]); LIGHT /= np.linalg.norm(LIGHT)


def tm(m):
    me = m.to_mesh(); return trimesh.Trimesh(np.asarray(me.vert_properties)[:, :3], np.asarray(me.tri_verts), process=False)


def draw(ax, t, col, alpha=1.0):
    rgb = np.array(matplotlib.colors.to_rgb(col))
    sh = np.clip(t.face_normals @ LIGHT, 0.2, 1.0)[:, None]
    ax.add_collection3d(Poly3DCollection(t.vertices[t.faces], facecolors=np.clip(rgb * (0.5 + 0.5 * sh), 0, 1),
                                         edgecolor="none", alpha=alpha))


def fit(ax, t, pad=1.0):
    lo, hi = t.bounds; c = (lo + hi) / 2; r = max(hi - lo) / 2 * pad
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1)); ax.set_axis_off()


BROWN, BEIGE, BLACK, GREEN = "#8b7b55", "#e9e2c6", "#2a2a2a", "#2fb34a"
parts = [
    ("faceplate (back)", tm(mp.faceplate()), BROWN, (-60, -100)),
    ("back_box", tm(mp.back_box()), BROWN, (25, -60)),
    ("button_plate", tm(mp.surround()), BROWN, (40, -70)),
    ("lcd_bezel x2", tm(mp.lcd_bezel()), BLACK, (40, -70)),
    ("button_cap x3", tm(mp.cap(mp.CAP, mp.VHF_TIP)), BLACK, (25, -60)),
    ("button_cap_dummy x4", tm(mp.cap(mp.CAP, mp.VHF_TIP, stem=False)), BLACK, (25, -60)),
    ("transfer_cap", tm(mp.cap(mp.TFR_CAP, mp.TFR_TIP, stem_dx=-mp.TFR_STEM_DX, stem_w=mp.TFR_STEM)), BLACK, (25, -60)),
    ("vhf_backer", tm(mp.vhf_backer()), BROWN, (40, -70)),
    ("transfer_backer", tm(mp.tfr_backer()), BROWN, (40, -70)),
    ("screen_clamp x2", tm(mp.oled_clamp()), BROWN, (40, -70)),
    ("tuning_knob", tm(mp.tuning_knob(True)), BEIGE, (35, -60)),
    ("hf_sens_knob", tm(mp.hf_sens_knob()), BEIGE, (35, -60)),
    ("dzus_head x4", tm(mp.dzus_head()), BROWN, (35, -60)),
    ("offside_light", tm(mp.offside_light()), GREEN, (35, -60)),
]
fig = plt.figure(figsize=(16, 13))
for i, (name, t, col, view) in enumerate(parts):
    ax = fig.add_subplot(4, 4, i + 1, projection="3d")
    draw(ax, t, col); fit(ax, t); ax.view_init(elev=view[0], azim=view[1])
    ax.set_title(name, fontsize=13)
plt.tight_layout()
out = os.path.join(here, "..", "docs", "parts_preview.png"); plt.savefig(out, dpi=80, facecolor="white"); plt.close()
print("wrote", out)

# back view: looking at the back of the faceplate (so left and right are swapped), electronics in colour
from matplotlib.collections import PolyCollection
_, solids = mp.fit_check()
fig, ax = plt.subplots(figsize=(15, 7.6))
def flat(t, col, alpha=1.0, z=0):
    tri = t.vertices[t.faces][:, :, :2].copy(); tri[:, :, 0] = mp.W - tri[:, :, 0]
    ax.add_collection(PolyCollection(tri, facecolors=col, edgecolors=col, linewidths=0.2, alpha=alpha, zorder=z))
flat(tm(mp.faceplate()), "#8b7b55", z=0)
for win in (mp.ACTIVE, mp.STANDBY):
    ax.add_patch(plt.Rectangle((mp.W - win[0] - mp.WINDOW[0] / 2, win[1] - mp.WINDOW[1] / 2), *mp.WINDOW, color="white", zorder=0.5))
COLS = [("wires", "#e0574f"), ("screen", "#3b6fd1"), ("clamp", "#d9c99f"), ("board", "#2d8a4e"), ("switch", "#333333"),
        ("encoder", "#777777"), ("stem", "#111111"), ("backer", "#e8d9a8"), ("post", "#6b5d3e"), ("flange", "#1b1b1b")]
order = sorted((n for n in solids if not n.startswith("corner")), key=lambda n: -solids[n].bounding_box()[2])
for k, n in enumerate(order):
    col = next((c for key, c in COLS if key in n), "#999999")
    flat(tm(solids[n]), col, 0.92, z=1 + k)
labels = {"ACTIVE screen\n(pins left)": mp.ACTIVE, "STANDBY screen\n(upside down)": mp.STANDBY, "tuning knob\n(pins down-left)": mp.KNOB,
          "VHF L": mp.BUTTONS["VHF L"][:2], "VHF C": mp.BUTTONS["VHF C"][:2], "VHF R": mp.BUTTONS["VHF R"][:2], "TFR": (mp.TFR[0], mp.TFR[1] + 6)}
for txt, (x, y) in labels.items():
    ax.text(mp.W - x, y - 9 if "VHF" in txt else y + 8, txt, ha="center", va="center", fontsize=10, zorder=500,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#555", alpha=0.85))
ax.set_xlim(-2, mp.W + 2); ax.set_ylim(-2, mp.H + 2); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Back of the faceplate (as you see it while wiring). Red = wire plugs, green = boards, blue = screens", fontsize=12)
plt.tight_layout()
out = os.path.join(here, "..", "docs", "back_view.png"); plt.savefig(out, dpi=110, facecolor="white")
print("wrote", out)
