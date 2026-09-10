# Single Tree — High-Density Photogrammetry Dataset

**812 full-resolution photographs (14.1 GB) of one mature deciduous tree, captured from
ground level to above the canopy. 807 of 812 images align — and the solved camera poses
ship with it.**
Released under CC BY 4.0 — free for commercial, academic and ML use with attribution.

> ## 🏆 Winner — RealityCapture #RCmonthlyChallenge, August 2020
>
> This reconstruction and its [companion Chicago city scan](https://github.com/Matt1Up/chicago-photogrammetry-dataset) were both named
> winners of Capturing Reality's monthly challenge, announced by **RealityScan** — the makers
> of RealityCapture — on 17 September 2020 in
> **[Winners of AUGUST #RCmonthlyChallenge ▶](https://www.youtube.com/watch?v=PfzdaZbUrFc)**.
>
> The video description credits the win as *"@Matt1up — Tree and Chicago city"*, and the
> tree model appears in the reel under a `created by: @Matt1up` title card.

![Tree reconstruction](preview/hero.jpg)

---

## Why this exists

Vegetation is the hardest subject in photogrammetry. Thin branches, self-similar texture,
leaves that move between frames, and a canopy that occludes its own trunk — a tree breaks
assumptions that buildings never test.

Most published photogrammetry datasets are buildings, statues or turntable objects precisely
because those are easy. This one is deliberately the hard case: **a single tree, covered
densely enough to actually solve**, with the low-altitude trunk passes that most aerial
captures skip.

If you are benchmarking a matcher, a Gaussian splatting pipeline, or a mesh reconstructor,
this is the set that will tell you where it breaks.

## The reconstruction

[![Tree reconstruction](preview/video-final.jpg)](https://vimeo.com/485263810)

*Finished reconstruction — click to watch on Vimeo*

[![Drone capture](preview/video-drone.jpg)](https://vimeo.com/494607575)

*Capture and processing — click to watch on Vimeo*

Full project write-up: **[mattguertin.com/portfolio/tree](https://mattguertin.com/portfolio/tree/)**

| | | |
|---|---|---|
| ![](preview/render-1.jpg) | ![](preview/render-2.jpg) | ![](preview/render-3.jpg) |

## What's in the dataset

| | |
|---|---|
| **Images** | 812 JPEG · 14.06 GB |
| **Alignment** | 807 / 812 images solve |
| **Sensor** | Hasselblad L1D-20c — 1" 20 MP CMOS (DJI Mavic 2 Pro) |
| **Resolution** | 5464 × 3640 |
| **Lens** | 10.3 mm — 28 mm full-frame equivalent, f/2.8 |
| **Geotagging** | GPS latitude / longitude / altitude in EXIF, all 812 images |
| **Location** | Minnetonka, MN — 44.944 N, −93.426 W |
| **Captured** | 18 and 20 July 2020 |
| **Camera poses** | included — 807 solved cameras + 1.2M tie points ([`poses/`](poses/)) |

### Capture tiers

The set is two sessions, two days apart, covering different heights. **The low and mid tiers
are the valuable, unusual part** — they are hover passes at knee and chest height with the
camera angled *upward*, capturing the trunk, root flare and canopy underside that a
conventional descending orbit never sees.

| group | images | date | height above takeoff | gimbal | covers |
|---|---:|---|---|---|---|
| `Original_low` | 85 | 2020-07-18 | +0.5 m | +6.2° (up) | trunk, root flare, canopy underside |
| `Original_mid` | 68 | 2020-07-18 | +1.7 m | +2.3° (up) | lower canopy, branch structure |
| `The_Tree` | 659 | 2020-07-20 | orbit to above canopy | varies | full crown and outer canopy |
| **total** | **812** | | | | |

## The capture rig

![FARO Focus S150 set up beneath the subject tree](preview/rig-laser.jpg)

Photography flown with a **DJI Mavic 2 Pro** (Hasselblad L1D-20c). EXIF records processing in
Adobe Lightroom Classic 9.3.

A **FARO Focus S150** terrestrial laser scanner was also on site, visible above.
**Its data is not part of this release** — this dataset is the 812 photographs only. The
scanner is shown because it is part of the honest record of how the subject was captured, not
because point clouds are included.

## Camera poses — start training immediately

**[`poses/`](poses/) contains a solved alignment**: 807 cameras with full intrinsics and
extrinsics, plus a 1,206,765-point sparse cloud. That is the equivalent of a COLMAP sparse
reconstruction, already done.

Most people who download a photogrammetry dataset spend their first several hours running
structure from motion before they can begin. On 812 images at 20 MP that is a long wait for a
result you already know. **Skip it.**

| | |
|---|---|
| `poses/xmp/` | 807 XMP sidecars, named to match `images/` |
| `poses/cameras.csv` | the same data as one table |
| `poses/unaligned.txt` | the 5 that did not solve |
| `tiepoints.ply` | 1.2M sparse points, hosted with the images (77 MB) |

Solved in **RealityScan 2.2**, the current free version, so the alignment is reproducible by
anyone rather than tied to a licence. Format details and Gaussian-splatting conversion notes
are in [`poses/README.md`](poses/README.md).

**All five unaligned images come from the low and mid tiers**, none from `The_Tree` — the
near-ground upward-angled frames are genuinely the hard ones. Beating 807 is a real result.

## Download

Images are hosted off GitHub — this repository holds documentation, manifests and checksums.
See **[docs/download.md](docs/download.md)** for mirrors and resumable download instructions.

```bash
# sample pack first (~420 MB) — evaluate before committing to 14 GB
./scripts/download.sh --sample

# full image set
./scripts/download.sh --full

# just the low-altitude trunk tiers (153 images)
./scripts/download.sh --group Original_low --group Original_mid
```

Every file is checksummed. After downloading:

```bash
./scripts/verify.sh
```

## Reproducing the reconstruction

See **[docs/reproduce.md](docs/reproduce.md)** for alignment settings.
Aligns in RealityCapture / RealityScan, Agisoft Metashape, COLMAP and Meshroom. Images carry
GPS, so georeferencing works without ground control.

**Expect ~807/812.** A handful of frames genuinely do not solve — that is the honest result on
this subject, not a processing failure to debug away. The solved alignment is in [`poses/`](poses/)
if you want to compare against it rather than start from nothing.

## Known characteristics

Read these before you file a bug — they are properties of the capture, not defects in the upload.

- **Captured in dead-still air, deliberately.** Both sessions were flown only when there was no
  wind at all. The tree is three blocks from where I lived; I watched the leaves from my window
  and drove over to fly the moment they stopped moving. **This is the single biggest reason the
  set solves as well as it does.** Foliage photogrammetry usually fails because the subject moves
  between frames — here it did not.
- **The 153 low/mid images had their metadata repaired.** These were exported through
  RealityCapture, which stripped all EXIF. The original camera metadata — make, model, GPS,
  timestamp, exposure — was grafted back on from the untouched 16-bit source files.
  **Pixel data is byte-identical to the export; only the metadata block was rewritten.**
  Verified: decoded-RGB checksums match before and after.
- **Filenames were normalised.** Those same 153 files carried a RealityCapture double extension
  (`Original_low-10.png.geometry.jpg`). Renamed to `Original_low-10.jpg`. Content untouched.
- **16-bit originals exist for 153 images.** The low and mid tiers have 16-bit lossless PNG
  masters (~100 MB each, 15 GB total). They are not in this release because 8-bit is what every
  photogrammetry pipeline actually consumes, and they would double the download for no
  alignment benefit. Open an issue if you have a use for them.
- **These are Lightroom exports, not raw.** Raw DNGs are not part of this release.

## Licence

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

Released under [Creative Commons Attribution 4.0 International](LICENSE).
**You may use this commercially, and you may train models on it.** You must give credit.

```
Single Tree Photogrammetry Dataset — Matthew Guertin, 2020.
Licensed CC BY 4.0. https://github.com/Matt1Up/tree-photogrammetry-dataset
```

See [CITATION.cff](CITATION.cff) for BibTeX and academic citation formats.

## Related

- **[Chicago / Grant Park dataset](https://github.com/Matt1Up/chicago-photogrammetry-dataset)** —
  2,751 aerial images and 43 laser stations over downtown Chicago. The large-area counterpart
  to this controlled single-subject set.
- **[mattguertin.com](https://mattguertin.com)** — portfolio and other work.

---

Captured, processed and released by **Matthew Guertin**.
If you build something with this, I would genuinely like to see it — open an issue.
