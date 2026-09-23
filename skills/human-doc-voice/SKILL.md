---
name: human-doc-voice
description: >
  Human-doc pass for any text a person will read to understand or act.
  Genre and folder do not decide. Triggers human-doc-voice, human doc,
  anti-agent-voice, LLM slop, too long, make it readable, polish document.
  Not for chat, agent scratch (log, .tmp, agent-notes), or code.
  Apply immediately. Keep facts. No approval wait.
metadata:
  scope: public
  author: Jlosev
  version: "1.7.0"
  tags: "human-doc,readability,dedup,slop"
created: 2026-07-28
updated: 2026-09-23
user-invocable: true
argument-hint: "[path]"
allowed-tools: Read, Edit, Write, Bash
---

# human-doc-voice

Make a text a person will read understandable: same meaning, shorter, no LLM slop.  
**Behavior SoT is this SKILL.** A project reminder rule only says when to call it.

`{SKILL_DIR}` = directory of this SKILL.md.

Content can be anything: a decision, a metric, an instruction, a write-up, an agreement. Rules below do not assume a document shape.

## Scope

| In | Out |
| --- | --- |
| Text a person will read to understand or act | Chat, thread, DM, status – use a voice skill if you have one |
| Prose in `.md`, a wiki page, a ticket, a Canvas string the person sees | Agent scratch: `log.md`, `.tmp`, `agent-notes`, raw transcript |
| Form: facts, density, duplication, slop | Code, imports, numbers as data |

**Test:** will a person read this to understand or take a step? Yes → this skill. Genre and folder do not matter.

**Publish** is a separate project rule. This skill does not send anything.

**Fallback:** invoked with no path and no file in hand → ask which file. A change that would alter a fact → keep the source wording and name it in the report. Do not stop for approval.

## Preconditions

- [ ] Polishing a file: path from `$ARGUMENTS` or the file being written. Canvas often lives in Cursor `canvases/` – use an absolute path
- [ ] Composing: write the new text to this contract; no separate detect pass
- [ ] `{SKILL_DIR}/scripts/check.sh` is available

## Contract

### 0. Mode (CRITICAL)

**Apply immediately.** Edit the file. Do not return a flag table and wait.

Leave a fragment that is already clear. Do not rewrite every heading or caption «just in case».

After a local fix, run the same pattern over the whole text.

**Not imported:** em-dash ban, «kill all adverbs», blog personality, forced «you». En dash «–» (U+2013) is fine; em dash (U+2014) is not.

### 1. Priority

If rules conflict: do not distort meaning → the reader can understand or act → be short → the rest.

### 2. Register

Text for a person. Not a leadership-report template and not chat.

Cut chat softeners («пж», «на всякий», «если коротко») and fake liveliness (a domestic metaphor instead of a fact, an aphoristic ending, a heading that is only a reply).

Keep the domain word. Do not translate a team term into a «neutral» synonym.

Name who acts. Imperative «you» only when the text is an instruction to that reader. Otherwise the subject is whoever does the action – a person, a service, a tool – not a forced address and not an impersonal verb.

| Pattern | Not OK | OK |
| --- | --- | --- |
| Passive where there is a subject | «дельта пересчитывается в серверные единицы» | «калькулятор переводит дельту в серверные единицы» |
| Infinitive instead of an actor | «Пакет передайте лиду: сверить, уточнить» | «Пакет передайте лиду – он сверит цифры и уточнит» |
| Dash or colon instead of a conjunction | «Если она не пустая – учтите объём» | «Если она не пустая, учтите объём» |
| Nominalization instead of a verb | «это вход в расчёт на шаге 5» | «понадобится на шаге 5» |
| Root repeated in one phrase | «домен скрывает объекты без домена» | «фильтр домена отбрасывает объекты без разметки» |

Read-aloud test: if you stumble, a conjunction is missing or the subject is hidden.

### 3. Facts (CRITICAL)

Modality, a part of a number (year, unit), negation, scope, and a list stay as in the source. «Пробуем» does not become «делаем». Silence in the source stays silence.

Do not invent an owner, a date, or a decision. Mark the gap in the text, short and in place.

An evaluative word only next to a fact. Do not rename a metric. Example, not a special section: a share of 4–5 ratings is not NPS unless that is the instrument.

A qualifier stays only if without it a fact is misread. Otherwise cut. Example: «non-representative sample» with no gloss either becomes a plain limit («цифры про ответивших») or goes.

### 4. Reader

The point is at the top of the text and at the top of a section. Someone who stops early still leaves with a whole answer, just a shorter one.

A heading names what is in the section, without knowing how the text was assembled. A questionnaire code in a heading is one example, not the only case.

No assembly kitchen in the reader-facing body: how the text was merged, question codes, run labels, «a separate section is not needed». `fill rate` and `Q4` are examples of that class, not the full ban list.

The text does not narrate its own history. No sections «что выяснили» or «по итогам обсуждения». A live agreement («со смежниками согласовано: делаем так») stays – that is a fact, not a diary.

Out of scope is a link to where that scope is described, not a section «не делаем». A boundary that is itself a fact («остальные отступы не трогаем») stays.

### 5. One fact, one place (CRITICAL)

The same fact in two places is a duplicate, whatever the form: paragraph, list, table, caption, example. A step / FAQ / roles table is one case of this, not a required outline.

The fact stays where the reader hits it. Other hits – delete or, if the explanation is longer than a line, one pointer. At most one pointer per fact. Dedup does not delete the fact: one place, not zero.

One entity, one name – the name the reader already uses.

A caption or sentence that only restates the heading or the neighboring number – delete.

**Patch of a live page:** read the finished page, including blocks you did not touch.

What you cut goes to «Не вошло» in the report, with where it still lives (source, another section, a link). Nothing disappears silently.

### 6. Slop (CRITICAL)

Empty wrappers and stock phrases – `scripts/lexicon.txt`. Replace with the fact, or cut. Do not ban modality words («может», «должен», «согласовано»): those are facts to preserve.

Three or more bold spans in one paragraph means nothing is emphasized. Thin them. Monospace only for what the reader will copy literally (field, method, command, path). A service or product name is ordinary text.

**A tic is frequency, not the construction.** Once or twice can be the author; in every paragraph it is a generator. Thresholds: `scripts/tics.py`.

| Tic | Threshold | Fix |
| --- | --- | --- |
| Antithesis «X, not Y» and «не только … но и» | >3 | Keep where the contrast is the point. Else say the point |
| «Значит / Поэтому / Отсюда / то есть» at sentence start | >4 | Drop the linker |
| Label-colon «Есть: … Нет: …» | >3 | Same register in every item, or nowhere |
| Same tail on list items | >3 | Collapse into a table |
| Same rhythm in every section (fact → moral) | all sections | Leave some sections without a moral |

Compression test, not a length quota: what can leave so the reader will not notice? There is no «cut in half» target.

### 7. Self-check

Before the report, find and fix:

- a sentence that would fit a document about another system, unchanged
- a sentence that holds by rhythm and has no fact
- a verb that needs a human subject, with no human there

### 8. Surfaces

Same checks on every string a person sees, including Canvas headings, captions, callouts, table headers, footer. No separate voice for Canvas. Do not touch numbers, imports, logic, or `cursor/canvas`.

## Algorithm

1. Composing from material: write from what the reader needs, not from the source’s phrasing. Then check numbers, names, modality, negation, and scope against the source – compression loses them first.
2. Polishing a path: read it, run the check commands, edit in place. Clear fragments stay.
3. A local fix → the same pattern over the whole text.
4. Run `check.sh` again.
5. Report in chat. Do not wait.

```
## Отчёт
- короче: <словами, или «объём почти тот же»>
- не вошло: <2–3 куска и где лежат>
- спорное: <одно решение, если мог ошибиться>
```

A line with nothing to say is omitted. Do not narrate the steps.

## Hard Stop Rules

- Do not upgrade modality, drop part of a number, flip a negation, or widen a scope.
- Do not invent an owner, a date, or a decision. Mark the gap.
- Dedup leaves the fact in exactly one place, not zero. Cuts are listed in «Не вошло».
- Do not copy this contract into `.mdc` or other files.
- Do not publish. A project publish rule is separate.
- Do not blanket-rewrite a clear fragment.
- Do not translate a domain term.
- Do not add an owner or a «lead» block the source does not have.
- `check.sh` – once before edits and once at the end. Not after every edit.

## References

Scan hints, not a genre and not an approval gate.

| File | Purpose |
| --- | --- |
| `references/ai-writing-tells-checklist.md` | Wikipedia / humanizer tells – content, language, chatbot |
| `references/structural-tells.md` | Structures: not-X-but-Y, rule-of-three, metronomic rhythm |
| `scripts/lexicon.txt` | Empty Russian wrappers. Not a ban on modality. `check.sh` runs `lexicon_scan.py`, `emphasis_scan.py`, `repeats.py`, `tics.py` |

## Definition of Done

- [ ] File edited; clear fragments left alone
- [ ] `check.sh` at the end; leftover hits are intentional and named in «спорное»
- [ ] Each fact in one place; modality and numbers match the source
- [ ] Headings name the content; a qualifier is needed or gone
- [ ] Report delivered; no wait for «ok»
- [ ] Nothing published by this skill

## Example

Examples of the checks, not a required document type.

**In.** A fragment a person will read:

> Важно отметить, что дельта пересчитывается в серверные единицы. Дельта переводится в серверные единицы на шаге 5.

**Out.** Same fact, one place, actor named, empty wrapper gone:

> На шаге 5 калькулятор переводит дельту в серверные единицы.

**Report.** короче на треть. не вошло: повтор про шаг 5. спорное: нет.

## Gotchas

- Repeat scan skips tables, code, and quotes after `**Было:**` – check those by eye.
- Punctuation-linker scan is noisy on definitions – a hint, not an edit list.
- Lexicon hits inside a real term or a quote – leave them and say so in «спорное».
- One-off HTML export does not update itself – re-export after copy changes (`canvas-to-html`).

## Check commands

```bash
"{SKILL_DIR}/scripts/check.sh" "<path>"
test -x "{SKILL_DIR}/scripts/check.sh"
```
