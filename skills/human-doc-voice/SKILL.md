---
name: human-doc-voice
description: >
  Human-doc pass for outbound artifacts (strategy, wiki draft, live-page patch,
  report for leads, demo Canvas). Triggers /human-doc-voice, human doc, anti-agent-voice,
  ready for leads, for sending, publish draft, check redundancy and duplication.
  Not for internal WIP/research for yourself and not for chat messages.
  Form only – tone, density, dedup; fix mismatches, do not rewrite everything.
metadata:
  scope: public
  author: Jlosev
  version: "1.5.1"
  tags: "human-doc,publish,readability,dedup"
created: 2026-07-28
updated: 2026-09-03
user-invocable: true
argument-hint: "[path.md | path.canvas.tsx]"
allowed-tools: Read, Edit, Write, Bash, AskUserQuestion
---

# human-doc-voice

Make an outbound document read like a human PM wrote it: formal report tone, no agent-meta, no LLM slop.  
**Behavior SoT is this SKILL.** A project reminder rule is optional.

`{SKILL_DIR}` = directory of this SKILL.md.

## Scope

| In | Out |
| --- | --- |
| `.md` for leads / wiki draft / live-page patch / publish | Internal research, exploration, `.tmp` |
| User-facing strings in a demo Canvas (`.canvas.tsx`) | Canvas without a demo goal; React refactors |
| Form (lead, prose, captions, anti-agent-meta) | Changing meaning of bets / decisions / numbers without confirm |

**Chat / messenger drafts:** use a dedicated voice skill if you have one – not this.  
**Fallback:** path unclear → ask; meaning disputed after rewrite → show diff and ask. Do not publish.

## Preconditions

- [ ] Path to `.md` / `.canvas.tsx` (from `$ARGUMENTS` or a question). Canvas often lives in Cursor `canvases/` – need an absolute path
- [ ] Intent = outbound / demo (or explicit `/human-doc-voice`)
- [ ] `{SKILL_DIR}/scripts/check.sh` is available

## Contract

### 0. Mode (CRITICAL)

**Goal – find and fix** where the language fails the contract.  
**Not the goal – rewrite everything.** If a fragment is already fine (e.g. «Главный вывод»), leave it.

After targeted edits from user comments – **run the whole document** for the same error pattern (not only the highlighted fragment).

Antipattern: «must rewrite every Caption/Callout» → excess, ruins good text.

### 1. Tone: formal report, not personal chat

Report for leads / teams: businesslike, dense.  
No conversational slang, no «as if over coffee».

| OK | Not OK |
| --- | --- |
| Главный вывод · TL;DR · Итоги | Если коротко · Собрал … · реально страдают / больно |
| Сегменты с низкими оценками | Кому хуже всего |
| Свободная обратная связь | Свободный текст и блок «…» |
| Насколько продукты известны | Кто знает какие продукты |

Do not copy chat softeners («пж», «на всякий»).

### 2. Headings name the content

H1/H2 must answer «what is in this section?», not survey mechanics or internal assembly slang.  
If a heading is unclear without knowing the questionnaire – rephrase.

### 3. Disclaimers: clear payoff or delete (CRITICAL)

A methodology / disclaimer sentence is allowed **only** if without it a number misleads.

| Action | When |
| --- | --- |
| Keep short | Needed to interpret a number («Speed – DWH only») |
| Delete | Unclear why; sounds like «do not trust the results»; duplicates a heading/table |
| Rewrite | There is meaning, but jargon («non-representative sample», «long paths») |

The reader must not wonder: «does this mean we cannot trust the survey?»

### 4. Anti-agent-meta + anti-kitchen

Forbidden in reader-facing body:

- agent-meta: `влито`, `gap → must`, `residual`, session src, Artifact Review Log, «merge X × Y», `keyword-кластер`, `fill rate`, `verbatim`, `baseline`/`friction` as labels, `Q4`/`Q9` codes in UI
- analyst kitchen: «long paths», «wave figure», «we are not inflating», «a separate section is not needed», «we look at that over there…», «masks the group» without decoding
- meta about document structure instead of a fact about the data

### 5. Anti-slop + anti-padding (CRITICAL)

**Fix / ban:** «паттерн», «кластер», «охват метрик», «сигнал волны», «когорта», «сходимость», «Mean», «n=» as decoration, bureaucratic glue, empty connectors.

**CSAT** – OK as a metric name if expanded once («share of 4–5 ratings»).

**NPS:** check the target metric definition before banning the word. Do not call a satisfaction share (4–5) «NPS». Do not promise a «comparable NPS» by rescaling to 0–10 unless that is the actual instrument. If the team uses a custom scale, name whose canon it is.

**Hard antipattern:** inflate a caption when the heading or numbers already carry the meaning.

Rule: every sentence in a Caption = a fact or a necessary qualifier. Otherwise cut.  
A caption that only restates the neighboring Stat/heading – delete.

**Syntax is the main source of «AI» sound.** Clean lexicon still reads machine-like if sentences are impersonal, glued with punctuation, and hung on nominalizations.

| Pattern | Not OK | OK |
| --- | --- | --- |
| Impersonal 3rd person where there is a reader | «считают и заказывают по юниту» | «считайте и заказывайте по юниту» |
| Infinitive instead of an actor | «Пакет передайте лиду: сверить, уточнить» | «Пакет передайте лиду – он сверит цифры и уточнит» |
| Passive where there is a subject | «дельта пересчитывается в серверные единицы» | «калькулятор переводит дельту в серверные единицы» |
| Dash and colon instead of a conjunction | «Если она не пустая – учтите объём» | «Если она не пустая, учтите объём» |
| Nominalization instead of a verb | «это вход в расчёт на шаге 5» | «понадобится на шаге 5» |
| Root repeated in one phrase | «домен скрывает объекты без домена» | «фильтр домена отбрасывает объекты без разметки» |

Read-aloud test: if you stumble, a conjunction is missing or the subject is hidden.

**A tic is frequency, not the construction (CRITICAL).** Once or twice sounds like an author; in every paragraph – like a generator. Thresholds: `scripts/tics.py`.

| Tic | Threshold | Fix |
| --- | --- | --- |
| Antithesis «X, not Y» | >3 per document | Keep where the contrast is the point. Else affirmative |
| «Значит / Поэтому / Отсюда / то есть» at sentence start | >4 | Drop the linker – order already implies the conclusion |
| Label-colon «Есть: … Нет: …» | >3 | Same register in every item, or nowhere |
| Same tail on list items | >3 | Collapse into a table |
| Same rhythm in every section (numbers → moral) | all sections | Merge some morals, leave some sections without one |

### 6. Dedup: one fact – one place (CRITICAL)

Before language edits – inventory repeats: list key facts/terms and count explanations (`rg` + `check.sh`). The fact stays where the reader hits it in the scenario; other hits – delete or reduce to a pointer.

| Dup pattern | Fix |
| --- | --- |
| One rule in N places (step, callout, FAQ, roles table) | Full explanation at the first scenario hit; then a short reminder or nothing |
| Mechanics and «why» both repeated | Step = action, FAQ = reason; not both |
| Prose then a list of the same | Keep the action list + one-line lead-in |
| Table column with the same value in every row | Lift into the intro |
| Example duplicates a reference table | Example only has what the calculation needs |
| Caption restates heading or Stat | Delete (§5) |
| Same number in observations and again in the plan | Number stays in observations; plan = action without repeating it |
| Synonyms for one entity | One term per entity, as in the UI |

A pointer is OK if the explanation is longer than a line; else just drop the dup. At most one pointer per fact.

Do not introduce entities outside the document scope.

**Patch / diff to a live page:** read as a finished page, including untouched blocks. Dup between patch and old text is the most common leak.

### 7. Lead + ownership

Lead 2–4 short sentences: context + main point + who owns / what is out of the doc. No filler.

### 8. Canvas: what to touch

Walk user-facing strings (H1/H2, Caption, Callout, table headers, footer).  
**Edit only** what hits §1–6. Leave good text alone.

Do not touch: numbers, imports, logic, `cursor/canvas`.

## Algorithm

1. Path from `$ARGUMENTS` or ask. If the user wants an «unclear» document rewritten – first structure it for the reader's question, then voice. Do not polish assembly kitchen.
2. Baseline – `cp "<path>" ".tmp/human-doc-$(basename "<path>")"`.
3. Checklist + repeat scan – `{SKILL_DIR}/scripts/check.sh "<path>"` (again only after user-comment edits and in DoD, not after every Edit).
4. **Dedup pass** (§6): read as a reader – for a patch, together with the live page.
5. Language audit → targeted contract edits (not a blanket rewrite).
6. If edits came from user comments – **full pass** of the document for the same pattern.
7. Show **what changed**: removed dups as «dup / before / after»; other edits as before→after only. State that meaning is intact.  
   **HARD STOP:** language accepted only after «ok» / «согласовано».
8. External publish (wiki / CMS) – only after an explicit «publish».

## Hard Stop Rules

- Do not change meaning (bets, numbers, owners, decisions) without explicit confirm.
- Do not run the skill on internal WIP/research «for myself» without explicit `/human-doc-voice`.
- Do not copy this SKILL contract into `.mdc` / other files.
- Do not publish externally without user confirm.
- Do not blanket-rewrite «just in case».
- If the skill was called because of **new** sections: fix your own text. `check.sh` flags on lines outside the diff – show the user, do not silent-edit.
- Do not slide a formal report into a personal/chat tone.
- Do not leave a disclaimer the reader cannot understand on the first read.
- Dedup ≠ deleting the fact: it must remain in exactly one place, not zero.
- `check.sh` – once on baseline (step 3) and once in DoD. Not after every Edit.

## Definition of Done

- [ ] `check.sh` ran; heuristic agent-meta / slop / chatty / kitchen markers clean or left on purpose
- [ ] Dedup: each fact explained in one place
- [ ] Headings clear without questionnaire knowledge; disclaimers clear or gone
- [ ] Lead readable in ~60s; no padded captions
- [ ] Shown dups and before→after **only for changed** spots; language «ok»
- [ ] External publish not done without «publish»

## Example

**In:** `/human-doc-voice report.canvas.tsx`  
**Bad:** «non-representative sample» with no gloss; «Who knows which products»; caption about «long paths»; «a separate section is not needed».  
**Good:** drop the disclaimer or «figures are about respondents»; «How well-known the products are»; «Org blocks come from the Department field; tiny groups hidden»; fact without structure-meta.

**Dedup case:** «then order via the usual process» in 5 places – kept in the roles table and the last step; «why we count by services» in the step and FAQ – kept in FAQ, pointer in the step.

## Gotchas

- Repeat scan skips tables, code, and quotes after `**Было:**` – check those by eye.
- Punctuation-linker scan is noisy on definitions and captions – a reading hint, not an edit list.
- One-off HTML export does **not** update itself – re-export after copy changes (`canvas-to-html`).

## Check commands

```bash
"{SKILL_DIR}/scripts/check.sh" "<path>"
python3 "{SKILL_DIR}/scripts/repeats.py" "<path>"
python3 "{SKILL_DIR}/scripts/tics.py" "<path>"
test -x "{SKILL_DIR}/scripts/check.sh"
```
