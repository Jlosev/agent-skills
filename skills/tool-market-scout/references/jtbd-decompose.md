# JTBD Decompose

## Product decompose (если назван бренд)

1. Прочитай official docs / features / pricing — не обзоры-списки.
2. Раздели capabilities на **jobs**, не фичи:

| Маркетинг («AI-polished output») | Job |
|----------------------------------|-----|
| Works in every app | System-wide text injection from voice |
| Removes filler words | Real-time cleanup while dictating |
| Personal dictionary | Learn custom vocabulary / jargon |
| Command mode | Voice-driven text editing |
| Cross-device sync | Same dictation profile on phone + desktop |

3. Спроси пользователя: какие jobs **must** vs **nice**?
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

## Пример Wispr Flow

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

## Checkpoint template

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
