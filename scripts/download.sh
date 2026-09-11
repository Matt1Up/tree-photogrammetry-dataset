#!/usr/bin/env bash
# Download the dataset from Hugging Face.
#   ./scripts/download.sh --sample            small evaluation pack
#   ./scripts/download.sh --colmap            COLMAP sparse reconstruction (points3D.txt, 58 MB)
#   ./scripts/download.sh --images            all 812 images (15.1 GB)
#   ./scripts/download.sh --full              everything — images, sample, COLMAP, tie points
#   ./scripts/download.sh --group NAME [...]  one or more capture groups
set -euo pipefail

HF_REPO="${HF_REPO:-Matt1up/tree-minnetonka-photogrammetry}"
DEST="${DEST:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/data}"

groups=(); mode=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --sample) mode=sample; shift ;;
    --colmap) mode=colmap; shift ;;
    --images) mode=images; shift ;;
    --full)   mode=full;   shift ;;
    --group)  groups+=("$2"); mode=group; shift 2 ;;
    --dest)   DEST="$2"; shift 2 ;;
    -h|--help) sed -n '2,7p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done
[[ -z "$mode" ]] && { sed -n '2,7p' "$0"; exit 2; }

if ! command -v hf >/dev/null 2>&1 && ! command -v huggingface-cli >/dev/null 2>&1; then
  echo "This downloader uses the Hugging Face CLI (resumable, parallel, verifies hashes)."
  echo "Install it with:  pip install -U huggingface_hub"
  echo
  echo "Or download files in a browser: https://huggingface.co/datasets/$HF_REPO/tree/main"
  exit 1
fi
HF=$(command -v hf || command -v huggingface-cli)

mkdir -p "$DEST"
args=(download "$HF_REPO" --repo-type dataset --local-dir "$DEST")

case "$mode" in
  sample) args+=(--include "sample/*") ;;
  colmap) args+=(--include "colmap/*") ;;
  images) args+=(--include "images/*") ;;
  full)   : ;;
  group)  for g in "${groups[@]}"; do args+=(--include "images/${g}*"); done ;;
esac

echo "→ $HF_REPO  ($mode)  →  $DEST"
"$HF" "${args[@]}" || {
  echo
  echo "Stopped early. Run the same command again — finished files are skipped."
  echo "HTTP 429 is Hugging Face's rate limit: wait five minutes, or log in first with  hf auth login"
  exit 1
}
echo
echo "Done. Verify integrity with:  ./scripts/verify.sh"
