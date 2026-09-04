---
created: 2026-09-03
updated: 2026-09-04

<!-- Scan: https://github.com/LpcPaul/tool-scout-skill (LpcPaul) -->
<!-- Verdict rubric: https://mm.dreamineering.com/playbook/applications/select-tech/ (Dreamineering) -->

# Tool Market Scout

JTBD brief → community scan (tool-scout) → scoring → verdict Buy / Build / Hybrid / Defer.

`{SKILL_DIR}` = directory of this SKILL.md.

## Scope

In: choosing SaaS, desktop/mobile, OSS lib, MCP/skill; constraints (platform, budget, OSS-only, data sovereignty)  
Out: docs lookup for an already named package, product strategy for a whole market, customer interviews, internal service TDR  
Fallback: if candidates <2 → Build or widen JTBD

## Gotchas

- **JTBD brief + ack before scan** – `references/jtbd-decompose.md`
- **No primary «alternatives to {brand}»** – capability queries from functional jobs
- **Do not reimplement scan** – delegate to `tool-scout` (Step 2)
- **Scoring + verdict** – only when ≥2 candidates **and** buy-or-build stake
- **No auto-Buy** – verdict waits for ack
- **Stars ≠ quality** – `references/scoring-rubric.md`

## Algorithm

### Step 0: Intake + scope gate

Collect trigger, constraints, must-have capabilities, buy-or-build stake (yes/no).  
If the user named a package and only wants **docs/API** → **stop**, wrong skill.  
If trigger = product to replace → Step 1a, not alternatives search.

### Step 1a: Native audit (if a product is named)

Official docs/features → **functional jobs**, not marketing. Format – `references/jtbd-decompose.md`.

### Step 1b: JTBD brief (gate)

Job statement, functional jobs, constraints, out of scope, buy-or-build stake.  
**STOP.** Show the user. Wait for «ok» / edits. No ack – no scan.

### Step 2: Community scan (tool-scout)

**Do not** run your own WebSearch/multi-source scan. Use the community skill:

```bash
npx skills add LpcPaul/tool-scout-skill
python3 "$TOOL_SCOUT_DIR/scripts/tool_scout.py" "CAPABILITY QUERY FROM JTBD" --json --limit 10
```

- Query = capability-first from functional jobs (`references/search-sources.md`)
- Supplementary `{brand} alternatives` – max 1, after brief only
- If `tool_scout.py` missing → ask user to install, then minimal capability search (no full scan reimplementation)

Normalize to candidate table (name, type, OSS/paid, source URL, covers jobs).

### Step 3: Score (conditional)

**Only if** ≥2 candidates **and** buy-or-build stake = yes.  
Rubric – `references/scoring-rubric.md`. ≥3 candidates + **Build yourself** row. Evidence required per score.

### Step 4: Verdict (gate)

**Only if** Step 3 ran. Buy | Build | Hybrid | Defer; top pick; risks; next step; how to start.  
**STOP.** Show scoring + verdict. Wait for ack. **No auto-Buy.**

If stake = no → shortlist only; offer verdict on request.

### Step 5: Writeback (optional)

If the user wants a note: `Research/Tooling/{topic-slug}.md` from `references/output-template.md` (or path they name). Skip if chat-only.

## Hard Stop Rules

- No scan without confirmed JTBD brief
- No primary «alternatives to {brand}»
- No reimplementing tool-scout scan
- No verdict without scoring when buy-or-build stake
- No auto-Buy; verdict waits for ack

## Definition of Done

- JTBD brief confirmed
- Scan via tool-scout (or install prompt + fallback)
- When stake: scoring with evidence + verdict with ack
- URLs are markdown links to primary sources

## Check commands

```bash
SKILL_DIR="<path-to-this-skill>"
ls "$SKILL_DIR/references"/*.md
```
