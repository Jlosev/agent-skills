---
name: critic
description: >
  Manual adversarial review of any work artifact vs the original request.
  Triggers critic, критик, /critic, review this document, review this result, review this plan.
  Do not auto-invoke. Not for inline critique, PR/diff code review, incident RCA, or post-execution QA.
metadata:
  scope: public
  author: Jlosev
  version: "2.0.1"
  tags: "{critic,orchestrator,review,research,planning}"
created: 2026-07-08
updated: 2026-09-03
user-invocable: true
---

# Critic – artifact adversarial review orchestrator

The parent agent **does not critique the artifact itself**. On **manual** start it dispatches an isolated Opus 5 subagent, applies structured criticism, and revises the document until handoff.

`{SKILL_DIR}` = directory of this SKILL.md. All skill paths are relative to `{SKILL_DIR}`.

## Preconditions

- [ ] Artifact available – a file **or** a full snapshot (Cursor Plan Mode / draft in chat). See `references/artifact-types.md`.
- [ ] `{ARTIFACT_TYPE}` set (fallback – `work-artifact`).
- [ ] `{ORIGINAL_REQUEST}` available from the session; if lost – ask the user, do not dispatch.
- [ ] `{SKILL_DIR}/agents/critic.md` and `{SKILL_DIR}/references/critic-dispatch-template.md` exist.
- [ ] `Task` (or equivalent subagent dispatch) is available; else Hard Stop.

## Scope

In: any finished work result before action / publish / writeback – plan, research, investigation, strategy/OKR, spec/PRD, design doc, wiki/chat draft, meeting synthesis, memo, report (except recurring status/period reviews).  
Out: auto-invoke without an explicit phrase/yes; inline critique by the parent; PR/diff code review; post-incident RCA; period/status digest; eval runs  
Fallback: no Task/subagent – Hard Stop, do not proceed to the action

**Invocation:** **manual only**. An optional project reminder rule may ASK; without yes do not dispatch.

## Gotchas

- The subagent **does not see** chat history – pass `{ORIGINAL_REQUEST}`, `{ARTIFACT_CONTENT}`, `{GOAL_FROM_ARTIFACT}` in the prompt (`references/critic-dispatch-template.md`).
- Do not mix with PR/diff review or an incident-RCA critic.
- Cursor Plan Mode often **does not** save a file – a full-text snapshot in `{ARTIFACT_CONTENT}` is required.
- **Critic model is Opus 5.** Before `Task` read `model` from `{SKILL_DIR}/agents/critic.md` and pass it. Do not substitute a cheap default.
- A critique phase inside another research skill ≠ this skill.
- **Do not patch** producer skills just to add a gate.
- For `research-conclusion`: unread source listed in Open Questions + an immediate action with owner/deadline/DoD may be **Accepted residual** in round ≥2.
- **Breadth vs summary:** a wide research/strategy body is not a finding; Executive Summary / Conclusions / Recommendations must be on-goal to `{ORIGINAL_REQUEST}`.
- **Anti-water:** on Conciseness findings the orchestrator **cuts/compresses**; suggested fix = what to delete.

## Algorithm

### Step 1: Detect the artifact

1. Entry: explicit user phrase **or** yes on a reminder ASK. Otherwise do not start the cycle.
2. Set `{ARTIFACT_TYPE}` and `{ARTIFACT_PATH}` (file or `cursor-plan-mode/...` / `ephemeral/...`).
3. Get full `{ARTIFACT_CONTENT}` – `Read` or a Plan Mode / chat snapshot.
4. Extract `{GOAL_FROM_ARTIFACT}` – Goal / research question / conclusion in one sentence.
5. Lock `{ORIGINAL_REQUEST}` – the user's task (or ask if context is gone).
6. If the file already has `## Artifact Review Log` with PASS for this same content – do not duplicate the round.

### Step 1b: Confirm (if no consent yet)

1. **Explicit phrase** = consent → Step 2.
2. **Yes** on a reminder ASK = consent → Step 2.
3. Else **ask once**: run critic for `{ARTIFACT_PATH}` (`{ARTIFACT_TYPE}`)?
4. **No** → do not dispatch; finish without critique (not a Hard Stop).

### Step 2: Dispatch the isolated critic

1. Read `{SKILL_DIR}/agents/critic.md` – take `model` from frontmatter (canon – `claude-opus-5-thinking-high`).
2. Fill `{SKILL_DIR}/references/critic-dispatch-template.md`.
3. Call **only** via `Task`:

```json
{
  "subagent_type": "generalPurpose",
  "model": "claude-opus-5-thinking-high",
  "readonly": true,
  "run_in_background": false,
  "description": "Adversarial critique",
  "prompt": "<filled critic-dispatch-template>"
}
```

4. **Hard Stop** – do not go to execution until Task returned a structured report.

### Step 3: Apply criticism

1. Sort Critical → Important → Minor.
2. For each Critical/Important – edit the artifact or return a revised block for ephemeral/cursor-plan.
3. If Critical remain – repeat Step 2 (rounds ≤ 3).
4. On Verdict **PASS** with residual Important (≤2 per gate) – apply them **in the same turn** before finalizing the Review Log.
5. Add / update `## Artifact Review Log` (in the file) or a chat summary (ephemeral).

### Step 4: Handoff gate

1. Verdict gate in `references/critique-rubric.md`: **PASS** – zero Critical, ≤2 Important, ≤2 Minor, all rubric scores ≥4; **REVISE** – ≥1 Critical, ≥3 Important, or any score ≤2.
2. Handoff only on **PASS** or after edits + a PASS re-round. Open Critical – stop.
3. Tell the user a short review summary and the path/summary of the updated artifact.
4. Only after PASS – the next step by type (execution, writeback, publish – see `artifact-types.md`).

## Hard Stop Rules

- **No silent run** – no `Task` without yes / an explicit phrase.
- **No inline critique** – parent does not score the artifact; only `Task` with `{SKILL_DIR}/agents/critic.md`.
- **No `{ORIGINAL_REQUEST}` in the prompt** – stop.
- **Critical or ≥3 Important without edits** – stop handoff.
- **Verdict REVISE** – stop handoff until a re-round or explicit user ack.
- **>3 rounds with repeating Critical** – stop, escalate.
- **Empty or truncated `{ARTIFACT_CONTENT}`** – stop; snapshot Plan Mode first.
- **`model`** – only from the agent frontmatter (`claude-opus-5-thinking-high`).

## Definition of Done

- [ ] Artifact fixed (file or full snapshot) with `{ARTIFACT_TYPE}`
- [ ] Consent received (phrase or yes)
- [ ] Critic called via `Task` on Opus 5, not inline
- [ ] Structured report received
- [ ] All Critical/Important handled (fixed or explicitly accepted)
- [ ] Review Log in the file or chat summary
- [ ] Verdict PASS (or REVISE handled)
- [ ] User sees a summary before execution handoff

## Example

**In A:** `Research/Plans/2026-07-08-retry-fix.md`. User: «review this plan». Type = implementation-plan.

**In B:** spec / design draft. User: «critic». Type = product-spec / design-doc / work-artifact.

**In C:** Cursor Plan Mode finished; yes on ASK. Path = `cursor-plan-mode/retry`.

**Result fragment:**

```markdown
# Critique Report
**Verdict:** REVISE
### Critical
| 1 | L28 / §Step 2 | No idempotency check on retry | «add retry» with no limit | set max retries + backoff |
```

## Check commands

```bash
SKILL_DIR="<path-to-this-skill>"
grep -E '^## (Hard Stop Rules|Definition of Done|Scope|Gotchas|Algorithm|Example)' "$SKILL_DIR/SKILL.md"
test -f "$SKILL_DIR/agents/critic.md"
test -f "$SKILL_DIR/references/critic-dispatch-template.md"
test -f "$SKILL_DIR/references/critique-rubric.md"
test -f "$SKILL_DIR/references/artifact-types.md"
grep -q 'claude-opus-5-thinking-high' "$SKILL_DIR/agents/critic.md"
grep -q 'readonly: true' "$SKILL_DIR/agents/critic.md"
```
