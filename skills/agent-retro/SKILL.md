---
created: 2026-09-03
updated: 2026-09-03

# Session Efficiency Retro

Analyze agent work **under the hood** from gryph logs: anti-patterns that burn context and time. Primary output – a readable report: **diagnosis → what we fix with a gate → what is not OK but has no autofix**. Rules/skills land only after explicit confirm.

`{SKILL_DIR}` = directory of this SKILL.md.

## Preconditions

- `gryph` on PATH; Shell with full rights to `~/Library/Application Support/gryph/`.
- `{SKILL_DIR}/scripts/extract_retro_logs.py` available.
- Workspace known (for `--project` and `.tmp/`).

## Scope

**In:** gryph JSONL, `extract_retro_logs.py`, `gryph session <id>`.

**Out (priority):**
1. **Retro Report**
2. **Fix Cards** – only after Viability Audit (step 5.5)
3. **Implementation stubs** – optional after confirm

**Fallback:** gryph missing → instruct install. Commands fail / zero events → **first** Shell `required_permissions: ["all"]` (sandbox blocks the gryph DB). After retry with full permissions and an empty query → check gryph in the **global** `~/.cursor/hooks.json`. Do **not** duplicate gryph in a workspace `.cursor/hooks.json` – Cursor merges configs and doubles every event.

## Gotchas

- Pattern recognition, not a single failed command.
- **Hook fan-out:** one action → several hook events. The script dedupes by `(SessionID, action, target, second)`. `stuck_session` – only deduped ≥ 100.
- **Gryph query limit:** the script passes `--limit 50000 --sort desc`. For 7d all-projects when `event_count > 50000` – fork a one-off extractor with a higher limit; do not leave the bump in this skill.
- **Cluster deep dive:** if `flagged_sessions > 30` – dive clusters, not every id.
- **search_misuse allowlist:** Grep/Glob in `.agents/`, `.cursor/`, `.tmp/`, `.git/` is not misuse. Knowledge-base notes → the vault search tool if the project uses one.
- **Export path:** only workspace `.tmp/gryph-export.jsonl`. Not `/tmp/`.
- **Cursor sandbox (CRITICAL):** all gryph commands and the extractor – Shell with `required_permissions: ["all"]`.
- **Infra stub ≠ auto-gap:** a playbook stub is a draft. Without step 5.5 it often duplicates existing Gotchas / detectors.

### Severity

| Level | Examples |
| --- | --- |
| **P0** | `destructive_shell` without confirm, hook bypass |
| **P1** | `re_read` ≥3, `search_misuse`, `stuck_session`, `thrash_command`, `failed_command`, `mcp_error` |
| **P2** | `re_read` ×2, `directory_read`, `rtk_dup`, `speculative_read` |
| **P3** | minor redundancy (manual, on deep dive) |

Session flagged: ≥1 P0/P1 or ≥2 P2 (`--min-severity`).

## Algorithm

### 1. Extract

Shell with `required_permissions: ["all"]`:

```bash
gryph query --since 1d --format jsonl | wc -l
python3 "{SKILL_DIR}/scripts/extract_retro_logs.py" --days 3 [--project "path/to/workspace"] [--min-severity P2]
```

Period: `/agent-retro 7d` → `--days 7`.

### 2. Flag

Read `flagged_sessions` and `sessions.<id>.anti_patterns`. Do not rely only on legacy `friction_points`.

### 3. Deep dive

If `flagged > 30` – **cluster deep dive**. `gryph session <session_id>`. Collect a 3–5 step timeline, inferred task, waste estimate.

Optional raw JSONL: `mkdir -p .tmp && gryph export --since 3d -o .tmp/gryph-export.jsonl`

### 4–5. Internal material

Build facts for the report (show the user only in the step 5.5 «Output» shape): sessions, flagged, top anti-patterns, per-cluster timeline, waste. Split (A) we fix with a gate / (B) not OK but no autofix / (C) detector noise.

Draft a Fix Card per finding. **Do not show** and **do not ask Implement** until 5.5.

### 5.5. Viability Audit (required, before Fix Cards)

For each card open the **concrete** files from the stub + related skill / AGENTS / rules / this extractor. Verdict: skip – already covered / wrong layer / no effect; narrow; do.

**Effect is mandatory** before `do` / `narrow`: «After the change the next run **will not be able to** / **will stop** [anti-pattern] because [gate/script/Hard Stop]».

#### User output (canonical)

```markdown
## Retro Report – [period] / [project?]

### Short
[2–4 lines]

### Metrics (compact)
- Sessions: N (flagged: M) | top: …

### Proposed improvements
Only `do` / `narrow`. Each card: Problem / What we change / Effect / Severity.

### Diagnosis without Implement
Friction that is **not OK**, but infra skip.

### Noise / already covered

Implement infra fixes? (all / #N / skip)
```

### 6. Implement (only after confirm)

Ask Global vs Local scope. Apply only audited `do`/`narrow` after an explicit «yes» on the diff. **Forbidden** to implement `skip-*` even if the user said `all`.

## Fix Playbooks

Stubs are **hypotheses for step 5**, not final infra.

| Anti-pattern | Agent instruction | Infra stub (hypothesis → audit 5.5) |
| --- | --- | --- |
| `re_read` | Check chat context before a second Read; park interim output in `.tmp/` | Context: re-read threshold in AGENTS.md |
| `directory_read` | Do not Read a directory; open a concrete file | Guardrail in the search rule |
| `search_misuse` | Knowledge base → vault search; Grep/Glob – code and scripts | Strengthen the search hook message |
| `rtk_dup` | One shell version per action | Detector first (same-second hook) |
| `stuck_session` | After 3 failed attempts – stop and ask | Capability in the **session skill**, not global AGENTS |
| `speculative_read` | AGENTS.md once per session; do not Read a changelog file as a search | Context: log routing in AGENTS.md |
| `thrash_command` | Do not repeat the same command | Guardrail or hook reminder |
| `destructive_shell` | Destructive ops – plan + explicit confirm | Guardrail hook on `rm -rf` |
| `hook_retry_loop` | Do not retry the same blocked tool | Improve the hook message |
| `failed_command` / `mcp_error` | Read stderr; do not retry blind | Context: known-good command patterns |

## Hard Stop Rules

- NEVER apply rules/skills/hooks without explicit user approval.
- User report – **always** the 5.5 shape.
- Fix Cards / Implement – **only after** Viability Audit; only `do`/`narrow`.
- **Forbidden** to ask «Implement?» on draft cards or on «Diagnosis without Implement».
- **Forbidden** to name friction in «Short» and then omit it from Proposed / Diagnosis / Noise.
- **Forbidden** to propose a stub «in AGENTS.md» if the canon is already in skill Gotchas or the issue is a detector false positive.
- Scope Global/Local – only on step 6.

## Definition of Done

- Gryph extracted (full permissions), `flagged_sessions` parsed
- Deep dive per flagged session (or cluster)
- Viability Audit done
- Canonical report shown
- Implement is optional after confirm

## Check commands

```bash
python3 "{SKILL_DIR}/scripts/extract_retro_logs.py" --days 1
python3 "{SKILL_DIR}/scripts/extract_retro_logs.py" --days 3 --project "path/to/workspace"
```

## Example

**In:** `/agent-retro 7d`  
Extract → flag → 5.5 audit → Short / Proposed / Diagnosis / Noise → Implement? only on Proposed.
