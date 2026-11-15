# JTBD Decompose

## Product decompose (если назван бренд)

1. Прочитай official docs / features / pricing / changelog — не обзоры-списки. Если задача – надстройка над этим продуктом, сначала проверь его штатные возможности (меню, команды, плагины, API): покрытие 70%+ – скажи об этом до внешнего поиска.
2. Раздели capabilities на **jobs**, не фичи:

| Маркетинг («AI-polished output») | Job |
|----------------------------------|-----|
| Works in every app | System-wide text injection from voice |
| Removes filler words | Real-time cleanup while dictating |
| Personal dictionary | Learn custom vocabulary / jargon |
| Command mode | Voice-driven text editing |
| Cross-device sync | Same dictation profile on phone + desktop |

3. Stake – спроси пользователя, какие jobs **must** и **nice**. Small pick – размечай сам и пиши в бриф одной строкой.
4. Запиши **out of scope** — что пользователю не нужно (экономит scan).

## Idea decompose (если описана идея, без бренда)

1. Job statement: `When [situation], I want [motivation], so I can [outcome]`
2. Разбей на functional / emotional / social (минимум functional)
3. Текущий workaround: что делает сейчас + cost (время, деньги, боль)

## Anti-patterns

| Плохо | Хорошо |
|-------|--------|
| «Найти замену Wispr» | «System-wide voice dictation with cleanup on macOS» |
| «Transcription app» | «Real-time dictation into any text field» + optional «batch file transcription» как отдельный job |
| Один job на всё | 3–7 atomic jobs, каждый → свои query families |

## Иллюстрация: замена Wispr Flow

Пример разбора одного продукта. Для другой задачи – те же шаги, свои jobs.

**Jobs (functional):**
- J1 — голос → текст в любом приложении (hotkey, background)
- J2 — cleanup при диктовке (filler, self-correction, punctuation)
- J3 — персональный словарь / domain terms
- J4 — голосовые команды редактирования текста
- J5 — sync macOS ↔ iOS

**Out of scope (если пользователь не просил):**
- Batch transcription длинных записей
- Meeting notes / speaker diarization
- Team admin / SSO

## Small pick – brief в одну строку

```text
Brief: <capability> · <platform> · <constraints> · out of scope: <...>
```

## Checkpoint template (stake)

```markdown
## JTBD Brief — {topic}
**Job statement:** ...
**Must jobs:** J1, J2, ...
**Nice jobs:** ...
**Constraints:** platform, budget, OSS, privacy
**Workaround today:** ...
**Out of scope:** ...

Подтверди или поправь — после этого начну scan.
```
