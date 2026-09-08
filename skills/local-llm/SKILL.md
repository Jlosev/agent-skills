---
name: local-llm
description: >
  Используй когда нужна пачка однотипной разметки, тегов или саммари без инструментов и MCP.
  Триггерные фразы «локальная модель», «LM Studio», «offload», «дешёвый complete».
  Не используй для judgment-heavy classify другого пайплайна, outbound-чата, mutate задач или Task-субагента.
metadata:
  scope: public
  author: Jlosev
  version: "1.0.0"
  tags: "lm-studio,local-llm,offload"
user-invocable: true
allowed-tools: Read, Write, Shell
created: 2026-09-08
updated: 2026-09-08
---

<!-- Based on: LM Studio OpenAI-compat structured output (https://lmstudio.ai/docs/developer/openai-compat/structured-output); LM Studio #1971 (reasoning_content fallback); LM Studio #1105 (GPT-OSS + strict schema hang) -->

# Local LLM

Облако решает и оркестрирует. Локальная модель только считает JSON. Вызов – `Shell`, не `Task`.

`{SKILL_DIR}` = directory of this SKILL.md.

Гейт – `references/when-to-use.md`. Default-модель – `references/model-pick.md`.

## Preconditions

- [ ] Прочитан `references/when-to-use.md`; гейт пройден (все три пункта).
- [ ] Есть JSON-схема (или короткий шаблон полей) и входной текст.
- [ ] LM Studio server на `LOCAL_LLM_BASE_URL` или `http://127.0.0.1:1234/v1`.

## Алгоритм

### Шаг 1 – гейт

Read `references/when-to-use.md`. Не все три пункта → не звать скрипт, сделать самому, одной строкой почему.

### Шаг 2 – health

```bash
python3 "{SKILL_DIR}/scripts/local_complete.py" --health
```

Exit ≠ 0 → fallback, не ретраить.

### Шаг 3 – файлы

Промпт, схему и `--out` писать только в `.tmp/local-llm/`.

### Шаг 4 – complete

```bash
python3 "{SKILL_DIR}/scripts/local_complete.py" \
  --prompt .tmp/local-llm/prompt.txt \
  --schema .tmp/local-llm/schema.json \
  --out .tmp/local-llm/out.json
```

Default модель `google/gemma-3-12b` (см. `references/model-pick.md`). Переопределение `--model` / `LOCAL_LLM_MODEL`. Load: `--gpu max -c 8192 --parallel 1 --ttl 900` (`LOCAL_LLM_GPU` / `LOCAL_LLM_CONTEXT` / `LOCAL_LLM_PARALLEL` / `LOCAL_LLM_TTL`).

### Шаг 5 – результат

Прочитать `--out`. Exit 4 → один retry только если это parse. Иначе fallback.

Не запускать `Task`. Не ходить в MCP с локалки. Complete сам делает `lms load` с gpu/ctx/parallel/ttl, если модель в каталоге, но не loaded.

### Шаг последний – retro

Одной строкой: что улучшить в скилле после этого прогона.

## Hard Stop Rules

- **`Task` / новый агент** для локалки запрещены.
- **`lm-studio-subagents` запрещён** – Task или REST без `json_schema` не замена этому скиллу.
- **Авто-load только через скрипт.** `lms load <id> --yes --gpu max -c 8192 --parallel 1 --ttl 900`. `LOCAL_LLM_TTL=0` – без TTL. Load fail → exit 3, fallback.
- **Нет третьего identical retry.**
- **Stdout скрипта** не смешивать с диагностикой; диагностика у скрипта в stderr.
- **Не заменять** judgment-heavy classify другого пайплайна этим скиллом.

### Exit codes

| Код | Смысл |
| --- | --- |
| 0 | ok |
| 2 | сервер недоступен / timeout |
| 3 | нет instruct / модель не loaded |
| 4 | ответ не JSON или нет required |

## Definition of Done

- Гейт пройден или явно отвергнут.
- При вызове скрипта есть `--out` с валидным JSON **или** fallback без `Task`.
- Скрипт agent-compatible-cli: stdout = JSON only, stderr = диагностика, non-interactive.
- Артефакты только в `.tmp/local-llm/`.
- Retro-строка записана.

## Пример

**Вход:** пачка заголовков + схема `{tag, noise}`.

**Шаги 2–4** → `.tmp/local-llm/out.json`.

**Результат (фрагмент):**

```json
{"tag": "fyi", "noise": false}
```

**Fallback:** exit 3 после неудачного авто-load → оркестратор размечает сам.

## Команды проверки

```bash
grep -E '^## (Hard Stop Rules|Definition of Done|Команды проверки|Scope|Gotchas|Алгоритм|Пример|Preconditions)' \
  "{SKILL_DIR}/SKILL.md"

python3 "{SKILL_DIR}/scripts/test_local_complete.py"
python3 "{SKILL_DIR}/scripts/local_complete.py" --health
```

## Gotchas

- `/v1/models` показывает скачанные, не loaded. Скрипт смотрит `/api/v0/models` (`state`); not-loaded → `lms load --yes`, потом POST.
- **Retry taxonomy:** exit 2 (transport) – не ретраить; exit 3 (availability) – не ретраить; exit 4 (parse) – один retry.
- Модели **≥7B** для `json_schema` – см. [LM Studio structured output](https://lmstudio.ai/docs/developer/openai-compat/structured-output). Модели <7B на схеме ненадёжны – не default. Easy-фикстура может пройти копированием текста; hard-кейсы ломают urgency.
- **GPT-OSS + strict schema** может зависнуть (LM Studio #1105) – не default-модель для схемного complete.
- Пустой `content`, JSON в `reasoning_content` – скрипт принимает fallback (LM Studio #1971).
- `google/gemma-4-26b-a4b-qat` игнорирует `-c 8192` и грузится с ctx ~226k – не default.
- Две instruct в RAM сразу не грузить на 48 GB unified (запас на IDE).

## Scope

In: схемный/шаблонный complete на уже скачанной модели LM Studio  
Out: субагент, judgment-heavy classify другого пайплайна, outbound-чат, mutate задач, ручной `lms load` в обход скрипта, ngrok  
Fallback: скрипт ≠ 0 → оркестратор делает сам
