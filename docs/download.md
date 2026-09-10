# Downloading the dataset

The images are **not stored in this GitHub repository** — GitHub is not built for this, and
Git LFS bandwidth caps would make it unusable. This repo holds documentation, manifests and
checksums; the images live on hosts designed for large public datasets.

Total: **14.1 GB, 812 images.**

---

## Why it is packaged the way it is

**The images are published as individual files, not one giant archive.** That is deliberate:

- You can download **one capture group** instead of all 14.1 GB.
- Downloads **resume**. A dropped connection partway through does not start over.
- Each file is **individually checksummed**, so corruption is localised, not fatal.
- No scratch space needed just to unpack an archive.

**Nothing is gzipped.** JPEG is already compressed — measured on this dataset, gzip reclaims
**0.2%** while costing hours of CPU and destroying random access. Where archives are offered
(mirrors below), they are **store-only ZIPs**, split per capture group.

---

## Primary — Hugging Face

Resumable, parallel, hash-verified, and the CLI handles retries for you.

```bash
pip install -U 'huggingface_hub[cli]'

# sample pack (~420 MB) — look before you commit to 14.1 GB
./scripts/download.sh --sample

# everything
./scripts/download.sh --full

# just the low-altitude trunk tiers (153 images)
./scripts/download.sh --group Original_low --group Original_mid
```

Or browse the files directly: **https://huggingface.co/datasets/Matt1Up/tree-minnetonka-photogrammetry**

Raw CLI, if you prefer not to use the wrapper:

```bash
hf download Matt1Up/tree-minnetonka-photogrammetry --repo-type dataset --local-dir ./data --include 'images/*'
```

---

## Mirror — Internet Archive

Permanent, no account needed, and every item gets a **BitTorrent** file automatically.
Torrent is the friendliest option for the full set: it resumes, verifies, parallelises, and
costs the project nothing.

**https://archive.org/details/tree-minnetonka-photogrammetry-2020**

```bash
# whole set over torrent
aria2c https://archive.org/download/tree-minnetonka-photogrammetry-2020/tree-minnetonka-photogrammetry-2020 _archive.torrent

# or a single group over plain HTTPS, resumable
curl -C - -O https://archive.org/download/tree-minnetonka-photogrammetry-2020/images/Grid_Down_1-1.jpg
```

---

## Sample pack

A small curated subset — enough to judge image quality, overlap and metadata before
committing to the full download. Served from `files.hometwin.io`.

---

## Verifying what you downloaded

```bash
./scripts/verify.sh
```

Checks SHA-256 for every file you actually have and ignores the rest, so partial downloads
verify cleanly. `manifest/checksums.sha256` is the authoritative list;
`manifest/images.csv` additionally carries dimensions, capture time and GPS per image.

## If a mirror is down

All mirrors carry byte-identical files with matching checksums. Pull from whichever works —
`verify.sh` will confirm you got the right bytes regardless of source.
