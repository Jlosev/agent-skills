---
created: 2026-09-03
updated: 2026-09-03

<!-- Based on: https://github.com/LpcPaul/tool-scout-skill -->
<!-- Based on: https://mm.dreamineering.com/docs/software/applications/tech-review/ -->

# Tool Market Scout

JTBD-first tool market research: job decompose → multi-source scan → scoring → verdict Buy / Build / Hybrid / Defer.

`{SKILL_DIR}` = directory of this SKILL.md.

## Scope

In: choosing SaaS, desktop/mobile app, OSS lib, MCP/skill; personal and team tools; constraints (platform, budget, OSS-only, data sovereignty)  
Out: product strategy for a whole market, customer interviews, design review of an internal service, implementing the chosen solution  
Fallback: if candidates <2 after scan → explicitly offer Build or widen the JTBD

## Gotchas

- **Do not start with «alternatives to {brand}»** – JTBD brief first (`references/jtbd-decompose.md`). «X alternatives» is allowed **only** as a supplementary query after capability search.
- **Stars ≠ quality** – for OSS look at maintainers, issues, license, last commit (`references/scoring-rubric.md`)
- **Product class beats brand**
- **Native audit** – if a product is named, check built-in OS/app capabilities first
- **Checkpoint required** after the JTBD brief and before the final verdict

## Algorithm

### Step 0: Intake

From `$ARGUMENTS` and context collect trigger, constraints, must-have / nice-to-have capabilities, build appetite. If the trigger is a product name → Step 1a, not alternatives search.

### Step 1a: Native audit (if a product is named)

Read official docs/features. List **functional jobs**, not marketing. Format – `references/jtbd-decompose.md`.

### Step 1b: JTBD brief (gate)

Build `JTBD_BRIEF` (job statement, functional jobs, workaround + cost, constraints, out of scope).  
**STOP.** Show the user. Wait for «ok» / edits. No ack – do not scan.

### Step 2: Query expansion

From each functional job, 2–3 capability-first query families. Supplementary `{brand} alternatives` only after the brief if the user came with «replace X». Rules – `references/search-sources.md`.

### Step 3: Multi-source scan

In parallel (at least 3 sources): WebSearch, GitHub / awesome-lists, product catalogs (G2, Product Hunt, app stores). Optional: skills.sh / MCP directories for agent tools.

Collect 5–12 candidates. Dedup by product. Every row needs a source URL.

### Step 4: Score

Rubric in `references/scoring-rubric.md`. At least 3 candidates + a **Build yourself** row. Each score 1–5 **with evidence**. No evidence – no score.

### Step 5: Verdict (gate)

Recommendation Buy | Build | Hybrid | Defer; top pick; runner-up; build case; risks; next step; how to start (brew / winget / npm / download).  
**STOP.** Show scoring + verdict. Wait for ack.

### Step 6: Writeback (optional)

If the user wants a note in their knowledge base, write `Research/Tooling/{topic-slug}.md` from `references/output-template.md` (or a path they name). Frontmatter `created` / `updated`. Skip if there is no vault / they said chat-only.

## Output (chat)

1. JTBD Brief (after 1b)
2. Candidate table
3. Scoring matrix
4. Verdict + next step

## Hard Stop Rules

- **Do not** start the scan without a confirmed JTBD brief
- **Do not** use «alternatives to {brand}» as the primary query
- **Do not** give a verdict without a scoring table and evidence
- **Do not** recommend Buy without checking constraints
- **Do not** write a vault note without `created`/`updated` if you do write one

## Definition of Done

- JTBD brief confirmed
- ≥5 candidates or an explicit reason for fewer
- Scoring with evidence on every dimension
- Verdict with next step and how to start
- All URLs are markdown links to the primary source

## Check commands

```bash
SKILL_DIR="<path-to-this-skill>"
ls "$SKILL_DIR/references"/*.md
```
