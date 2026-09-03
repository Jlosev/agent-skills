---
created: 2026-09-03
updated: 2026-09-03
---

# System Prompt Quality Guide

Стандарт для SKILL.md, agent .md, CLAUDE.md, protocols.
Rules for Rules + Anthropic skill-creator + a publication DoD
+ eight LLM quality criteria (clarity, structure, self_containment, safety, preconditions, agent_agnostic, examples, self_improvement).

---

## Principles

| # | Rule | Why |
|---|------|-----|
| 1 | Signal-to-noise | каждый токен меняет поведение |
| 2 | Why over What | «X потому что Y» > MUST; CRITICAL только для safety |
| 3 | Verifiable | completion check на каждую инструкцию |
| 4 | Instructions first | static → dynamic (cache) |
| 5 | Positive framing | «Do Y» > «Don't X» |
| 6 | Graduated examples | 0/1/2-3/3-5 по сложности |
| 7 | Scope clarity | in / out / fallback |
| 8 | Progressive disclosure | core в body; conditional ≥30 строк → `references/` |
| 9 | One delimiter | Markdown XOR XML |
| 10 | Deterministic Offloading | Если есть жёсткая последовательность команд (CLI, парсинг), вынеси её в bash/python скрипт в `scripts/`. Не заставляй модель оркестрировать рутинные вызовы. |

## Compression

| Remove | → |
|--------|---|
| please, make sure to, CoT phrases | delete |
| prose lists | bullets/tables |
| passive voice | imperative |
| ALL CAPS | `**bold**` |
| цепочка 3+ shell-вызовов в Алгоритме | скрипт `scripts/script.sh` и один вызов |

---

## Publication DoD

Gate перед публикацией скилла. Severity: critical = блок, major = fix до публикации, minor = рекомендация.

### Frontmatter

| Критерий | Sev | Check |
|----------|-----|-------|
| `name` kebab-case `^[a-z0-9][a-z0-9_-]{0,63}$` | critical | = имя директории |
| `metadata.scope/author/version` | major | блок `metadata:`; `scope: public` для кросс-доменных скиллов, default `repo` – только с доступом к source-репо |
| `metadata.team` | minor | Prod |
| контекст ≥30 строк → `references/` | major | |
| логика → `scripts/` + упоминание в body | minor | |

### Discovery

| Критерий | Sev | Check |
|----------|-----|-------|
| **нет `:` в `description`** | critical | pre-commit gate |
| description ≤400 (hard ≤1024) | major/critical | >400 major, >1024 critical |
| when-to-invoke, не capabilities | major | |
| ≥3 trigger phrases | major | без метки «Триггеры:» |
| negative triggers | major | «Не используй для…» |
| контекст применения | minor | |

### Body

| Критерий | Sev | Check |
|----------|-----|-------|
| ≤300 строк (target 60–150) | major | >500 critical |
| single responsibility | major | |
| назначение 1–3 строки после H1 | major | |
| `## Алгоритм` или `## Шаг N` | critical | |
| `## Hard Stop Rules` | critical | |
| `## Definition of Done` | critical | |
| `## Команды проверки` | major | |
| `## Gotchas`, `## Scope` | major | |
| IMPORTANT/YOU MUST ≤3 | minor | |
| ≥1 usage example (вход → результат) | major | quality `examples` |
| preconditions block (доступы/файлы до шагов) | major | quality `preconditions` |
| agent-agnostic language | minor | quality `agent_agnostic` |
| self-improvement / post-run retro | minor | quality `self_improvement` |
| no hidden skill deps без fallback | major | quality `self_containment` |

### Safety

| Критерий | Sev | Check |
|----------|-----|-------|
| секреты, токены, PII | critical | |
| абсолютные пути `/Users/…` | major | placeholders |
| ФИО в output-шаблонах | major | роли |
| destructive ops без ack | major | |
| `references/*`, `scripts/*` существуют | minor | |

### Testing (Prod)

| Критерий | Sev | Check |
|----------|-----|-------|
| `evals/evals.json` ≥3 кейса | minor (optional) | |
| should-trigger ≥3 | major | |
| should-not-trigger ≥2 | major | |

---

## Skill quality criteria

Субъективные критерии LLM-оценки (`quality_score`). Severity для lint-отчёта.
Weights below are a local heuristic for the lint report.

| Критерий | Вес | Sev | Check |
|----------|-----|-----|-------|
| `clarity` | 0.20 | major | description = when-to-invoke + ≥3 trigger phrases + negative triggers |
| `structure` | 0.15 | major | алгоритм, actionability шагов, output format |
| `self_containment` | 0.15 | major | нет «сначала вызови skill-X» без fallback; conditional → `references/` |
| `safety` | 0.15 | critical | секреты, destructive/mass ops без ack, prod без guardrails |
| `preconditions` | 0.10 | major | явная проверка доступов/зависимостей/файлов **до** основных шагов |
| `agent_agnostic` | 0.10 | minor | нет привязки к Claude/Codex/Cursor без generic fallback |
| `examples` | 0.10 | major | ≥1 пример: вход (prompt/контекст) → ожидаемый результат |
| `self_improvement` | 0.05 | minor | post-run: Gardener / «что улучшить в скилле» / retro-шаг |

---

## Checklist by Type

Применяй секцию по типу файла **после** Publication DoD.

### SKILL.md (дополнительно к DoD)

- [ ] Output format указан
- [ ] ≥1 example (prompt → expected output)
- [ ] Preconditions: проверка доступов/файлов до шагов
- [ ] Self-containment: нет обязательных внешних скиллов без fallback
- [ ] Agent-agnostic: нет Claude-only без generic альтернативы
- [ ] Self-improvement: post-run retro (Gardener или аналог)
- [ ] `allowed-tools` – только нужные
- [ ] conditional branches в `references/`, не inline
- [ ] stateful → log/config для persistence

### Agent .md

- [ ] frontmatter: `name` + `description` + `tools`
- [ ] description = when to delegate
- [ ] numbered algorithm + rules; lean, no parent duplication

### CLAUDE.md

- [ ] project-specific only; commands/workflows; gotchas
- [ ] constraints в одной секции (CRITICAL > MANDATORY > RECOMMENDED)

### Protocol .md

- [ ] trigger + ordered steps + success criteria; idempotent

---

## Workflow Enforcement Patterns

Проверять при lint **stateful / multi-step / AskQuestion** скиллов (не требовать от одношаговых CLI-хелперов).

| Pattern | Sev | Check / Fix |
| --- | --- | --- |
| Named failure modes | major (stateful) | есть ≥2 явных «failure mode = X → stop/fix»; иначе → добавить таблицу |
| STOP before mutate/artifact | major | перед Write destructive / финальным артефактом есть STOP + wait user или script gate |
| Escape hatch с partial resistance | minor | если есть skip/«просто сделай» – 1-й skip ≠ full abort критичных фаз |
| Progressive disclosure | major | conditional ≥30 строк или phase>1 → `phases/`/`references/`; body = skeleton + «Read before execute» |
| Section / phase self-check | minor (multi-phase) | перед DONE – confirm Read нужных phase/section файлов |
| Completion vocabulary | minor | `DONE` / `DONE_WITH_CONCERNS` / `BLOCKED` / `NEEDS_CONTEXT` вместо только «готово» |
| One-question-per-turn (conversational) | major (diag/discovery) | не батчить forcing-вопросы; pipeline batch AskQuestion – OK |
| Mandatory alternatives before big rec | major (design/strategy) | ≥2 подхода + явный выбор до финального doc |
| Behavioral exemplars | minor | BAD/GOOD или anti-sycophancy на ключевых развилках (не обязательно для pipeline) |
| Mechanical DoD where possible | major | жёсткие CLI-цепочки → `scripts/` + exit-code gate (Principle 10; связать с failure modes) |

---

## Anti-patterns

| Pattern | Fix |
|---------|-----|
| CoT / boilerplate / vague | sections / delete / measurable criteria |
| LLM-оркестрация рутины | заменить 3+ команды на вызов скрипта из `scripts/` |
| negatives in body | positive rewrite |
| mixed delimiters | one format |
| MUST scattered | consolidate Constraints |
| description = internals | when-to-invoke + triggers + skip |
| `:` in description | comma-separated triggers |
| missing DoD sections | add Hard Stop / DoD / Команды |
| body >300 | extract to references |
| IMPORTANT >3 | → Hard Stop Rules |
| unconditional steps in references | keep in body (extra read cost) |
| «сначала /skill-X» без fallback | self_containment: inline fallback или references |
| нет примеров | добавить ## Пример с входом и результатом |
| Claude-only / Codex-only | agent_agnostic: generic формулировка |
| шаги без проверки prereqs | preconditions block перед алгоритмом |
| нет post-run retro | self_improvement: Gardener / «что улучшить» |
| hardcoded paths без verify | major: «проверь существование пути» |
| Recommend in prose and continue past STOP | STOP + tool AskQuestion / wait |
| Skip validation because user said «оставь» | показать контекст → потом skip_all |
| «Скилл завершён» без DoD/script exit 0 | completion status + verify |
| Load all phases into context at start | Gatekeeper: Read one phase |
| Soft skip of premise/alternatives on «fully formed plan» | keep critical phases; skip only questioning |

---

## Template (SKILL.md)

```yaml
---
name: {kebab-case}
description: >
  Используй когда {when}. Триггерные фразы {p1}, {p2}, {p3}.
  Не используй для {anti}.
metadata: {scope: public, author: {team}, version: "1.0.0"}
---
# Title
{1-2 lines purpose}
## Preconditions          # опционально, если есть зависимости
## Алгоритм / ## Hard Stop Rules / ## Definition of Done
## Пример                  # ≥1 сценарий: вход → результат
## Команды проверки / ## Gotchas / ## Scope
```
