#!/usr/bin/env python3
"""Build a representative sample pack from the full image set.

Usage:  scripts/make-sample.py <images_dir> <out_dir> [target_mb]

Picks images evenly spaced across every capture group, proportional to group size, so the
sample shows the real range of the dataset rather than a random clump. Files are copied at
FULL resolution -- the point of a sample is to show true image quality.
"""
import csv, os, shutil, sys

img_dir = os.path.abspath(sys.argv[1])
out_dir = os.path.abspath(sys.argv[2])
target = int(sys.argv[3]) if len(sys.argv) > 3 else 500
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(root, "manifest", "images.csv")) as fh:
    rows = list(csv.DictReader(fh))
if not rows:
    sys.exit("manifest/images.csv is empty -- run make-manifest.py first")

groups = {}
for r in rows:
    groups.setdefault(r["group"], []).append(r)

avg = sum(int(r["bytes"]) for r in rows) / len(rows)
n_total = max(1, int(target * 1024 * 1024 / avg))
print(f"{len(rows)} images, avg {avg/2**20:.1f} MB -> sampling ~{n_total} for ~{target} MB")

picked = []
for g, items in sorted(groups.items(), key=lambda kv: -len(kv[1])):
    items.sort(key=lambda r: r["filename"])
    share = max(1, round(n_total * len(items) / len(rows)))
    step = max(1, len(items) // share)
    sel = items[::step][:share]
    picked.extend(sel)
    print(f"  {g:<26} {len(sel):>3} of {len(items)}")

os.makedirs(out_dir, exist_ok=True)
total = 0
for r in picked:
    src = os.path.join(img_dir, r["filename"])
    shutil.copy2(src, os.path.join(out_dir, r["filename"]))
    total += int(r["bytes"])

with open(os.path.join(out_dir, "README.txt"), "w") as fh:
    fh.write(
        "SAMPLE PACK\n\n"
        f"{len(picked)} of {len(rows)} images, spread evenly across all capture groups.\n"
        "Full resolution, original files, metadata intact -- identical to what you get in the\n"
        "full download. This pack exists so you can judge quality and overlap before\n"
        "committing to the complete set.\n\n"
        "Full dataset, checksums and documentation:\n"
        "https://github.com/Matt1Up/\n"
    )
print(f"\n{len(picked)} images, {total/2**20:.0f} MB -> {out_dir}")
