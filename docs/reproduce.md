# Reproducing the reconstruction

**Expect ~807 of 812 images to align.** That is the honest result on this subject, not a
failure to debug away. If you are getting substantially fewer, the settings below are where to
look — vegetation needs different treatment from buildings.

---

## Working with foliage

- **Texture is self-similar.** One leaf looks like the next, so matchers produce confident wrong
  correspondences.
- **The subject occludes itself.** The canopy hides the trunk from above, the trunk hides the far
  canopy from below. That is why the low and mid tiers exist.
- **Thin structures fall below a pixel.** Outer twigs will not reconstruct at this GSD and no
  setting changes that.
- **Wind normally ruins foliage capture.** This one was flown in still air, so that variable is
  gone. A windy recapture of the same tree would not behave the same way.

---

## RealityCapture / RealityScan

**Alignment** — suggested starting points, not the original run's settings.
| setting | value | why |
|---|---|---|
| Image overlap | `High` | dense orbits with heavy overlap |
| Detector sensitivity | **`High`** | `Medium` tends to under-detect on foliage |
| Max features per image | `40000` | |
| Max features per mpx | `10000` | |
| Image downscale factor | `1` | do not downscale; thin structure is already marginal |

**Do not downscale.** The usual "halve resolution to speed up alignment" advice actively
destroys this dataset — branch detail is close to the resolution limit already.

**Reconstruction** — `High` detail. Vegetation is where high detail earns its cost, unlike
flat urban facades. Set a tight reconstruction region around the tree and its ground plane;
background vegetation will otherwise consume enormous time reconstructing an unusable mess.

Expect to spend real time in **filtering and cleanup**. Foliage reconstruction produces
floaters — disconnected blobs where the matcher was confident and wrong. Filter by
component size before texturing.

---

## Agisoft Metashape

```
Align Photos:  Accuracy Highest · Generic preselection on
               Key point limit 60,000 · Tie point limit 0 (unlimited)
```

Higher key point limit than you would use on buildings, and an unlimited tie point limit —
foliage needs the density. Then:

```
Optimize Cameras → Build Depth Maps (High, Mild filtering) → Build Dense Cloud
```

**Use `Mild` depth filtering, not `Aggressive`.** Aggressive filtering removes thin branches
along with the noise, which loses the part of the subject you actually came for.

---

## COLMAP

```bash
colmap feature_extractor \
  --database_path db.db --image_path images/ \
  --ImageReader.camera_model SIMPLE_RADIAL \
  --ImageReader.single_camera 1 \
  --SiftExtraction.max_num_features 16384 \
  --SiftExtraction.estimate_affine_shape 1 \
  --SiftExtraction.domain_size_pooling 1

colmap exhaustive_matcher --database_path db.db \
  --SiftMatching.guided_matching 1

colmap mapper --database_path db.db --image_path images/ --output_path sparse/
```

`estimate_affine_shape` and `domain_size_pooling` are slow but measurably improve matching on
repetitive organic texture. `guided_matching` helps recover correct matches where the naive
ratio test discards them. Exhaustive matching is tractable at 812 images.

---

## Gaussian splatting

This set works well as a 3DGS benchmark, and arguably better than as a mesh source — splats
handle thin foliage far more gracefully than any mesh reconstructor.

Run COLMAP as above for camera poses, then feed `sparse/0` to your splatting implementation.
The low and mid tiers matter here: without near-ground upward-looking coverage, the trunk
region degenerates into smeared blobs.

---

## Capture tiers, and using a subset

| group | images | what it buys you |
|---|---:|---|
| `The_Tree` | 659 | full crown — enough on its own for a canopy-only model |
| `Original_low` | 85 | trunk, root flare, canopy underside |
| `Original_mid` | 68 | lower canopy, branch structure |

For a faster first run use `The_Tree` alone. Add the low and mid tiers when you want the trunk
to actually resolve — that is the difference between a green blob on a stick and a tree.

**The two sessions are two days apart** (18 and 20 July 2020). Lighting and leaf position
differ between them. Solvers handle this, but it is a real source of tie-point noise and worth
knowing when you are interpreting your residuals.
