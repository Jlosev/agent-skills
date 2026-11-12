---
name: pipeline
description: Classic implementation pipeline – preflight, brainstorm/spec if unclear, writing-plans, eng review (technical) or autoplan (feature), SDD, then a deterministic verify gate and rebase before finish. Runs phases back-to-back, decides instead of asking, keeps state on disk, resumes after a crash. Use when the user types /pipeline or the project's AGENTS.md routes an implementation task through /pipeline; not for one-line fixes or questions.
icon: rocket
color: blue
metadata:
  scope: public
  author: Jlosev
  version: "1.1.0"
  tags: "pipeline,orchestrator,sdlc"
created: 2026-09-15
updated: 2026-11-08
user-invocable: true
---

# /pipeline – запуск реализации

Оркестратор. Скиллы **читай с диска и выполняй**, тела не копируй. `AGENTS.md` workspace побеждает дефолты этого скилла (§Переопределение проектом).

**Announce:** `Using /pipeline – preflight → classify → plan → review → execute → verify → finish.`

**Hard gate:** до закрытия review не пиши продуктовый код, не scaffold, не коммить реализацию. Исключение – throwaway spike, явно помеченный.

**Прогон целиком.** Один вызов = все фазы до `done`. Закрыл артефакт – сразу следующая фаза. Не спрашивай «продолжать?», не подменяй работу промежуточным отчётом. Пауза только по §Остановки. Хук `Stop` (`references/hooks.md`) не даёт закончить ход посреди прогона.

`TOOLS = python3 -I ~/.agents/skills/pipeline/scripts/pipeline.py` (рядом с этим SKILL.md).

---

## State

`{main workspace}/.pipeline/state.json`. Каталог создаёт `TOOLS preflight` с `.pipeline/.gitignore` = `*`: в git не попадает, `.git/info/exclude` не трогай. Из worktree прогона state всё равно пишется в главный checkout (preflight печатает путь). Старый `.cursor/pipeline/` (preflight печатает `legacy_state=`) – прогон 1.0, возможно живой: без слова пользователя не трогай, новая задача – свой worktree и state. Перенос по просьбе – целиком, по §«Где лежат файлы прогона».

`session` = `session=` из preflight (`$CLAUDE_CODE_SESSION_ID`); на resume в новом чате перезапиши. По нему хук `Stop` узнаёт сессию прогона.

Пиши **после каждой фазы, ruling и вмешательства пользователя**. State – источник истины; после компакта, обрыва или в новом чате читай его, а не память чата.

```json
{
  "task": "short-slug",
  "session": "id from preflight",
  "class": "unclear|technical|feature",
  "size": "S|M|L",
  "phase": "preflight|clarify|plan|review|execute|verify|finish|done",
  "artifacts": { "spec": "path", "plan": "path|state" },
  "branch": "feat/x", "worktree": ".pipeline/worktrees/feat-x", "base": "origin/main",
  "scope": ["src/widgets/**", "tests/widgets/**"],
  "verify": { "cmd": "make ci", "runtime": "how or null", "gates": {}, "diff_sha": "", "at": "" },
  "blocked": null,
  "notify": { "progress_id": null, "ask_id": null },
  "rulings": ["что решил – почему – чем рискуем"],
  "interventions": [{ "at": "", "kind": "question|nudge|correction|access|scope|gate|other", "said": "≤100 симв.", "prevent": "что в скилле убрало бы это" }],
  "updated": "YYYY-MM-DDTHH:MMZ (UTC: date -u +%Y-%m-%dT%H:%MZ)"
}
```

Одна активная задача на workspace. Вторая параллельно – отдельный worktree и свой `<worktree>/.pipeline/state.json` (с тем же `.gitignore` = `*`): хук и diff-guard сначала ищут state в своём worktree.

### Где лежат файлы прогона

Скилл общий для Claude Code, Cursor, Codex и других агентов. Каталоги харнесов (`.cursor/`, `.claude/`, `.codex/`) – только для их настроек: файлов прогона туда не пиши, даже если там уже лежит state 1.0.

| Что | Куда |
|---|---|
| state, задания исполнителям, control plane, черновики | `.pipeline/` главного checkout: `state.json`, `briefs/<slug>.md`, `scratch/`. Отложенная задача – `archive/state-<task>.json` |
| спеки, планы | путь из `AGENTS.md`, иначе дефолт `brainstorming` / `writing-plans`; в git ветки прогона |
| отчёты, разборы, исследования для человека | по правилам проекта (`AGENTS.md`, `docs/`, база), иначе рядом со спекой. Ссылка – в `artifacts` |

`.pipeline/` вне git: туда только то, что не нужно после прогона. Документ, который прочитает человек или соавтор, туда не клади.

---

## 0. Preflight и контекст

1. **Прочитай state.** Есть, `phase != done` → resume с этой фазы (§Старт).
2. `TOOLS preflight`. `BLOCKED` → одна строка пользователю с готовым исправлением из вывода, `blocked` в state, стоп. Прогон из чужого каталога (vault, `~`) – это `BLOCKED`, не обходи.
3. Прочитай `AGENTS.md` workspace и всё, на что ссылается запрос: ссылки, файлы, issue. Непрочитанная ссылка из запроса – дефект прогона.
4. **Команда проверки** → `verify.cmd`: из `AGENTS.md`, иначе ближайший к CI кандидат из `verify_candidate=` preflight (`make ci` > `make check` > набор test+lint), иначе шаги `.github/workflows`. Не нашёл – ruling «проверка: <что гоняю> – почему». Baseline – в §4.
5. **Внешние зависимости** задачи (токены, аккаунты, доступы, платные ресурсы; `remote=unreachable` или `gh` без входа, если прогон будет пушить) – собери все сразу и попроси одним сообщением в начале, как остановку (§Остановки). Во время execute не всплывают по одной. `base=unknown` – ruling: ветка, куда идут PR.
6. Классифицируй **вслух** (пользователь может переопределить) и запиши `task`, `class`, `size`:

| Класс | Когда | Дальше |
|---|---|---|
| **Unclear** | нет спеки, цель/границы размыты, «хочу X» без как | brainstorming |
| **Technical** | техдолг: Makefile, CI, рефактор, тесты, изоляция, без новой user-facing фичи | writing-plans → **только** `plan-eng-review` |
| **Feature** | новая способность, UI, продукт, подсистема, поведение для пользователя | writing-plans → **`autoplan`** |

| Размер | Когда | Отличие |
|---|---|---|
| **S** | ≤3 файла, одна область, без нового поведения для пользователя, без auth/security/миграций | план – список задач и `scope` в state, `artifacts.plan = "state"`, сразу `phase: execute`, прямой TDD |
| **M** | всё остальное | полный путь |
| **L** | несколько подсистем, миграции, auth/security | полный путь, ревьюеры с повышенным effort |

Сомнение в классе → Feature, в размере → M. Hotfix (прод горит) – единственный skip review кроме S; скажи вслух и обоснуй.

---

## 1. Clarify (только Unclear)

Прочитай и следуй `brainstorming` (`~/.agents/skills/brainstorming/SKILL.md`). Диалог с пользователем здесь законен: хук в фазе `clarify` не держит ход.

- Architectural → спека на диск (путь из `AGENTS.md`, иначе дефолт скилла), затем writing-plans.
- Bounded (поток уже есть, правка локальная) – короткий дизайн в чате. Апрув нужен, только если выбор меняет продукт (§Остановки); иначе ruling и дальше, всё равно через writing-plans.
- Spike → ответ, не код в ветку.

gstack `/spec` / `/office-hours` – только если просит `AGENTS.md` или пользователь.

---

## 2. Plan

Прочитай и следуй `writing-plans` (`~/.agents/skills/writing-plans/SKILL.md`). План на диск; путь из `AGENTS.md` побеждает `docs/superpowers/plans/`.

Пути файлов из плана (Create/Modify/Test) → `state.scope`, globs допустимы. Для изменения UI план называет **сценарий проверки в продукте** и способ: spec e2e проекта или браузерная проверка → `verify.runtime`.

Путь плана в `artifacts.plan`, `phase: review`, дальше без паузы.

---

## 3. Review (кроме S и hotfix)

Один и тот же plan file. Не пиши второй `## GSTACK REVIEW REPORT` – заменяй секцию.

| Класс | Скилл | Что пропустить |
|---|---|---|
| **Technical** | `plan-eng-review` | CEO, design, DX, autoplan |
| **Feature** | `autoplan` | не подменяй «только eng», если это фича |

Скилл ищи по порядку: инструмент Skill (`autoplan`, `plan-eng-review`); `~/.claude/skills/gstack/<name>/SKILL.md`; `~/.cursor/skills/gstack-<name>/SKILL.md`. Codex нет → Claude-only, тег `[codex-unavailable]`.

Review просит правки плана → правь план, не код; обнови `scope`. Замечания закрыты → `phase: execute` и дальше. Итог review – одна строка в `rulings`.

---

## 4. Execute

Изоляция: `using-git-worktrees` (`~/.agents/skills/using-git-worktrees/SKILL.md`). Путь – из `AGENTS.md`, иначе `.pipeline/worktrees/<branch>`: каталог уже в игноре, `.gitignore` и `.git/info/exclude` не трогай. Cloud уже изолирован. `branch`, `worktree` → state.

План и спека, написанные в главном checkout, – перенеси в ветку прогона и закоммить первым коммитом (если `AGENTS.md` не велит иное), обнови пути в `artifacts`. В главном checkout не оставляй неотслеживаемых файлов.

До первой правки – `verify.cmd` в worktree → `verify.baseline`: что падает уже на `base`. В главном checkout проверки не гоняй.

**Default:** `subagent-driven-development` (`~/.agents/skills/subagent-driven-development/SKILL.md`). Независимые задачи плана (разные файлы, нет зависимости) – параллельно через `dispatching-parallel-agents`. Иное (`executing-plans`; прямой TDD для S или 1–2 механических шагов) – можно, причину в rulings.

**Вызов `/pipeline` – явная просьба пользователя коммитить в ветке прогона.** О коммитах не спрашивай. Push, PR, merge – по §Финиш.

Субагент упал (обрыв, ошибка API, пустой hand-back) → перезапусти ту же задачу из state до 2 раз, без вопроса. Дальше – bounded retry.

Последняя задача закрыта → `phase: verify`.

---

## 5. Verify (обязательна, включая S)

Готовность доказывают команды, а не отчёт исполнителя. Порядок и форма записи – `references/verify.md`. Коротко:

1. `verify.cmd` целиком в worktree; гейты в `verify.gates`: `passed | failed | blocked | not_run: причина`. `ci` не запустился – это `blocked`, не `not_run`.
2. `verify.runtime` задан → проверка сценария в работающем продукте, evidence (trace, скриншот с assertion) – путь в state. Нет способа запустить – `not_run: причина`; тогда PR только draft и строка в отчёте.
3. `TOOLS diff-guard` (сам находит worktree прогона) → каждая `FINDING` закрыта: правка, или ruling с обоснованием (намеренная смена контракта, правка CI по задаче). `DIFF_SHA` → `verify.diff_sha`.
4. Финальное ревью кода (из SDD или `requesting-code-review`): ревьюер получает план, diff, вывод verify и diff-guard. Выводы и самооценку исполнителя не передавай.

`failed` → назад в execute с логом падения; тот же отпечаток падения 3 раза → `blocked`. Падение, которое есть в `verify.baseline` и вне задачи, – `failed: pre-existing`, его не чини и не прячь: строка в отчёте. Всё `passed`, `pre-existing` или обоснованный `not_run` → `phase: finish`.

---

## 6. Финиш

1. `git fetch` и rebase на `base`. Ветка уже запушена (`upstream` есть) или `AGENTS.md` велит merge – merge `base` в ветку: force push не нужен. Конфликт решай сам; не решается без угадывания → `blocked`.
2. После обновления снова `verify.cmd` и `TOOLS diff-guard`, новый `verify.diff_sha`. Перед PR `TOOLS diff-guard --expect-sha <verify.diff_sha>` = 0: код после проверки не менялся.
3. `finishing-a-development-branch` (`~/.agents/skills/finishing-a-development-branch/SKILL.md`). Push и PR – как разрешает `AGENTS.md` или пользователь; иначе ветка готова локально и это сказано в отчёте.
4. `verification-before-completion` – свежий вывод команд.
5. **Отчёт** (до 10 строк): что сделано, PR/ветка, гейты со статусами, всё `not_run` отдельной строкой, rulings с риском, вмешательства пользователя этого прогона. → `phase: done`.

---

## Автономность

**Rulings, не вопросы.** Неоднозначность, дефект плана, выбор инструмента, превышение лимита из плана – решай сам, строкой в `rulings`: `что решил – почему – чем рискуем`. Неверный ruling стоит переделки, которую видно в диффе; сессия на вопросе стоит дня.

**Не спрашивай** (это всегда ruling):

- отступить ли от маршрута этого скилла или упростить его – нет, иди по маршруту; разумное отступление – ruling;
- коммитить ли в ветке прогона, как назвать ветку, какой execute-скилл выбрать;
- распараллелить ли, какую модель и effort взять субагенту;
- «продолжать?», «так ок?» между фазами.

**Руками пользователя – только то, что агенту недоступно** (интерактивный логин, окно ОС, секрет). Тогда точная проверенная команда одной строкой, с `!` для запуска в сессии.

**Bounded retry.** ≤3 попытки на один отпечаток падения. Дальше `blocked`.

**Идемпотентность.** На resume закрытую фазу не переделывай: проверь артефакт из state. Метка фазы есть, артефакта нет – доверяй диску.

**Итог фазы и гейт вехи – список на просмотр, не вопросы.** Решения, принятые в фазе, отдавай одним списком «проверь и поправь, если не так»: что решил – почему – чем рискуем. Ручная приёмка вехи из плана – законная остановка, но одной просьбой: что проверить, как именно, что будет после «ок». Пачка «решения за вами» запрещена: всё, что можешь решить сам, – в rulings.

**Вмешательства.** Пользователь написал посреди прогона (кроме ответа на законную остановку) – запиши в `interventions`: что сказал, тип, что в скилле предотвратило бы это. Сводка вмешательств – материал для следующей версии скилла.

### Остановки

Только это:

1. Необратимое или деструктивное, чего пользователь не просил: force push, `reset --hard`, удаление данных, публикация, push/PR/merge без разрешения.
2. Нет факта, доступа или секрета – дальше только угадывать.
3. Вкус и конфликт: taste-gate `autoplan`, альтернативы с разным продуктом, требования противоречат друг другу или ранее зафиксированному решению.
4. План сломан так, что любой путь – догадка.
5. `blocked` по bounded retry или preflight.

**Любой вопрос пользователю и пауза по его просьбе – сначала `blocked` в state, потом вопрос.** Без этого хук `Stop` вернёт ход. Ответ получен – очисти `blocked`.

На остановке:

1. `blocked` в state: что нужно и что будет при каждом ответе.
2. Вопрос пользователю: что решить, последствия вариантов, твоя рекомендация. Без голого «да?».
3. Есть канал уведомлений пользователя – вопрос туда с вариантами, ожидание ответа фоновой командой (`references/notify.md`). Ответ в чате тоже принимается.
4. Не сворачивай прогон «на всякий случай»: независимую работу, которой ответ не нужен, продолжай.

### Прогресс

Вызов `/pipeline` – просьба пользователя уведомлять о прогоне, если его правила допускают канал. Есть канал уведомлений – одна живая карточка прогресса на прогон, обновление на смене фазы; итог и остановки – отдельной карточкой со звуком (`references/notify.md`). Нет канала – молча работай, сводка в отчёте.

---

## Переопределение проектом

`AGENTS.md` (или правила проекта) побеждает дефолт по каждому пункту, если явно задаёт его:

| Что | Дефолт скилла |
|---|---|
| пути спек и планов | дефолты `brainstorming` / `writing-plans` |
| `verify.cmd`, обязательные гейты | ближайший к CI кандидат из preflight |
| проверка сценария в продукте | spec e2e проекта или браузерная проверка для UI |
| `base`, rebase или merge | `origin/HEAD`, rebase |
| push, PR, ready, merge | только с разрешения пользователя |
| маршрут задачи (чат, внешний runner) | этот скилл в чате |
| worktrees | `.pipeline/worktrees/<branch>` |
| уведомления | по глобальным правилам пользователя |

Запреты проекта сильнее разрешений этого скилла. Противоречие проекта с этим скиллом – ruling в пользу проекта.

---

## Запреты

- Сразу кодить, потому что «и так ясно»
- Спрашивать «продолжать?»; резать прогон на один шаг за ход
- Начинать с нуля, когда в state живая задача
- Держать фазу и решения только в чате
- Закрывать фазу без артефакта; ставить `done` без verify и rebase
- Засчитывать результат проверки старше последнего diff
- Ослаблять тесты, assertions, CI ради зелёного статуса
- Пропустить brainstorming при Unclear; writing-plans при M/L
- Feature → только eng; Technical → полный autoplan «на всякий случай»
- gstack `/execute`

---

## Старт

1. Прочитай state. Нет файла → preflight и новая задача; есть и `phase != done` → resume, одной строкой: задача, фаза, артефакт.
2. `blocked` заполнен и пользователь дал недостающее → очисти `blocked`, продолжай с той же фазы.
3. Прочитай `SKILL.md` текущей фазы и выполни её **до артефакта**.
4. Обнови state → следующая фаза без паузы. Повторяй до `phase: done` или остановки.
