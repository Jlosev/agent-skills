---
created: 2026-09-08
updated: 2026-09-08
---

# Default model

**Winner:** `google/gemma-3-12b`

Load (скрипт сам, если не loaded):

```bash
lms load google/gemma-3-12b --yes --gpu max -c 8192 --parallel 1 --ttl 900
```

Переопределение: `--model` / `LOCAL_LLM_MODEL`. Load-флаги: `LOCAL_LLM_GPU`, `LOCAL_LLM_CONTEXT`, `LOCAL_LLM_PARALLEL`, `LOCAL_LLM_TTL` (`0` = без TTL).

## Железо (2026-09-08)

MacBook Pro Mac16,7, M4 Pro, 48 GB unified. Две instruct сразу не грузить.

## Каталог на диске

| id | Диск | A/B 2026-09-08 | Вердикт |
| --- | --- | --- | --- |
| `google/gemma-3-12b` | 13.36 GB, dense Q8 | easy: `action_me`/`critical`; hard: `fyi`/`low` + своя выжимка; load+easy 6.9 с; ctx **8192** как просили | **default** |
| `google/gemma-4-26b-a4b-qat` | 15.64 GB, MoE QAT 4-bit | easy: тот же JSON; hard: `fyi`/`low`, выжимка чуть врёт («устранены»); warm joke 0.7 с; **`-c 8192` игнорирует**, встаёт ctx **226304** | запасной `--model`; не default |
| `qwen2.5-1.5b-instruct-mlx` | 885 MB | easy: угадала копированием; hard: `noise` + **`critical`** и копия поста | не default |
| эмбеддеры | <1 GB | не complete | не complete |

Новое с Hub не качали: на диске нет кандидата точнее 12B на схемном JSON. Community research не дала кандидата ≥80%.

## Почему 12B, не 26B

Качество на схемном classify не выше, а load-контракт хуже: 26B A4B не принимает наш context cap (оба варианта `-c` / `--context-length`). 12B – Q8, ctx 8192, parallel 1, TTL 15 мин, холодный старт ~7 с.

Источники: live `lms ls` / `lms ps` / `local_complete.py` 2026-09-08; [Gemma 3 developer guide](https://developers.googleblog.com/introducing-gemma3/); [LM Studio structured output](https://lmstudio.ai/docs/developer/openai-compat/structured-output).
