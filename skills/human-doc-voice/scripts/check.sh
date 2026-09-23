#!/usr/bin/env bash
# human-doc-voice checklist – stdout only; does not edit files.
set -euo pipefail

PATH_ARG="${1:-}"
if [[ -z "$PATH_ARG" ]]; then
  echo "usage: check.sh <path>" >&2
  exit 2
fi

DIR="$(dirname "$0")"

echo "human-doc-voice checklist: $PATH_ARG"
echo
echo "Тест"
echo "  [ ] Текст прочитает человек, чтобы понять или сделать шаг"
echo "  [ ] Не чат, не заметка агента себе, не код"
echo
echo "Режим"
echo "  [ ] Править сразу. Ясный фрагмент не переписывать"
echo "  [ ] После точечной правки – тот же паттерн по всему тексту"
echo "  [ ] Факт, модальность и часть числа как в источнике"
echo
echo "Читатель"
echo "  [ ] Суть в начале текста и раздела"
echo "  [ ] Заголовок называет содержание, без знания того, как текст собирали"
echo "  [ ] Оговорка нужна, чтобы факт не прочитался неверно, или её нет"
echo "  [ ] Нет истории документа: «что выяснили», «по итогам обсуждения»"
echo
echo "Один факт – одно место"
echo "  [ ] Один и тот же факт не стоит в двух формах (абзац, список, таблица, подпись, пример)"
echo "  [ ] Одна сущность – одно имя"
echo "  [ ] Патч к живой странице прочитан вместе с нетронутым текстом"
echo
echo "Слоп"
echo "  [ ] Нет пустых оборотов из lexicon.txt"
echo "  [ ] В абзаце меньше трёх выделений"
echo "  [ ] У действия назван тот, кто действует"
echo "  [ ] Модальность («может», «должен», «согласовано») не вычищена и не усилена"
echo
if [[ -f "$PATH_ARG" ]]; then
  echo "Quick scan (heuristic):"
  if command -v python3 >/dev/null 2>&1; then
    lex_hits="$(python3 "$DIR/lexicon_scan.py" "$PATH_ARG" "$DIR/lexicon.txt" || true)"
    if [[ -n "$lex_hits" ]]; then
      echo "  lexicon:"
      echo "$lex_hits" | sed 's/^/    /'
    else
      echo "  lexicon: нет"
    fi
    echo
    bold_hits="$(python3 "$DIR/emphasis_scan.py" "$PATH_ARG" || true)"
    if [[ -n "$bold_hits" ]]; then
      echo "  выделения (3+ в абзаце):"
      echo "$bold_hits" | sed 's/^/    /'
    else
      echo "  выделения: нет абзацев с тремя и больше"
    fi
  else
    echo "  (python3 not found – skip lexicon and emphasis)"
  fi
  echo
  if command -v rg >/dev/null 2>&1; then
    hits="$(rg -n --ignore-case \
      'влито|gap → must|residual|Artifact Review Log|keyword-?кластер|fill rate|verbatim|Если коротко|на всякий|отдельный раздел не нужен|что выяснили|по итогам обсуждения' \
      "$PATH_ARG" 2>/dev/null || true)"
    if [[ -n "$hits" ]]; then
      echo "  possible kitchen / history:"
      echo "$hits" | sed 's/^/    /'
    else
      echo "  no obvious kitchen / history markers"
    fi
    echo
    echo "  нейро-синтаксис (эвристика – смотреть глазами, не править слепо):"
    neuro="$(rg -n --ignore-case \
      'вход в расчёт|пересчёт в |пересчитывается|оформляется|заполняется|производится|осуществля|формирование |носит характер' \
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
    python3 "$DIR/repeats.py" "$PATH_ARG" | sed 's/^/    /'
  else
    echo "    (python3 not found – skip scan)"
  fi
  echo
  echo "Шаблонные тики (частота конструкции выше порога – читается как машинный текст):"
  if command -v python3 >/dev/null 2>&1; then
    python3 "$DIR/tics.py" "$PATH_ARG" | sed 's/^/    /'
  else
    echo "    (python3 not found – skip scan)"
  fi
else
  echo "Note: path not found on disk – checklist only"
fi
