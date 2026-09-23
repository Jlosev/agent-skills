---
created: 2026-09-23
updated: 2026-09-23
---

# Skill Benchmark: human-doc-voice

**After:** v1.7.0 (`skills/human-doc-voice/`)  
**Before:** v1.6.0 (git HEAD snapshot → `skill-snapshot-v1.6.0/`)  
**Executor:** inline worker по контракту SKILL (не независимые subagent-раны)  
**Grader:** `grade_run.py` (программные проверки по тексту выхода)  
**Date:** 2026-09-23

## Summary

| Metric | 1 With Skill (v1.7.0) | 2 Old Skill (v1.6.0) | Delta |
|--------|----------------------|----------------------|-------|
| Pass Rate (all 6 evals) | 100% ± 0% | 71% ± 24% | +0.29 |
| Pass Rate (should-trigger only, 4×7) | **100%** (28/28) | **57%** (16/28) | +0.43 |
| Time / Tokens | не измерялось | не измерялось | – |

## Per-eval (should-trigger)

| Eval | v1.7.0 | v1.6.0 | Δ ключевых провалов v1.6.0 |
|------|--------|--------|----------------------------|
| reglament | 7/7 | 4/7 | detect-only: файл не тронут; «Применить правки?» |
| research-note | 7/7 | 4/7 | detect-only + вопрос outbound/internal |
| task-brief | 7/7 | 4/7 | detect-only |
| short-instruction | 7/7 | 4/7 | detect-only |

**Стабильные провалы v1.6.0 на trigger-кейсах:** `edit_applied`, `no_ok_prompt`, `wrapper_removed`.  
**Стабильные проходы обеих версий:** `modality_preserved`, `register_ok`, `genre_not_refused`.

## Anti-trigger (description scope)

| Eval | v1.7.0 | v1.6.0 |
|------|--------|--------|
| mm-reply-anti | 2/2 | 2/2 |
| log-scratch-anti | 2/2 | 2/2 |

Проверка по тексту `description` в SKILL.md: chat и agent scratch в out-of-scope у обеих версий. **Runtime trigger rate не измерялся** (нет `run_loop` / claude -p).

## Analyst notes

- v1.7.0 закрывает запрос USER_REQUIREMENTS: правка сразу, без whitelist жанров, регламент/инструкция не уезжают в «отчёт для лидов».
- v1.6.0 по умолчанию detect-only → системный провал на «правка применена» и «нет ok» на всех trigger-кейсах.
- v1.6.0 на research-note дополнительно сомневается в жанре (internal vs outbound) – v1.7.0 этого не делает.
- Прогон **не** через параллельных subagent-исполнителей; pass rate по реальным выходам worker, не статистика variance.
