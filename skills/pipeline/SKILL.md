---
name: pipeline
description: Classic implementation pipeline – brainstorm/spec if unclear, writing-plans, then eng review (technical) or autoplan (feature), then SDD. Runs phases back-to-back, keeps state on disk, resumes after a crash. Use when starting or continuing a task via /pipeline.
disable-model-invocation: true
icon: rocket
color: blue
metadata:
  scope: public
  author: Jlosev
  version: "1.0.0"
  tags: "pipeline,orchestrator,sdlc"
created: 2026-09-15
updated: 2026-09-15
user-invocable: true
---

# /pipeline – запуск реализации

Оркестратор. Скиллы **читай с диска и выполняй**, тела не копируй и не вендори. `AGENTS.md` workspace побеждает дефолтные пути Superpowers/gstack.

**Announce:** `Using /pipeline – classify → plan → review → execute.`

**Hard gate:** до закрытия review **не пиши продуктовый код**, не scaffold, не `git commit` реализации. Исключение – throwaway spike, явно помеченный как throwaway.

**Прогон целиком.** Один вызов = все фазы до финиша ветки. Фазы идут подряд в этой сессии: закрыл артефакт – сразу следующая. Не спрашивай «продолжать?», не подменяй работу промежуточным отчётом. Пауза только по §Остановки.

Не зови gstack `/execute`. После плана – только role reviews / `autoplan`, затем Superpowers execute.

---

## State

`{workspace}/.cursor/pipeline/state.json` (путь из `AGENTS.md`, если задан). Лежит в **главном** workspace, не в `.worktrees/*` – иначе resume его не найдёт.

Пиши **после каждой фазы и каждого ruling**, не в конце прогона. State – источник истины о фазе; после компакта, обрыва сети или в новом чате читается он, а не память чата.

```json
{
  "task": "short-slug",
  "class": "unclear|technical|feature",
  "phase": "clarify|plan|review|execute|finish|done",
  "artifacts": { "spec": "path", "plan": "path" },
  "branch": "feat/x",
  "worktree": ".worktrees/feat-x",
  "blocked": null,
  "rulings": ["что решил – почему"],
  "updated": "YYYY-MM-DDTHH:MMZ"
}
```

Не коммитить: добавь `.cursor/pipeline/` в `.git/info/exclude` (локально, без диффа в репо).

Одна активная задача на workspace. Нужна вторая параллельно – отдельный worktree и свой state внутри него.

---

## 0. Контекст

1. **Прочитай state.** Есть, `phase != done` → resume с этой фазы, не с нуля (§Старт).
2. Прочитай `{workspace}/AGENTS.md` (если есть) – пути specs/plans, worktrees, запреты.
3. Классифицируй **вслух** (пользователь может переопределить):

| Класс | Когда | Дальше |
|---|---|---|
| **Unclear** | нет спеки, цель/границы размыты, «хочу X» без как | brainstorming |
| **Technical** | узкий техдолг: Makefile, CI, рефактор, тесты, изоляция, без новой user-facing фичи | writing-plans → **только** `plan-eng-review` |
| **Feature** | новая способность, UI, продукт, подсистема, поведение для пользователя | writing-plans → **`autoplan`** |

Сомнение → **Feature**. Hotfix (прод горит, минимальный патч) – единственный skip review; скажи это вслух и обоснуй.

Запиши `task` и `class` в state.

---

## 1. Clarify (только Unclear)

Прочитай и следуй `brainstorming` (`~/.agents/skills/brainstorming/SKILL.md`).

- Architectural → спека на диск, затем writing-plans. Путь спеки: `AGENTS.md` / `canon/superpowers/specs/` если задано, иначе дефолт скилла.
- Bounded в смысле brainstorming (уже есть поток в репо, правка локальная) – короткий дизайн в чате. Апрув нужен, только если выбор меняет продукт (§Остановки); иначе ruling и дальше. После дизайна всё равно **writing-plans**, не прыгай в код.
- Spike → ответ, не код в ветку. Новый запрос на внедрение = новый `/pipeline`.

gstack `/spec` / `/office-hours` – только если `AGENTS.md` или пользователь явно просит; не вместо brainstorming по умолчанию.

---

## 2. Plan

Прочитай и следуй `writing-plans` (`~/.agents/skills/writing-plans/SKILL.md`).

План на диск. Путь: `AGENTS.md` (`canon/superpowers/plans/` и т.п.) побеждает `docs/superpowers/plans/`.

Не предлагай «какой execute?» – сначала review. Путь плана в `artifacts.plan`, `phase: review`, дальше без паузы.

---

## 3. Review (обязателен, кроме hotfix)

Один и тот же plan file. Не пиши второй `## GSTACK REVIEW REPORT` – заменяй секцию. Не вендори SKILL.md. Не `docs/designs/`.

| Класс | Скилл | Что пропустить |
|---|---|---|
| **Technical** | `gstack-plan-eng-review` | CEO, design, DX, autoplan |
| **Feature** | `gstack-autoplan` | не подменяй «только eng», если это фича |

Пути скиллов (первый читаемый):

- `$HOME/.cursor/skills/gstack-autoplan/SKILL.md` / `$HOME/.cursor/skills/gstack-plan-eng-review/SKILL.md`
- `…/AgentStores/…/files/skills/gstack-autoplan/SKILL.md` / `…/skills/gstack-plan-eng-review/SKILL.md`
- иначе `$HOME/gstack/autoplan/SKILL.md` / `$HOME/gstack/plan-eng-review/SKILL.md`

Codex нет → Claude-only, тег `[codex-unavailable]`. Нет `~/gstack` при читаемом SKILL.md – не повод скипать review.

Review просит правки плана → правь план, не код. Замечания закрыты (eng-review без открытых critical; на taste-gate autoplan – только он и есть законная пауза) → `phase: execute` и сразу дальше.

---

## 4. Execute

Изоляция: `using-git-worktrees` (`~/.agents/skills/using-git-worktrees/SKILL.md`) – laptop `.worktrees/<branch>`; cloud уже изолирован, не вкладывать `.worktrees/`. `branch` и `worktree` → в state.

**Default:** `subagent-driven-development` (`~/.agents/skills/subagent-driven-development/SKILL.md`).

Агент может выбрать другое **и обязан сказать почему**:

- `executing-plans` – нет субагентов / задачи жёстко сцеплены в одной сессии
- прямой TDD в этой сессии – план на 1–2 механических шага и SDD избыточен

Не молча уходи в код в контроллере «чтобы быстрее».

Финиш ветки – как велит выбранный execute-скилл (`finishing-a-development-branch`). Commit/PR/push – только по правилам пользователя (обычно явная просьба). Перед `phase: done` – `verification-before-completion` (`~/.agents/skills/verification-before-completion/SKILL.md`): свежий вывод команд, не «должно проходить».

---

## Автономность

**Rulings, не стойка.** Неоднозначность, дефект плана, выбор инструмента, превышение лимита из плана – решай сам. Строкой в `state.rulings`: `что решил – почему – чем рискуем`. Неверный ruling стоит переделки, которую видно в диффе; сессия, зависшая на вопросе, стоит дня.

**Bounded retry.** ≤3 попытки на одну и ту же причину падения. Дальше – `blocked`, не четвёртый круг.

**Идемпотентность.** На resume не переделывай закрытую фазу: проверь артефакт из state (файл есть, плановые задачи отмечены, тесты гоняются) и иди дальше. Нет артефакта, хотя фаза помечена закрытой – доверяй диску, не метке.

### Остановки

Только это:

1. Необратимое или деструктивное, чего пользователь не просил: force push, `reset --hard`, удаление данных, публикация, push/PR без просьбы.
2. Нет факта, доступа или секрета – дальше только угадывать.
3. Вкус и конфликт: taste-gate `autoplan`, близкие альтернативы с разным продуктом, требования противоречат друг другу или ранее зафиксированному решению.
4. План сломан так, что любой путь – догадка.
5. `blocked` по bounded retry.

На остановке: запиши `blocked` (что именно нужно), скажи это в 1–2 строках и что `/pipeline` продолжит с этой фазы. Не сворачивай прогон «на всякий случай».

---

## Запреты

- Сразу кодить, потому что «и так ясно»
- Спрашивать «продолжать?» между фазами; резать прогон на один шаг за ход
- Начинать с нуля, когда в state живая задача
- Держать фазу и решения только в чате
- Писать state в `.worktrees/*`
- Закрывать фазу без артефакта или без свежей verification
- Пропустить brainstorming при Unclear
- Пропустить writing-plans, если вызван `/pipeline`
- Feature → только eng; Technical → полный autoplan «на всякий случай» (дорого и мимо)
- Второе копирование плана в vault / Agent Store вместо canon/workspace path
- gstack `/execute`

---

## Старт

1. Прочитай state. Нет файла → создай под новую задачу; есть и `phase != done` → resume, скажи одной строкой: задача, фаза, артефакт.
2. `blocked` заполнен и пользователь дал недостающее → очисти `blocked`, продолжай с той же фазы.
3. Прочитай `SKILL.md` текущей фазы и выполни её **до артефакта**.
4. Обнови state → следующая фаза без паузы. Повторяй до `phase: done` или остановки.
