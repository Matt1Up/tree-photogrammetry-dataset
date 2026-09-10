#!/usr/bin/env python3
"""Build manifest/images.csv and manifest/checksums.sha256 from an image directory.

Usage:  scripts/make-manifest.py <images_dir> [repo_root]

Columns: filename, group, bytes, sha256, width, height, datetime, lat, lon, alt_m, gps_valid
'gps_valid' is false for null-island (0,0) fixes and for missing coordinates.
"""
import csv, hashlib, json, os, re, subprocess, sys

img_dir = os.path.abspath(sys.argv[1])
root = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(root, "manifest")
os.makedirs(out, exist_ok=True)

files = sorted(f for f in os.listdir(img_dir) if f.lower().endswith(".jpg"))
if not files:
    sys.exit(f"no .jpg found in {img_dir}")
print(f"{len(files)} images in {img_dir}")

print("reading EXIF ...")
meta = {}
proc = subprocess.run(
    ["exiftool", "-q", "-q", "-m", "-n", "-json",
     "-FileName", "-ImageWidth", "-ImageHeight", "-DateTimeOriginal",
     "-GPSLatitude", "-GPSLongitude", "-GPSAltitude",
     "-GPSLatitudeRef", "-GPSLongitudeRef", img_dir],
    capture_output=True, text=True)
for r in json.loads(proc.stdout or "[]"):
    meta[r.get("FileName", "")] = r

def signed(val, ref, negative_ref):
    """exiftool -n returns an UNSIGNED magnitude; the hemisphere lives in a separate Ref tag.
    Without this, every western longitude comes out positive -- Chicago lands in Kazakhstan."""
    if val in (None, ""):
        return ""
    v = abs(float(val))
    if str(ref).strip().upper().startswith(negative_ref):
        v = -v
    return v


def group_of(name):
    m = re.match(r"^(.*)-\d+\.jpg$", name, re.I)
    return m.group(1) if m else name.rsplit(".", 1)[0]

rows, sums = [], []
for i, name in enumerate(files, 1):
    path = os.path.join(img_dir, name)
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    digest = h.hexdigest()
    m = meta.get(name, {})
    lat, lon = signed(m.get("GPSLatitude"), m.get("GPSLatitudeRef"), "S"), \
               signed(m.get("GPSLongitude"), m.get("GPSLongitudeRef"), "W")
    valid = lat not in (None, "") and lon not in (None, "") \
            and float(lat) != 0.0 and float(lon) != 0.0
    rows.append({
        "filename": name, "group": group_of(name),
        "bytes": os.path.getsize(path), "sha256": digest,
        "width": m.get("ImageWidth", ""), "height": m.get("ImageHeight", ""),
        "datetime": m.get("DateTimeOriginal", ""),
        "lat": lat if lat is not None else "", "lon": lon if lon is not None else "",
        "alt_m": m.get("GPSAltitude", ""), "gps_valid": "true" if valid else "false",
    })
    sums.append(f"{digest}  images/{name}")
    if i % 250 == 0 or i == len(files):
        print(f"  hashed {i}/{len(files)}")

cols = ["filename","group","bytes","sha256","width","height","datetime","lat","lon","alt_m","gps_valid"]
with open(os.path.join(out, "images.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
with open(os.path.join(out, "checksums.sha256"), "w") as fh:
    fh.write("\n".join(sums) + "\n")

nbad = sum(1 for r in rows if r["gps_valid"] == "false")
total = sum(r["bytes"] for r in rows)
groups = {}
for r in rows:
    groups[r["group"]] = groups.get(r["group"], 0) + 1
summary = {
    "images": len(rows), "bytes": total, "gib": round(total / 2**30, 2),
    "gps_invalid": nbad,
    "groups": dict(sorted(groups.items(), key=lambda kv: -kv[1])),
}
with open(os.path.join(out, "summary.json"), "w") as fh:
    json.dump(summary, fh, indent=2)
print(json.dumps(summary, indent=2))
