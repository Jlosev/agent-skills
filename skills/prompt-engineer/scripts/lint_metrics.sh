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
import os, re, sys
path = sys.argv[1]
text = open(path, encoding="utf-8").read()
root = os.path.dirname(os.path.abspath(path))
cited = set(re.findall(r"(?<![A-Za-z0-9_./-])(?:references|scripts|phases)/[A-Za-z0-9_./-]+\.[A-Za-z0-9]+", text))
missing = [rel for rel in sorted(cited) if not os.path.isfile(os.path.join(root, rel))]
print("missing_deps:", ", ".join(missing) if missing else "none")
m = re.match(r"^---\n(.*?)\n---", text, re.S)
if not m:
    print("colon_in_description: N/A")
    print("description_chars: N/A")
    sys.exit()
desc = re.search(r"^description:[ \t]*(?:[>|][-+]?[ \t]*\n((?:[ \t].*\n?)+)|(.+))", m.group(1), re.M)
if not desc:
    print("colon_in_description: N/A")
    print("description_chars: N/A")
else:
    raw = desc.group(1) if desc.group(1) is not None else desc.group(2)
    folded = " ".join(line.strip() for line in raw.splitlines() if line.strip()).strip("'\"")
    body = folded.replace("http://", "").replace("https://", "")
    print("colon_in_description:", "yes" if ":" in body else "no")
    n = len(folded)
    level = "critical" if n > 1024 else "major" if n > 400 else "ok"
    print(f"description_chars: {n} ({level}; limit 400, hard 1024)")
PY
