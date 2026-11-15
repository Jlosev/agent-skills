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
# Phrases skills.sh security audits flag: privilege escalation, bypassing user review, installing third-party skills.
echo "audit_tells: $(grep -ciE 'full permission|elevated permission|\bsudo\b|no approval|(do not|don.t) (wait|stop) for (approval|ok)|without (asking|approval)|npx skills add [a-z0-9_.-]+/|outside the sandbox|dangerouslyDisableSandbox|вне песочницы|полными правами|не жди (подтверждения|«?ок)' "$FILE" 2>/dev/null || true)"
echo "has_example_section: $(grep -cE '^## Пример|^## Example|^## Examples' "$FILE" 2>/dev/null || true)"
echo "has_preconditions: $(grep -cE '^## Preconditions|^## Предусловия' "$FILE" 2>/dev/null || true)"
# Python in its own file: a here-doc needs a temp file, which agent sandboxes often refuse.
python3 "$(dirname "$0")/lint_metrics.py" "$FILE"
