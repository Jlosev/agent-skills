#!/usr/bin/env bash
# verify_export.sh – mechanical gate for canvas-to-html Step 3
set -euo pipefail

OUTPUT="${1:?usage: verify_export.sh <output-dir>}"

fail() { echo "FAIL: $*" >&2; exit 1; }
warn() { echo "WARN: $*" >&2; }

test -d "$OUTPUT" || fail "output dir missing: $OUTPUT"
test -f "$OUTPUT/index.html" || fail "missing index.html"

shopt -s nullglob
files=("$OUTPUT/index.html" "$OUTPUT"/*.css "$OUTPUT"/*.js)
for f in "${files[@]}"; do
  [[ -f "$f" ]] || continue
  if grep -qE 'href="/|src="/|fetch\(|cdn\.|unpkg\.|jsdelivr\.' "$f" 2>/dev/null; then
    fail "forbidden pattern in $f"
  fi
done

# Asset refs must be relative (./…), #, or data:. Content hyperlinks may be https?://.
if [[ -f "$OUTPUT/index.html" ]]; then
  while IFS= read -r ref; do
    attr="${ref%%=*}"
    val="${ref#*=}"
    val="${val#\"}"
    val="${val%\"}"
    case "$val" in
      ./* | "#"* | data:*) ;;
      http://* | https://*)
        # Content links OK; asset-like CDN already failed above.
        ;;
      *)
        warn "non-relative ${attr}: ${val}"
        ;;
    esac
  done < <(grep -oE '(href|src)="[^"]+"' "$OUTPUT/index.html" 2>/dev/null || true)
fi

echo "OK: $OUTPUT verified"
exit 0
