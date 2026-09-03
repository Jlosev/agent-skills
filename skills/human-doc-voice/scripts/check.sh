#!/usr/bin/env bash
# human-doc-voice checklist – stdout only; does not edit files.
set -euo pipefail

PATH_ARG="${1:-}"
if [[ -z "$PATH_ARG" ]]; then
  echo "usage: check.sh <path.md|path.canvas.tsx>" >&2
  exit 2
fi

echo "human-doc-voice checklist: $PATH_ARG"
echo
echo "Intent"
echo "  [ ] Артефакт уйдёт наружу (лиды / wiki / publish / «для отправки») или это demo Canvas"
echo "  [ ] Не внутренний WIP/research «для себя» (иначе skip skill)"
echo
echo "Режим"
echo "  [ ] Проверить и исправить несоответствия – не переписывать всё подряд"
echo "  [ ] После точечных правок – полный проход документа на тот же паттерн"
echo "  [ ] Тон: формальный отчёт, не личный чат"
echo
echo "60s reader test"
echo "  [ ] За 60 сек понятно: зачем читать + главная мысль"
echo "  [ ] Заголовки называют содержание (понятны без знания анкеты)"
echo "  [ ] Оговорки: ясная польза или удалены"
echo
echo "Дедупликация – один факт в одном месте"
echo "  [ ] Правило не объясняется дважды (шаг, callout, FAQ, таблица ролей)"
echo "  [ ] Механика – в шаге, «почему» – в FAQ; не в обоих"
echo "  [ ] Проза и список не пересказывают друг друга"
echo "  [ ] Нет колонки таблицы с одинаковым значением во всех строках"
echo "  [ ] Пример не дублирует справочную таблицу"
echo "  [ ] Одна сущность – один термин, дословно как в UI"
echo "  [ ] Нет ролей и систем вне scope; неизменившийся процесс – одной отсылкой"
echo "  [ ] Патч к живой странице прочитан вместе с нетронутым текстом"
echo
echo "Anti-agent-meta / anti-slop / anti-padding / anti-kitchen"
echo "  [ ] Нет: влито / residual / keyword-кластер / fill rate / verbatim / Q-коды в UI"
echo "  [ ] Нет разговорного: «Если коротко» / «Собрал…» / «реально страдают» / «кому хуже»"
echo "  [ ] Нет кухни: «длинные пути» / «не оргсхема» / «цифра волны» / «не раздуваем»"
echo "  [ ] Нет мета про структуру: «отдельный раздел не нужен» / «там смотрим»"
echo "  [ ] Подписи не раздуты и не дублируют заголовок/Stat"
echo
echo "Нейро-синтаксис"
echo "  [ ] Обращение к читателю, а не безличное «считают / оформляется»"
echo "  [ ] У действия назван субъект: «калькулятор переводит», не «пересчитывается»"
echo "  [ ] Связки союзами, а не тире и двоеточием подряд"
echo "  [ ] Глагол вместо отглагольного ярлыка («вход в расчёт», «оптика», «пересчёт в»)"
echo "  [ ] Нет повтора корня в одной фразе"
echo
echo "Handoff"
echo "  [ ] Показать before→after только по правкам; ждать «ок» на язык"
echo "  [ ] Внешняя публикация – только после явного «публикуй»"
echo
if [[ -f "$PATH_ARG" ]]; then
  echo "Quick scan (heuristic):"
  if command -v rg >/dev/null 2>&1; then
    hits="$(rg -n --ignore-case \
      'влито|gap → must|residual|Artifact Review Log|merge .+ ×|эволюция с [0-9]{4}|keyword-?кластер|fill rate|verbatim|friction KPI|opt-in|CSAT|сходимость|когорт|Если коротко|реально страдают|за кофе|Собрал Tech|на всякий|не репрезентатив|длинные пути|не оргсхема|цифра волны|не раздуваем|отдельный раздел не нужен|Кому хуже всего|В двух словах|В шапке:' \
      "$PATH_ARG" 2>/dev/null || true)"
    if [[ -n "$hits" ]]; then
      echo "  possible agent-meta / slop / chatty / kitchen:"
      echo "$hits" | sed 's/^/    /'
    else
      echo "  no obvious agent-meta / slop / chatty / kitchen markers"
    fi
    echo
    echo "  нейро-синтаксис (эвристика – смотреть глазами, не править слепо):"
    # эвристики шумят на таблицах, списках-определениях и frontmatter – отсекаем их
    neuro="$(rg -n --ignore-case \
      'вход в расчёт|оптика для|пересчёт в |пересчитывается|оформляется|заполняется|заказывают|считают |берётся|производится|осуществля|обеспечива|формирование|наличие |в целях|носит характер' \
      "$PATH_ARG" 2>/dev/null | rg -v '^[0-9]+:\|' || true)"
    joints="$(rg -n '^[^|>#*[:space:]-].*[–:].*–' "$PATH_ARG" 2>/dev/null \
      | rg -v '^[0-9]+:[a-z_]+:' | rg -v '^[0-9]+:`' | rg -v '\[[^]]*–' || true)"
    if [[ -n "$neuro" ]]; then
      echo "    безличное / отглагольное:"
      echo "$neuro" | head -8 | sed 's/^/      /'
    fi
    if [[ -n "$joints" ]]; then
      echo "    связки пунктуацией вместо союза:"
      echo "$joints" | head -8 | sed 's/^/      /'
    fi
    if [[ -z "$neuro" && -z "$joints" ]]; then
      echo "    чисто"
    fi
  else
    echo "  (rg not found – skip scan)"
  fi
  echo
  echo "Повторы (фразы от 5 слов, встречаются 2+ раз; таблицы, код и цитаты «Было» пропущены):"
  if command -v python3 >/dev/null 2>&1; then
    python3 "$(dirname "$0")/repeats.py" "$PATH_ARG" | sed 's/^/    /'
  else
    echo "    (python3 not found – skip scan)"
  fi
  echo
  echo "Шаблонные тики (частота конструкции выше порога – читается как машинный текст):"
  if command -v python3 >/dev/null 2>&1; then
    python3 "$(dirname "$0")/tics.py" "$PATH_ARG" | sed 's/^/    /'
  else
    echo "    (python3 not found – skip scan)"
  fi
else
  echo "Note: path not found on disk – checklist only"
fi
