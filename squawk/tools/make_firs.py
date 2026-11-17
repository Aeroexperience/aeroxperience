"""Build data/firs.json (FIR / center boundaries and names) from the VATSpy Data Project.

Source: https://github.com/vatsimnetwork/vatspy-data-project (Boundaries.geojson + VATSpy.dat),
licensed CC BY-SA 4.0. The output file is a simplified copy and keeps that licence.
Run:  python3 make_firs.py /path/to/vatspy-data-project
"""
import json, sys, os
from shapely.geometry import shape, mapping

src = sys.argv[1]
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "firs.json")
g = json.load(open(os.path.join(src, "Boundaries.geojson")))

names = {}
sec = None
for line in open(os.path.join(src, "VATSpy.dat"), encoding="utf-8", errors="ignore"):
    line = line.strip()
    if line.startswith("["):
        sec = line
        continue
    if sec != "[FIRs]" or not line or line.startswith(";"):
        continue
    p = line.split("|")
    if len(p) >= 4:
        names.setdefault(p[3], p[1])

ENDS = ("Control", "Radar", "Center", "Centre", "Oceanic", "Radio", "Information")


OCEANIC_IDS = {"EGGX", "CZQO", "LPPO", "KZWY", "KZAK", "NZZO", "TTZO", "SBAO", "GVSC", "BGGL", "ENOB", "RJJJ", "YBBB"}


def nice(fid, oceanic):
    n = names.get(fid, fid)
    if fid == "LPPO":
        n = "Santa Maria Oceanic"
    n = n.split(" ACC")[0].split(" - ")[0].replace(" FIR", "").strip()
    if oceanic:
        return n if "Oceanic" in n else n + " Oceanic"
    if n.endswith(ENDS):
        return n
    us = fid[0] in "KP" and len(fid) == 4 and fid[1] == "Z" or fid.startswith("CZ")
    return n + (" Center" if us else " Control")


feats = []
for f in g["features"]:
    pr = f["properties"]
    fid = pr["id"]
    if "-" in fid or fid == "NAT" or "TMA" in names.get(fid, "") or "(Up to" in names.get(fid, ""):
        continue   # sub-sectors, terminal areas and the combined NAT shape overlap the real FIRs
    oc = pr.get("oceanic") == "1" or fid in OCEANIC_IDS or "Oceanic" in names.get(fid, "")
    geom = shape(f["geometry"]).simplify(0.03, preserve_topology=True)
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    rings = []
    for pl in polys:
        rings.append([[round(x, 2), round(y, 2)] for x, y in pl.exterior.coords])
    b = [round(v, 2) for v in geom.bounds]
    lab = [round(float(pr.get("label_lon", 0)), 2), round(float(pr.get("label_lat", 0)), 2)]
    # where FIRs overlap (altitude splits), Squawk picks the one whose label point is closest
    feats.append({"i": fid, "n": nice(fid, oc), "o": 1 if oc else 0, "b": b, "a": round(geom.area, 1), "l": lab, "p": rings})

os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump({"src": "VATSpy Data Project, CC BY-SA 4.0", "f": feats}, open(out, "w"), separators=(",", ":"))
print(len(feats), "FIRs,", os.path.getsize(out) // 1024, "KB")
