# Camera poses

807 solved cameras with intrinsics and extrinsics, plus a sparse tie-point cloud. Same thing
COLMAP would give you, so you can skip that step.

Solved in RealityScan 2.2, which is free.

## Contents

| | |
|---|---|
| `xmp/` | 807 XMP files, one per aligned image, named to match `images/` |
| `cameras.csv` | the same data as one table |
| `unaligned.txt` | the 5 images that didn't solve |
| `tiepoints.ply` | 1,206,765 tie points with RGB — hosted with the images, not here (77 MB) |

## XMP format

```xml
<rdf:Description xcr:Version="4" xcr:Coordinates="absolute"
   xcr:DistortionModel="perspective" xcr:DistortionCoeficients="0 0 0 0 0 0"
   xcr:FocalLength35mm="26.34" xcr:PrincipalPointU="0" xcr:PrincipalPointV="0">
  <xcr:Rotation>r0 r1 r2 r3 r4 r5 r6 r7 r8</xcr:Rotation>
  <xcr:Position>x y z</xcr:Position>
</rdf:Description>
```

- `Rotation` — 3×3 matrix, row-major, world→camera
- `Position` — camera centre in world coordinates
- `FocalLength35mm` — multiply by `width / 36` for pixels
- **Coordinates are a local frame of unverified scale** — not lat/lon, and not confirmed to be
  metres. The whole capture spans about 17 m of GPS footprint, which is too small to calibrate
  scale against consumer GPS carrying several metres of error per fix. If you need real-world
  units, measure something in the scene. For splatting or novel-view work the scale does not
  matter

`cameras.csv` has the same fields as columns: `R0`–`R8`, `X`/`Y`/`Z`, `focal_35mm`,
`principal_u`/`principal_v`, `distortion_model`, `distortion_coeffs`, `width`, `height`.

## Gaussian splatting

**Already converted** — [`colmap/`](colmap/) has `cameras.txt`, `images.txt` and
`points3D.txt`, which is what 3DGS implementations read. Grab `points3D.txt` with
`./scripts/download.sh --colmap` and point your pipeline at it.

Downsample the images to ~1600 px wide before training. Nothing trains at 5464 px, and the
originals are here so you can pick your own resolution.

If you want to redo the conversion yourself,
[`../scripts/xmp-to-colmap.py`](../scripts/xmp-to-colmap.py) does it and prints its own
verification.

## The 5 that didn't align

```
Original_low-22.jpg   Original_low-24.jpg   Original_low-25.jpg
Original_low-27.jpg   Original_mid-23.jpg
```

All from the low and mid tiers, none from `The_Tree`. Those are the knee- and chest-height
frames angled upward, where there's less overlap and the trunk blocks a lot of the view.
