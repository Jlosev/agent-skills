---
name: prompt-engineer
description: >
  Lint and review agent instruction files (SKILL.md, agent.md, CLAUDE.md, protocol) for executability.
  Triggers prompt-engineer, lint skill, review SKILL.md, Publication DoD, quality checklist, agent instructions review.
  Checks triggers, progressive disclosure, Hard Stop, DoD, deterministic script offload per quality-guide.
  Not for scaffolding a new skill from scratch, chat-prompt optimization, or model-specific prompt research.
metadata:
  scope: public
  author: Jlosev
  version: "1.2.0"
  tags: "skill-dev,prompt-engineering,lint"
created: 2026-09-03
updated: 2026-09-04
user-invocable: true
---

# Prompt Engineer

Lint/review agent instruction files. Criteria live **only** in `references/quality-guide.md` (do not duplicate them here).

`{SKILL_DIR}` = directory of this SKILL.md.

## Scope

In: SKILL.md, agent `.md`, CLAUDE.md, protocol  
Out: runtime debug, strategy, scaffold from scratch, chat-prompt optimization, model-specific prompt research  
Fallback: generic checklist + ask the type

## Preconditions

- [ ] Target file path from `$ARGUMENTS`.
- [ ] `references/quality-guide.md` read.
- [ ] If called from a multi-skill factory pipeline – only after the orchestrator’s validation checkpoint.

## Algorithm

### Step 1: File and type

Path from `$ARGUMENTS` or ask.

| Signal | Type |
| --- | --- |
| `skills/` + `name`/`description` | SKILL.md |
| `agents/` + `name`/`tools` | Agent |
| `CLAUDE.md` | CLAUDE.md |
| `protocols/` | Protocol |
| else | Generic |

### Step 2: Analyze

1. Read `references/quality-guide.md` – publication DoD + quality criteria + type checklist + anti-patterns. For **multi-step / AskQuestion** skills also run Workflow Enforcement Patterns.
2. Read the target file.
3. For each criterion: check → severity (critical/major/minor) + a concrete fix (`→`).
4. **Determinism:** rigid CLI sequences → suggest moving them to `scripts/`.
5. **Quality criteria** (SKILL.md only): clarity, structure, self_containment, safety, preconditions, agent_agnostic, examples, self_improvement – table ✅/❌ + fix.

Metrics script:

```bash
"{SKILL_DIR}/scripts/lint_metrics.sh" <file>
```

Description metrics: character length, `:` check, trigger phrases, negative triggers – per DoD §Discovery.

Also: compression, anti-patterns table, token estimate (words×1.3), extraction (conditional ≥30 lines → `references/`).

### Step 3: Report

```
## Prompt Engineer: [file]

**Type:** … | **Size:** ~N tok (~M lines) | **DoD:** Pass/Fail

### Critical / Major / Minor
- [loc]: [issue] → [exact fix text]

### DoD Checklist (SKILL.md)
| Frontmatter | Discovery | Body | Safety | Metrics | → ✅/❌ |

### Quality (SKILL.md)
| clarity | structure | self_containment | safety | preconditions |
| agent_agnostic | examples | self_improvement | → score band |

Score band: 0 critical + ≤2 major → likely 70–85; else likely <60.

### Anti-patterns | What is good | **Grade:** A/B/C/D
A=0 critical ≤1 major | B=0 critical ≤3 major | C=1+ critical
```

### Step 4: Apply

Ask «Apply? (all / selected / no)». Fixes are exact replacement text, not «improve wording».

### Step 5: Post-run

If lint found ≥1 major on the quality criteria – propose 1 concrete improvement for **prompt-engineer itself**. Format: «Gardener: …».

## Example

**In:** «lint SKILL.md – wall of text, path: .agents/skills/foo/SKILL.md»

```
## Prompt Engineer: foo/SKILL.md
**Type:** SKILL.md | **Size:** ~420 tok (~180 lines) | **DoD:** Fail
### Major
- description: internals instead of triggers → «Use when… Triggers lint, review prompt…»
- body: no ## Example → add a section with input/result
### Quality
| clarity ❌ | examples ❌ | preconditions ❌ | … |
**Grade:** C
Apply fixes? (all / selected / no)
```

## Hard Stop Rules

- If invoked from a factory pipeline: run only as a Task from the orchestrator; the parent does not lint inline.
- Report **before** edits
- CLAUDE.md – warn before apply (project-shared)
- Do not change meaning; do not add new content
- `:` in description – critical

## Definition of Done

- Report with severity + DoD checklist + quality table (SKILL.md) + grade shown
- User answered the apply prompt
- Applied fixes = exact text replacements
- Post-run Gardener note if ≥1 major on quality criteria

## Check commands

```bash
"{SKILL_DIR}/scripts/lint_metrics.sh" <file>
grep -A5 '^description:' <file>   # no ':' in value lines
```

## Gotchas

- A baseline without the guide finds the obvious; value = DoD + quality table + anti-patterns + fix texts
- External `quality_score` from an evaluator is not replaced by the score band
- preconditions ≠ Hard Stop Rules
- agent_agnostic minor does not block publication
- description >400 major; `:` critical
- unconditional steps stay in the body, not in references/
- Use «Trigger phrases …» instead of «Triggers:» in description (avoid `:`)
