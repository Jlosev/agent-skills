# Verify – детерминированный гейт перед финишем

## CONSTRAINTS

- Готовность = вывод команд в этом diff. Самооценка исполнителя, «должно проходить» и exit 0 субагента – не доказательство.
- Статусы гейтов: `passed`, `failed`, `blocked`, `not_run: <причина>`, `not_applicable: <причина>`. Пустой статус = `not_run`.
- Результат старше последнего изменения кода не засчитывается: после любой правки и после rebase гоняй заново и обновляй `diff_sha` (`DIFF_SHA` из diff-guard, учитывает и untracked-файлы). Перед PR `diff-guard --expect-sha <diff_sha>` обязан дать 0.
- `verify.baseline` – результат `verify.cmd` на `base` до правок. Падение из baseline вне задачи – `failed: pre-existing <тест>`: не чинить попутно, не отключать, строка в отчёте. Новое падение – обычный `failed`.
- `ci` не запустился – `blocked`. `runtime` без способа запуска – `not_run: причина`, PR только draft.
- Не ослабляй проверку ради зелёного: `skip`, `xfail`, удалённые assertions, `|| true`, `continue-on-error`, правка снапшотов под новый вывод. Нужна смена контракта – ruling с обоснованием, и ревьюер видит это в diff-guard.
- Проект без какого-то вида проверки (нет typecheck, нет e2e) – `not_applicable` с причиной; фиктивный гейт не добавляй.

## ROUTING

| Шаг | Что делать | Запись в `state.verify.gates` |
|---|---|---|
| 1. static + tests | `verify.cmd` целиком в worktree, с тем же окружением, что в CI (`CI=true`, если так в CI) | `ci: passed` / `failed` + хвост лога ≤20 строк в отчёт |
| 2. runtime | `verify.runtime` задан → запусти продукт, пройди сценарий, проверь результат assertion-ом, сохрани trace или скриншот | `runtime: passed` + путь evidence; нет возможности → `not_run: <почему>` |
| 3. diff-guard | `python3 -I <skill>/scripts/pipeline.py diff-guard` | `diff_guard: passed` или список закрытых `FINDING` |
| 4. review | финальное ревью кода; ревьюеру: план, diff, вывод шагов 1–3 | `review: passed` / найденное → назад в execute |

### runtime: как выбрать способ

| Изменение | Способ |
|---|---|
| web UI | e2e-spec проекта на изменённый сценарий (новый или существующий), иначе браузерная проверка по правилам пользователя (`/browse`, `playwright-cli`) |
| API | запрос к локально запущенному сервису: статус, схема, бизнес-assertion |
| CLI | запуск на синтетическом входе: exit code, stdout, выходные файлы |
| без поведения для пользователя | `not_applicable: <почему>` |

Скриншот без проверки результата – не доказательство. Порт занят чужим процессом – возьми другой; чужой процесс не убивай.

### Отпечаток падения

`failed` → в execute с логом падения. Тот же тест или та же ошибка в третий раз подряд – `blocked`, четвёртого круга нет.

## DATA

```json
"verify": {
  "cmd": "make ci",
  "runtime": "tests/e2e/widget-bubble.spec.ts --trace on",
  "gates": { "ci": "passed", "runtime": "passed", "diff_guard": "passed", "review": "passed" },
  "evidence": [".pipeline/evidence/widget-bubble-trace.zip"],
  "diff_sha": "3f2a9c01d4e5b6a7",
  "at": "2026-11-08T21:40Z"
}
```

Evidence храни в `.pipeline/evidence/` (не в git). Trace и скриншоты могут содержать токены и персональные данные: синтетические аккаунты, наружу не публикуй.
