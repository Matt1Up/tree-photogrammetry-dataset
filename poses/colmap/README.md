# COLMAP-format poses

Drop-in sparse reconstruction. This is what Gaussian splatting and NeRF pipelines expect, so
you can start training without running structure-from-motion first.

```
colmap/
  cameras.txt     807 PINHOLE cameras
  images.txt      807 poses (quaternion + translation)
  points3D.txt    1,206,765 points — hosted with the images, 56 MB
```

`points3D.txt` is not in git because of its size. Get it with:

```bash
./scripts/download.sh --colmap
```

Then arrange it as your pipeline expects, usually:

```
your_project/
  images/          the 812 jpgs
  sparse/0/        cameras.txt  images.txt  points3D.txt
```

## What was converted, and how it was checked

Converted from the RealityScan XMP sidecars in [`../xmp/`](../xmp/) by
[`../../scripts/xmp-to-colmap.py`](../../scripts/xmp-to-colmap.py).

- **Camera model is `PINHOLE`.** Every XMP reports `DistortionModel="perspective"` with
  coefficients `0 0 0 0 0 0`, so there is no distortion to carry over.
- **Principal point is image centre** (2732, 1820). The XMPs put it there to within 1e-17.
- **Focal in pixels** = `FocalLength35mm × 5464 / 36`.
- **Translation** is `t = −R·C`, not the camera position. RealityScan stores the camera centre;
  COLMAP wants the translation vector. Mixing these up is the usual way these conversions go
  wrong and it fails silently.
- **The camera frame was not assumed.** The converter tests both plausible conventions by
  reprojecting the tie points through the resulting matrices and keeps whichever actually puts
  points in front of the cameras and inside the frame. Result: RealityScan's frame matches
  COLMAP's directly, 57.0% of sampled points landing in-frame versus 4.1% for the y/z-flipped
  alternative. Re-run the script and it prints those numbers again.
- All 807 quaternions are unit length.

## Scale

**The coordinate frame has no verified scale.** It is a local frame — not lat/lon, and not
confirmed to be metres.

I tried to check it against the EXIF GPS and could not. Comparing solved camera separations to
GPS separations gives a ratio that keeps changing with baseline length — 3.55 at 3–8 m, 2.03 at
8–15 m, 1.42 at 15–25 m — which is what GPS noise looks like, not a scale factor. The entire
capture spans roughly 17 m of GPS footprint, and consumer GPS carries several metres of error
per fix, so there is no baseline here long enough to calibrate against.

For Gaussian splatting, NeRF, or novel-view synthesis this does not matter. If you need real
units, measure something in the scene.

## Four cameras you may want to drop

[`../suspect_cameras.txt`](../suspect_cameras.txt) lists four whose solved focal length is
around 9.2 mm equivalent. The aircraft has a fixed 28 mm-equivalent lens, so those are not
physically possible — they are badly constrained solves that RealityScan accepted.

```
The_Tree-88.jpg   The_Tree-137.jpg   The_Tree-223.jpg   The_Tree-235.jpg
```

They are included so the export matches the alignment exactly. Drop them if your pipeline is
sensitive to bad intrinsics — for 3DGS, four wrong cameras out of 807 will put floaters in the
scene.
