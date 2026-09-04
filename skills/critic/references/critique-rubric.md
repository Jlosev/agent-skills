---
created: 2026-07-08
updated: 2026-09-04
metadata:
  scope: public
  author: Jlosev
  version: "2.0.0"
---

# Critique rubric – critic

Субагент оценивает артефакт по **всем** измерениям. Score 1 (плохо) – 5 (отлично). Finding обязателен при score ≤ 3.

## Type modifiers (по `{ARTIFACT_TYPE}`)

| Тип | Дополнительные red flags |
|-----|--------------------------|
| `research-conclusion` | вывод без источника; неразличимы факт и гипотеза; нет open questions; рекомендации не actionable; **summary/выводы уехали от `{ORIGINAL_REQUEST}`** при том что тело может быть шире; вода в Executive Summary |
| `investigation-report` | root cause без evidence; не рассмотрены альтернативы; overclaim «точно причина»; повтор одних тезисов в RCA / options / decision |
| `cursor-plan` | пропущенные зависимости между tasks; нет критерия готовности; план не покрывает `{ORIGINAL_REQUEST}` |
| `strategy-draft` | опции без trade-offs; нет явного «что не делаем»; цели не привязаны к запросу; раздутый vision без сжатого decision block |
| `product-spec` | требования без критерия приёмки; сценарии без актёра; scope без «не делаем»; дубли с уже существующим продуктом/страницей |
| `design-doc` | решение без альтернатив; нет failure modes; несовместимость с принятыми DECISIONS; overclaim «единственно верно» |
| `work-artifact` | нет связи с `{ORIGINAL_REQUEST}`; нет следующего действия; вода в лиде; непроверяемые claims |
| `implementation-plan` | стандартные red flags ниже |

### Breadth vs summary (research / strategy)

**Ширина тела допустима.** Контекст, смежные темы, альтернативы, background – OK в теле документа, если помогают понять выводы.

**Summary не размывается.** Executive Summary / Выводы / Recommendations / Key findings должны бить в `{ORIGINAL_REQUEST}` и `{GOAL_FROM_PLAN}` без off-topic и без «размытия» цели широким контекстом.

| Сигнал | Severity |
|--------|----------|
| Широкое тело + summary строго по цели | **не finding** (Accepted as-is) |
| Summary включает off-topic / размывает цель | минимум **Important**; если цель неузнаваема – **Critical** |
| Тело раздуто водой без новой информации (см. §8) | по Conciseness |

---

## 1. Goal alignment

**Вопрос:** каждый шаг/вывод ведёт к `{ORIGINAL_REQUEST}` и `{GOAL_FROM_PLAN}`?

| Score | Критерий |
|-------|----------|
| 1 | Артефакт решает другую задачу или >30% off-topic **в summary / core path** |
| 3 | Есть отвлечения, но core path верный |
| 5 | Каждый шаг / ключевой вывод traceable к success criteria |

**Red flags:** шаги «на будущее», generic boilerplate, отсутствие явной связи шаг → outcome; для research – summary, который отвечает на другой вопрос, чем `{ORIGINAL_REQUEST}`.

**Не red flag:** широкий background / смежный контекст в теле research, если summary и recommendations остаются on-goal.

---

## 2. YAGNI / overhead

**Вопрос:** нет ли лишней работы, абстракций, ceremony?

| Score | Критерий |
|-------|----------|
| 1 | Значительный over-engineering vs задача |
| 3 | Есть лишние шаги, но не блокеры |
| 5 | Минимальный достаточный объём работы / текста |

**Red flags:** новые слои/фреймворки без обоснования, «сначала рефакторинг всего», eval/infra до MVP, дублирование существующих скриптов.

**Отличие от §8:** YAGNI – лишняя *работа/scope исполнения*; Conciseness – лишний *текст* без новой информации.

---

## 3. Correctness

**Вопрос:** технически верны ли допущения, порядок, зависимости?

| Score | Критерий |
|-------|----------|
| 1 | Неверный порядок, невозможные шаги, ложные предпосылки |
| 3 | Мелкие ошибки в деталях |
| 5 | Зависимости и assumptions корректны |

**Red flags:** step B before A with a hard dependency, wrong paths/tools, ignored Hard Stop rules, incompatibility with project constraints.

**Environment assumptions (orchestrator, not user):** finding «file/tool may be missing» – suggested fix = verify via Read/MCP; severity only if the artifact asserts something false. Do not suggest «ask the user» about fs/tools/URLs.

---

## 4. Optimization

**Вопрос:** можно ли достичь цели проще, быстрее, меньшим diff?

| Score | Критерий |
|-------|----------|
| 1 | Очевидно более короткий путь существует |
| 3 | Небольшие улучшения возможны |
| 5 | Путь уже near-optimal для scope |

**Red flags:** sequential вместо parallel где независимо, ручные шаги вместо существующих скиллов/скриптов, повторное чтение одних файлов, отсутствие batching.

---

## 5. Missing risks

**Вопрос:** какие failure modes не покрыты?

| Score | Критерий |
|-------|----------|
| 1 | Критические риски не упомянуты |
| 3 | Основные риски есть, edge cases нет |
| 5 | Риски + mitigation явно прописаны |

**Red flags:** нет rollback, нет проверки auth/MCP, нет pre-commit/hook constraints, нет «что если субагент упадёт», миграции без backup.

---

## 6. Placeholder detection

**Вопрос:** артефакт исполним / пригоден для решения без додумывания?

| Score | Критерий |
|-------|----------|
| 1 | Преобладают TODO/TBD/«и т.д.» |
| 3 | Единичные placeholders в некритичных местах |
| 5 | Все шаги конкретны (файл, команда, критерий готовности) |

**Red flags:** `...`, «при необходимости», «настроить как обычно», unnamed files, vague «протестировать», отсутствие Definition of Done на шаг.

**Severity rule:** любой placeholder в Critical path → минимум **Important**; в core step → **Critical**.

---

## 7. Scope creep

**Вопрос:** артефакт раздувает задачу beyond `{ORIGINAL_REQUEST}`?

| Score | Критерий |
|-------|----------|
| 1 | Явное расширение scope без запроса пользователя **в действиях / recommendations / summary** |
| 3 | Пограничные «улучшения» |
| 5 | Strictly bounded scope (тело research может быть шире – см. Breadth vs summary) |

**Red flags:** «заодно обновим README», «refactor while here», новые evals/скиллы не из запроса, cross-cutting changes без explicit ask, документация vault без запроса; recommendations, которые решают другую задачу.

**Не red flag (research/strategy):** широкий обзор / смежные темы в теле, если они помечены как контекст и **не** попадают в summary/recommendations как обязательные next steps.

---

## 8. Conciseness / anti-water

**Вопрос:** документ ровно такой длины, какая нужна для объяснения темы – без пустых слов и повторов?

| Score | Критерий |
|-------|----------|
| 1 | Значительная доля текста – вода или одни и те же тезисы 3+ раз разными формулировками; цель тонет |
| 3 | Есть повторы / filler, но core читаем |
| 5 | Каждый абзац несёт факт, решение, evidence или уточнение; дубли только где нужны (напр. краткий summary ≠ полный разбор) |

**Red flags:**
- один тезис пересказан в summary + body + recommendations **без новой информации**;
- вводные «в данном документе рассмотрим…», «важно отметить, что…» без содержания;
- синонимичные абзацы подряд;
- секции, которые можно удалить без потери смысла или actionable вывода;
- раздувание уже длинного документа «для полноты» без новых фактов/источников.

**Не red flag:**
- краткий Executive Summary, который сжимает (не копирует) тело;
- повтор ключевого вывода один раз в Recommendations с owner/deadline;
- необходимая ширина research-тела (см. Breadth vs summary).

**Severity rule:** вода, которая **искажает или прячет** цель/вывод → минимум **Important**; локальный filler → **Minor**; >~30% объёма без новой информации или summary утоплен в повторах → **Critical**.

---

## Severity mapping (default)

| Условие | Severity |
|---------|----------|
| Артефакт непригоден / неверная цель / data loss risk | Critical |
| Placeholder в core step, неверный порядок, scope creep block | Critical |
| Summary размывает цель; вода топит вывод | Critical |
| YAGNI overhead >1 дня работы, missing major risk | Important |
| Вода / дубли без потери цели; summary слегка off-topic | Important |
| Optimization opportunity, minor correctness, tail placeholders, локальный filler | Minor |
| Stylistic / optional nice-to-have | Minor (или omit) |

---

## Verdict gate

| Verdict | Условие |
|---------|---------|
| **REVISE** | ≥1 Critical **или** ≥3 Important **или** любой rubric score ≤ 2 |
| **PASS** | zero Critical, ≤2 Important, ≤2 Minor, все scores ≥ 4 |
