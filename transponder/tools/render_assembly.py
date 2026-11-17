"""Render a front view of the assembled panel (../docs/assembly_preview.png)."""
import importlib.util, os, numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mp", os.path.join(here, "make_parts.py")); mp = importlib.util.module_from_spec(spec); spec.loader.exec_module(mp)
def tm(m):
    me = m.to_mesh(); return trimesh.Trimesh(np.asarray(me.vert_properties)[:, :3], np.asarray(me.tri_verts), process=False)
BROWN, BEIGE, BLACK, CREAM = "#8b7b55", "#e9e2c6", "#1a1a1a", "#f4f1e6"
items = [(tm(mp.faceplate()), BROWN)]
for d in mp.DZUS: items.append((tm(mp.dzus_head().translate([d[0], d[1], mp.PLATE_T - 0.4])), BROWN))
items.append((tm(mp.display_bezel().translate([mp.DISPLAY[0], mp.DISPLAY[1], mp.PLATE_T])), BLACK))
z0 = mp.PLATE_T + 1.6   # knobs sit a little above the panel (nut + washer)
for e in (mp.CODE_L, mp.CODE_R): items.append((tm(mp.code_knob(True).translate([e[0], e[1], z0])), BEIGE))
items.append((tm(mp.mode_knob(True).translate([mp.MODE[0], mp.MODE[1], z0])), BEIGE))
items.append((tm(mp.ident_cap().translate([mp.MODE[0], mp.MODE[1], z0 + 8.5])), CREAM))
angles = {"abv_n_blw_left": 200, "abs_rel_left": 105, "abv_n_blw_right": 20, "abs_rel_right": 100, "alt_source": 100, "xpndr_l_r": 110}
for nm, xy in mp.SELECTORS.items():
    k = mp.selector_knob().rotate([0, 0, angles[nm] - 90]).translate([xy[0], xy[1], mp.PLATE_T + 0.5])
    items.append((tm(k), BEIGE))
fig = plt.figure(figsize=(14, 6)); ax = fig.add_subplot(111, projection="3d")
light = np.array([0.25, 0.35, 0.9]); light /= np.linalg.norm(light)
for t, col in items:
    rgb = np.array(matplotlib.colors.to_rgb(col))
    sh = np.clip(t.face_normals @ light, 0.25, 1.0)[:, None]
    ax.add_collection3d(Poly3DCollection(t.vertices[t.faces], facecolors=np.clip(rgb * (0.55 + 0.45 * sh), 0, 1), edgecolor="none"))
# screen
win = mp.WINDOW
ax.add_collection3d(Poly3DCollection([[(mp.DISPLAY[0]-win[0]/2, mp.DISPLAY[1]-win[1]/2, mp.PLATE_T+0.05),(mp.DISPLAY[0]+win[0]/2, mp.DISPLAY[1]-win[1]/2, mp.PLATE_T+0.05),(mp.DISPLAY[0]+win[0]/2, mp.DISPLAY[1]+win[1]/2, mp.PLATE_T+0.05),(mp.DISPLAY[0]-win[0]/2, mp.DISPLAY[1]+win[1]/2, mp.PLATE_T+0.05)]], facecolors="#111111"))
ax.set_xlim(0, mp.W); ax.set_ylim(-44.45, 101.25); ax.set_zlim(-60, 85)
ax.view_init(elev=90, azim=-90); ax.set_proj_type("ortho"); ax.set_axis_off()
plt.subplots_adjust(0, 0, 1, 1)
out = os.path.join(here, "..", "docs", "assembly_preview.png"); plt.savefig(out, dpi=110, facecolor="white")
print("wrote", out)
