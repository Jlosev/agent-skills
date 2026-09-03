---
created: 2026-09-03
updated: 2026-09-03
---

# Search Sources

## Query families

На каждый functional job – 2–3 семейства:

```text
{capability} open source
{capability} {platform} app
{capability} self-hosted
best {capability} tool 2025 2026   ← только supplementary
```

**Primary:** capability + platform + license intent  
**Secondary:** brand name (для cross-check, не для discovery)  
**Tertiary:** `{brand} alternatives` – только после JTBD brief, max 1 query

## Source routing by tool type

| Tool type | Primary sources | Secondary |
|-----------|-----------------|-----------|
| Dev / CLI / lib | GitHub, npm, PyPI, awesome-lists | Hacker News, Reddit r/selfhosted |
| Agent / MCP / skill | skills.sh, GitHub | MCP directories |
| Desktop / mobile app | App Store, Play Store, Setapp, vendor sites | Product Hunt, G2 |
| SaaS / B2B | Vendor site, G2, Gartner (if public) | OSS self-hosted analog |
| Infra / data platform | CNCF, DB-Engines, vendor docs | company wiki (only if user said it is in scope) |

## Parallel scan checklist

- [ ] WebSearch – ≥3 capability queries
- [ ] GitHub – search + check awesome-list repos
- [ ] Paid – at least 2 SaaS/desktop candidates if user allows paid
- [ ] OSS – at least 2 if OSS preferred or allowed
- [ ] Native – OS built-in (e.g. macOS Dictation, Windows Speech)

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

- No pricing for paid product after search
- AGPL without legal note when user said «commercial»
- Last release >18 months for security-sensitive category
- Requires account + cloud when user said offline/local
