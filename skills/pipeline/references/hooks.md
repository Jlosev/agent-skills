# Хуки Claude Code для /pipeline

Ставятся один раз глобально, работают во всех проектах. Хук молчит, пока в сессии не идёт прогон `/pipeline`.

## Что делает `pipeline.py hook`

| Событие | Условие | Действие |
|---|---|---|
| `Stop` | найден state (сначала `.pipeline/` своего worktree, потом главного checkout, потом `.cursor/pipeline/`; закоммиченный в git не считается), `phase` не `done` и не `clarify`, `blocked` пуст, сессия – владелец прогона (`state.session`, иначе транскрипт вызывал `/pipeline`), `background_tasks` пуст | `{"decision":"block"}`: продолжай по state |
| `Stop` | то же, но нет прогресса (`updated` и `HEAD` те же) после 2 блоков подряд или 6 блоков за фазу | отпускает ход и шлёт «агент стоит» в канал уведомлений |
| `StopFailure` (ошибка API: лимит, сервер, обрыв) | активный прогон | только уведомление «напиши продолжай»: продолжить ход это событие не умеет |
| прерывание пользователем (Esc) | — | хук не вызывается, остановка всегда возможна |

Канал уведомлений: `$PIPELINE_NOTIFY_CMD`, иначе `lan-notify` из `PATH`, иначе без уведомлений. Сбой хука никогда не ломает сессию: любая ошибка → выход 0.

## Установка

`~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [{ "hooks": [{ "type": "command", "command": "f=~/.agents/skills/pipeline/scripts/pipeline.py; [ -f \"$f\" ] && python3 -I \"$f\" hook; exit 0", "timeout": 20 }] }],
    "StopFailure": [{ "hooks": [{ "type": "command", "command": "f=~/.agents/skills/pipeline/scripts/pipeline.py; [ -f \"$f\" ] && python3 -I \"$f\" hook; exit 0", "timeout": 20 }] }]
  }
}
```

`exit 0` в конце обязателен: для `Stop` код 2 значит «блокировать», и без него пропавший скрипт держал бы каждую сессию. Если блок `hooks.Stop` уже есть – добавь элемент в массив, не заменяй.

## Проверка

```sh
bash ~/.agents/skills/pipeline/scripts/test_pipeline.sh   # самопроверки preflight, diff-guard, hook
```

Cursor: формат хуков другой; там прогон держится на правилах скилла без хука.
