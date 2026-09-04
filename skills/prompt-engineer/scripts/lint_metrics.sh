#!/usr/bin/env bash
# Usage: lint_metrics.sh <path-to-md>
set -euo pipefail
FILE="${1:?file required}"

echo "=== lint_metrics: $FILE ==="
echo "lines: $(wc -l < "$FILE" | tr -d ' ')"
echo "must_count: $(grep -ciE 'IMPORTANT|YOU MUST|\bMUST\b' "$FILE" 2>/dev/null || true)"
echo "sections:"
grep -E '^## (Hard Stop Rules|Definition of Done|Команды проверки|Check commands|Scope|Gotchas|Алгоритм|Algorithm|Пример|Example|Examples|Preconditions|Предусловия)' "$FILE" || true
echo "agent_specific: $(grep -ciE 'Claude Code|Codex only|Cursor only|/skill-creator' "$FILE" 2>/dev/null || true)"
echo "skill_deps: $(grep -ciE 'сначала (вызови|запусти|используй).*(skill|/skill-)' "$FILE" 2>/dev/null || true)"
echo "has_example_section: $(grep -cE '^## Пример|^## Example|^## Examples' "$FILE" 2>/dev/null || true)"
echo "has_preconditions: $(grep -cE '^## Preconditions|^## Предусловия' "$FILE" 2>/dev/null || true)"
python3 - "$FILE" <<'PY'
import re, sys
path = sys.argv[1]
text = open(path, encoding="utf-8").read()
m = re.match(r"^---\n(.*?)\n---", text, re.S)
if not m:
    print("colon_in_description: N/A")
    sys.exit()
desc = re.search(r"^description:\s*(?:>\s*\n)?((?:[ \t].+\n?)+)", m.group(1), re.M)
if not desc:
    print("colon_in_description: N/A")
else:
    body = desc.group(1).replace("http://", "").replace("https://", "")
    print("colon_in_description:", "yes" if ":" in body else "no")
PY
