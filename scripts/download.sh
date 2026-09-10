#!/usr/bin/env bash
# Download the image set for this dataset.
#   ./scripts/download.sh --sample            small evaluation pack
#   ./scripts/download.sh --colmap            COLMAP sparse reconstruction (points3D.txt, 56 MB)
#   ./scripts/download.sh --full              everything (14.1 GB, 812 images)
#   ./scripts/download.sh --group NAME [...]  one or more capture groups
set -euo pipefail

HF_REPO="${HF_REPO:-Matt1Up/tree-minnetonka-photogrammetry}"
DEST="${DEST:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/data}"

groups=(); mode=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --sample) mode=sample; shift ;;
    --colmap) mode=colmap; shift ;;
    --full)   mode=full;   shift ;;
    --group)  groups+=("$2"); mode=group; shift 2 ;;
    --dest)   DEST="$2"; shift 2 ;;
    -h|--help) sed -n '2,6p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done
[[ -z "$mode" ]] && { sed -n '2,6p' "$0"; exit 2; }

if ! command -v hf >/dev/null 2>&1 && ! command -v huggingface-cli >/dev/null 2>&1; then
  echo "This downloader uses the Hugging Face CLI (resumable, parallel, verifies hashes)."
  echo "Install it with:  pip install -U 'huggingface_hub[cli]'"
  echo
  echo "Alternative mirrors that need no tooling are listed in docs/download.md"
  exit 1
fi
HF=$(command -v hf || command -v huggingface-cli)

mkdir -p "$DEST"
args=(download "$HF_REPO" --repo-type dataset --local-dir "$DEST")

case "$mode" in
  sample) args+=(--include "sample/*") ;;
  colmap) args+=(--include "colmap/*") ;;
  full)   args+=(--include "images/*") ;;
  group)  for g in "${groups[@]}"; do args+=(--include "images/${g}*"); done ;;
esac

echo "→ $HF_REPO  ($mode)  →  $DEST"
"$HF" "${args[@]}"
echo
echo "Done. Verify integrity with:  ./scripts/verify.sh"
