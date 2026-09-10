#!/usr/bin/env bash
# Verify downloaded files against the published SHA-256 manifest.
# Only checks files you actually have, so partial downloads verify fine.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${DEST:-$ROOT/data}"
SUMS="$ROOT/manifest/checksums.sha256"

[[ -f "$SUMS" ]] || { echo "missing $SUMS" >&2; exit 1; }
[[ -d "$DEST" ]] || { echo "nothing downloaded at $DEST" >&2; exit 1; }
cd "$DEST"

present=0; ok=0; bad=0; missing=0
while read -r sum path; do
  [[ -z "${sum:-}" ]] && continue
  if [[ -f "$path" ]]; then
    present=$((present+1))
    if [[ "$(sha256sum "$path" | cut -d' ' -f1)" == "$sum" ]]; then ok=$((ok+1))
    else bad=$((bad+1)); echo "CORRUPT: $path"; fi
  else missing=$((missing+1)); fi
done < "$SUMS"

total=$((present+missing))
echo
echo "checked $present of $total files"
echo "  ok        $ok"
echo "  corrupt   $bad"
echo "  absent    $missing  (not downloaded — fine for a partial fetch)"
[[ $bad -eq 0 ]] || { echo; echo "Re-download the corrupt files listed above."; exit 1; }
echo "All present files verified."
