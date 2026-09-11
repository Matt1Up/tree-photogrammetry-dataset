# Downloading the dataset

The images are **not stored in this GitHub repository** — GitHub is not built for this, and
Git LFS bandwidth caps would make it unusable. This repo holds documentation, manifests and
checksums; the images live on Hugging Face.

Total: **14.1 GB, 812 images.**

---

## Why it is packaged the way it is

**The images are published as individual files, not one giant archive.** That is deliberate:

- You can download **one capture group** instead of all 14.1 GB.
- Downloads **resume**. A dropped connection partway through does not start over.
- Each file is **individually checksummed**, so corruption is localised, not fatal.
- No scratch space needed just to unpack an archive.

**Nothing is gzipped.** JPEG is already compressed — measured on this dataset, gzip reclaims
**0.2%** while costing hours of CPU and destroying random access.

---

## Hugging Face

Resumable, parallel, hash-verified, and the CLI handles retries for you.

```bash
pip install -U huggingface_hub

# sample pack (~420 MB) — look before you commit to 14.1 GB
./scripts/download.sh --sample

# everything — images, sample, COLMAP, tie points
./scripts/download.sh --full

# the 812 images only
./scripts/download.sh --images

# just the low-altitude trunk tiers (153 images)
./scripts/download.sh --group Original_low --group Original_mid
```

Or browse the files directly: **https://huggingface.co/datasets/Matt1up/tree-minnetonka-photogrammetry**

Raw CLI, if you prefer not to use the wrapper. Run it again if it stops — finished files are
skipped.

```bash
# everything
hf download Matt1up/tree-minnetonka-photogrammetry --repo-type dataset --local-dir ./data

# images only
hf download Matt1up/tree-minnetonka-photogrammetry --repo-type dataset --local-dir ./data --include 'images/*'
```

---

## Sample pack

A small curated subset — enough to judge image quality, overlap and metadata before
committing to the full download. It is on Hugging Face under `sample/`;
`./scripts/download.sh --sample` fetches it.

---

## Verifying what you downloaded

```bash
./scripts/verify.sh
```

Checks SHA-256 for every image you actually have and ignores the rest, so partial downloads
verify cleanly. `manifest/checksums.sha256` is the authoritative list;
`manifest/images.csv` additionally carries dimensions, capture time and GPS per image.
