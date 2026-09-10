# Camera poses — v1.1

A solved alignment of this dataset: **807 of 812 cameras**, with intrinsics, extrinsics and a
sparse tie-point cloud. Together these are the equivalent of a COLMAP sparse reconstruction,
which means you can **skip straight to training** instead of spending hours running structure
from motion before you can start.

Produced with **RealityScan 2.2** — the current free version — so this alignment is
reproducible by anyone, not locked to a licence or a 2020 build.

## Contents

| | |
|---|---|
| `xmp/` | 807 XMP sidecars, one per aligned image, named to match `images/` |
| `cameras.csv` | the same data flattened into one table |
| `unaligned.txt` | the 5 images that did not solve |
| `tiepoints.ply` | 1,206,765 sparse tie points with RGB — **hosted with the images, not here** (77 MB) |

## Format

Each XMP is RealityCapture's `xcr` namespace:

```xml
<rdf:Description xcr:Version="4" xcr:Coordinates="absolute"
   xcr:DistortionModel="perspective" xcr:DistortionCoeficients="0 0 0 0 0 0"
   xcr:FocalLength35mm="26.34" xcr:PrincipalPointU="0" xcr:PrincipalPointV="0">
  <xcr:Rotation>r0 r1 r2 r3 r4 r5 r6 r7 r8</xcr:Rotation>
  <xcr:Position>x y z</xcr:Position>
</rdf:Description>
```

- **`Rotation`** — 3×3 rotation matrix, row-major, world→camera
- **`Position`** — camera centre in world coordinates
- **`FocalLength35mm`** — 35mm-equivalent focal length. Multiply by `width / 36` for pixels
- **Coordinates are a local metric system in metres**, not lat/lon. The images themselves carry
  GPS in EXIF if you want to georeference

`cameras.csv` has the same fields as columns — `R0`–`R8`, `X`/`Y`/`Z`, `focal_35mm`,
`principal_u`/`principal_v`, `distortion_model`, `distortion_coeffs`, plus `width`/`height`.

## The five that didn't align

```
Original_low-22.jpg   Original_low-24.jpg   Original_low-25.jpg
Original_low-27.jpg   Original_mid-23.jpg
```

**All five are from the low and mid tiers. None from `The_Tree`.** That is not chance — those
are the knee- and chest-height hover frames angled upward, where overlap is thinnest and the
trunk and grass occlude much of the frame. If you are benchmarking a matcher, this is where it
will struggle, and it is arguably the most interesting part of the dataset to work on.

Solving more than 807 is a legitimate result to beat.

## Using it for Gaussian splatting

Poses plus tie points is what 3DGS pipelines consume. You will need to convert XMP into your
implementation's expected format — most read COLMAP `cameras.txt` / `images.txt` / `points3D.txt`.

- Rotation is already a world→camera matrix, which is COLMAP's convention. Convert to quaternion
  for `images.txt`
- Translation for COLMAP is `t = -R * position`, not the position itself
- `tiepoints.ply` maps to `points3D`
- Downsample the images to ~1600px first; nobody trains at 5464px, and the originals are here
  so you can choose

## Reproducing this alignment

See [`../docs/reproduce.md`](../docs/reproduce.md). The settings that produced it are in there —
`High` detector sensitivity, no downscaling. Expect ~807 again.
