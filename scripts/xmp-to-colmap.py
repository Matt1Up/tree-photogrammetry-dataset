#!/usr/bin/env python3
"""Convert RealityScan XMP camera poses to COLMAP sparse text format.

Usage: scripts/xmp-to-colmap.py <xmp_dir> <images_dir> <tiepoints.ply> <out_dir>

Writes cameras.txt, images.txt, points3D.txt -- what 3DGS / NeRF pipelines read.

The camera-frame convention is NOT assumed. Both candidate conventions are tested by
reprojecting the tie points through the derived matrices; the one that actually puts points
in front of the cameras and inside the frame wins, and the result is printed.
"""
import os, re, sys, glob, math
import numpy as np

xmp_dir, img_dir, ply_path, out_dir = sys.argv[1:5]
os.makedirs(out_dir, exist_ok=True)

# RealityScan writes Rotation and Position EITHER as child elements OR as attributes on
# rdf:Description, and mixes both styles within a single export. Matching only the element
# form silently drops whichever cameras used the attribute form -- 70 of 807 here.
RX = {k: re.compile(p) for k, p in {
    "f35": r'xcr:FocalLength35mm="([^"]+)"',
    "ppu": r'xcr:PrincipalPointU="([^"]+)"',
    "ppv": r'xcr:PrincipalPointV="([^"]+)"',
}.items()}
_ELEM = {k: re.compile(rf'<xcr:{k}>([^<]+)</xcr:{k}>') for k in ("Rotation", "Position")}
_ATTR = {k: re.compile(rf'xcr:{k}="([^"]+)"') for k in ("Rotation", "Position")}

def vec(text, key):
    m = _ELEM[key].search(text) or _ATTR[key].search(text)
    return [float(x) for x in m.group(1).split()] if m else None

def img_size(name):
    from PIL import Image
    with Image.open(os.path.join(img_dir, name)) as im:
        return im.size

cams, skipped = [], []
for p in sorted(glob.glob(os.path.join(xmp_dir, "*.xmp"))):
    t = open(p).read()
    g = {k: RX[k].search(t) for k in RX}
    rv, pv = vec(t, "Rotation"), vec(t, "Position")
    if rv is None or pv is None:
        skipped.append(os.path.basename(p)); continue
    base = os.path.basename(p)[:-4]
    R = np.array(rv).reshape(3, 3)
    C = np.array(pv)
    cams.append(dict(name=base + ".jpg", R=R, C=C,
                     f35=float(g["f35"].group(1)) if g["f35"] else None,
                     ppu=float(g["ppu"].group(1)) if g["ppu"] else 0.0,
                     ppv=float(g["ppv"].group(1)) if g["ppv"] else 0.0))
print(f"parsed {len(cams)} XMP cameras")
if skipped:
    print(f"  WARNING: {len(skipped)} XMP files had no usable pose: {skipped[:5]}")

W, H = img_size(cams[0]["name"])
LARGE = max(W, H)
print(f"image size {W}x{H}")

# --- tie points ---
xyz, rgb = [], []
with open(ply_path, "rb") as fh:
    hdr, n = [], 0
    while True:
        line = fh.readline().decode("ascii", "replace")
        hdr.append(line.strip())
        if line.startswith("element vertex"): n = int(line.split()[-1])
        if line.strip() == "end_header": break
    for _ in range(n):
        parts = fh.readline().split()
        xyz.append([float(parts[0]), float(parts[1]), float(parts[2])])
        rgb.append([int(parts[3]), int(parts[4]), int(parts[5])])
xyz = np.array(xyz); rgb = np.array(rgb, dtype=int)
print(f"tie points: {len(xyz):,}")

# --- candidate conventions ---
FLIP = np.diag([1.0, -1.0, -1.0])   # y/z flip between +Y-up and +Y-down camera frames
CONVENTIONS = {"direct": np.eye(3), "yz_flip": FLIP}

def score(M):
    """fraction of tie points landing in front of the camera and inside the frame"""
    sub = xyz[:: max(1, len(xyz)//20000)]
    tot = inside = 0
    for c in cams[:: max(1, len(cams)//60)]:
        f = c["f35"] * LARGE / 36.0
        cx = W/2.0 + c["ppu"]*LARGE
        cy = H/2.0 + c["ppv"]*LARGE
        Rc = M @ c["R"]
        t = -Rc @ c["C"]
        P = (Rc @ sub.T).T + t
        z = P[:, 2]
        ok = z > 1e-6
        u = np.full(len(P), -1e9); v = np.full(len(P), -1e9)
        u[ok] = f*P[ok, 0]/z[ok] + cx
        v[ok] = f*P[ok, 1]/z[ok] + cy
        inside += int(np.sum(ok & (u >= 0) & (u < W) & (v >= 0) & (v < H)))
        tot += len(sub)
    return inside/tot

print("\ntesting camera-frame conventions by reprojection:")
scores = {k: score(M) for k, M in CONVENTIONS.items()}
for k, s in scores.items():
    print(f"  {k:<9} {s*100:6.2f}% of sampled tie points land in-frame")
best = max(scores, key=scores.get)
M = CONVENTIONS[best]
print(f"  -> using '{best}'")
if scores[best] < 0.02:
    sys.exit("ABORT: neither convention reprojects sensibly; not writing output")

def quat(R):
    tr = np.trace(R)
    if tr > 0:
        S = math.sqrt(tr+1.0)*2; w = 0.25*S
        x = (R[2,1]-R[1,2])/S; y = (R[0,2]-R[2,0])/S; z = (R[1,0]-R[0,1])/S
    elif R[0,0] > R[1,1] and R[0,0] > R[2,2]:
        S = math.sqrt(1.0+R[0,0]-R[1,1]-R[2,2])*2
        w = (R[2,1]-R[1,2])/S; x = 0.25*S; y = (R[0,1]+R[1,0])/S; z = (R[0,2]+R[2,0])/S
    elif R[1,1] > R[2,2]:
        S = math.sqrt(1.0+R[1,1]-R[0,0]-R[2,2])*2
        w = (R[0,2]-R[2,0])/S; x = (R[0,1]+R[1,0])/S; y = 0.25*S; z = (R[1,2]+R[2,1])/S
    else:
        S = math.sqrt(1.0+R[2,2]-R[0,0]-R[1,1])*2
        w = (R[1,0]-R[0,1])/S; x = (R[0,2]+R[2,0])/S; y = (R[1,2]+R[2,1])/S; z = 0.25*S
    return w, x, y, z

with open(os.path.join(out_dir, "cameras.txt"), "w") as fc, \
     open(os.path.join(out_dir, "images.txt"), "w") as fi:
    fc.write("# Camera list with one line of data per camera:\n")
    fc.write("#   CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]\n")
    fi.write("# Image list with two lines of data per image:\n")
    fi.write("#   IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME\n#   POINTS2D[] as (X, Y, POINT3D_ID)\n")
    for i, c in enumerate(cams, 1):
        f = c["f35"] * LARGE / 36.0
        cx = W/2.0 + c["ppu"]*LARGE
        cy = H/2.0 + c["ppv"]*LARGE
        fc.write(f"{i} PINHOLE {W} {H} {f:.6f} {f:.6f} {cx:.6f} {cy:.6f}\n")
        Rc = M @ c["R"]; t = -Rc @ c["C"]
        qw, qx, qy, qz = quat(Rc)
        fi.write(f"{i} {qw:.9f} {qx:.9f} {qy:.9f} {qz:.9f} {t[0]:.9f} {t[1]:.9f} {t[2]:.9f} {i} {c['name']}\n\n")

with open(os.path.join(out_dir, "points3D.txt"), "w") as fp:
    fp.write("# 3D point list with one line of data per point:\n")
    fp.write("#   POINT3D_ID, X, Y, Z, R, G, B, ERROR, TRACK[] as (IMAGE_ID, POINT2D_IDX)\n")
    for i, (p, c) in enumerate(zip(xyz, rgb), 1):
        fp.write(f"{i} {p[0]:.6f} {p[1]:.6f} {p[2]:.6f} {c[0]} {c[1]} {c[2]} 0\n")

print(f"\nwrote {out_dir}/cameras.txt images.txt points3D.txt")
print(f"  {len(cams)} cameras, {len(xyz):,} points")
