---
created: 2026-09-04
updated: 2026-09-04
---

# Search Sources

Scan execution – **tool-scout** (`python3 scripts/tool_scout.py`). This file – query rules only.

## Query families

Per functional job – 1–2 capability-first queries for `tool_scout.py`:

```text
{capability} open source
{capability} {platform}
{capability} self-hosted
```

**Primary:** capability + platform + license intent  
**Supplementary (max 1, after JTBD brief):** `{brand} alternatives` or `{brand} vs`  
**Forbidden as primary:** `alternatives to {brand}`, `{brand} replacement`

## Feed into tool-scout

```bash
python3 "$TOOL_SCOUT_DIR/scripts/tool_scout.py" "{capability query}" --json --limit 10
```

Optional source filter:

```bash
python3 "$TOOL_SCOUT_DIR/scripts/tool_scout.py" "{query}" --sources github,npm,vscode,mcp,web --json
```

## Normalization schema

```yaml
name: string
type: saas | desktop | mobile | oss-lib | builtin | hybrid
license: MIT | Apache | GPL | proprietary | unknown
pricing: free | freemium | paid | one-time
covers_jobs: [J1, J2]
source_url: required
notes: one line
```

## Red flags (exclude or downgrade)

- No pricing for paid product after scan
- AGPL without note when user said commercial
- Last release >18 months for security-sensitive category
- Requires cloud when user said offline/local
