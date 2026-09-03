---
created: 2026-07-08
updated: 2026-08-20
metadata:
  scope: public
  author: Jlosev
  version: "2.0.0"
---

# Artifact types – critic

Оркестратор классифицирует артефакт **до** dispatch. Тип влияет на акценты критика, не на pipeline.

## Когда предлагать / запускать

**Manual skill:** явная фраза (`критик`, `/critic`, `проверь документ`, `проверь результат`, `проверь план`) = согласие → полный цикл SKILL.

Типичные артефакты (для классификации, не для auto-invoke):

- любой законченный результат работы: план, выводы, spec, design doc, черновик wiki/чата, синтез встречи, memo;
- markdown в рабочих папках проекта (`Research/`, `docs/`, `.cursor/plans/`, `~/.cursor/plans/`);
- Cursor Plan Mode / CreatePlan (файл или UI-only snapshot);
- итог writing-plans, deep-research, product-discovery и аналоги.

**Не кандидаты:** регулярные status/period-отчёты, опубликованный wiki-архив, index/stub страницы, PR/diff, post-incident RCA.

**Hooks offline:** `plan-critic-*.sh` не в `.cursor/hooks.json`. Не полагайся на stop follow-up.

## Типы артефактов

| `{ARTIFACT_TYPE}` | Признаки | Источники (примеры) | Акцент критика |
|-------------------|----------|---------------------|----------------|
| `implementation-plan` | Шаги, файлы, команды, DoD на task | `Research/Plans/`, writing-plans | Исполнимость, порядок, YAGNI, anti-water |
| `cursor-plan` | Plan Mode, CreatePlan, tasks/checkboxes | `~/.cursor/plans/**`, workspace `.cursor/plans/**`, ephemeral UI plan | Полнота шагов, scope, missing deps |
| `research-conclusion` | Выводы, рекомендации, open questions | `Research/**`, deep-research, CustDev synth | Evidence, assumptions, actionability; **ширина тела OK, summary on-goal**; anti-water |
| `investigation-report` | Root cause, options, decision | triage, debug synth (не Period Review) | Correctness, missing checks, overclaim, anti-water |
| `strategy-draft` | Options, trade-offs, roadmap | `Strategy/**`, OKR draft | Goal alignment; тело шире OK, decision/summary строго по цели; anti-water |
| `product-spec` | PRD, требования, сценарии | `docs/` / spec draft | полнота vs запрос, YAGNI, placeholders, actionability |
| `design-doc` | архитектура, ADR-черновик | `Research/` / `docs/` design | correctness, альтернативы, missing risks, scope |
| `work-artifact` | любой другой законченный результат | memo, wiki/chat draft, синтез встречи, отчёт | goal alignment, placeholders, anti-water, actionability |

Если тип неочевиден – `work-artifact` + 1-line rationale в dispatch.

## Источник контента (`{ARTIFACT_PATH}`)

| Ситуация | `{ARTIFACT_PATH}` | Как получить `{ARTIFACT_CONTENT}` |
|----------|-------------------|-----------------------------------|
| Файл в проекте | полный путь | `Read` файла |
| Cursor Plan Mode / CreatePlan (файл) | `~/.cursor/plans/<file>.plan.md` или workspace `.cursor/plans/*.md` | `Read` |
| Cursor Plan Mode (только UI) | `cursor-plan-mode/<session-topic>` | snapshot из текущего плана в сессии – **обязателен полный текст** в prompt |
| Черновик в чате без файла | `ephemeral/<topic>` | скопировать итоговый блок в `{ARTIFACT_CONTENT}` |

**Hard Stop:** не диспатчить критика с пустым или усечённым `{ARTIFACT_CONTENT}`.

## Handoff после критики

| Тип | Типичный next step |
|-----|-------------------|
| `implementation-plan`, `cursor-plan` | execution, subagent-driven-development |
| `research-conclusion`, `investigation-report` | writeback в базу знаний, решение пользователю |
| `strategy-draft` | обсуждение, OKR/гейт, доработка |
| `product-spec`, `design-doc`, `work-artifact` | доработка → публикация / согласование / writeback |

Секция в артефакте после ревью: `## Artifact Review Log` (в файле) или summary в чате (ephemeral). Handoff – только при **PASS** по Verdict gate (`critique-rubric.md`).
