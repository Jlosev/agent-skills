#!/usr/bin/env python3
"""Речевые тики: шаблон, повторённый столько раз, что читается как машинный.

Лексика может быть чистой, а текст всё равно звучит сгенерированным – из-за
одной и той же конструкции, взятой шаблоном. Считаю частоту и сравниваю с
порогом, за которым приём перестаёт быть приёмом. Порог – не запрет: решает
человек, скрипт только показывает счёт.

Выход всегда 0 – это подсказка к чтению, не гейт.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

# name -> (regex, порог «дальше это тик»)
TICS: dict[str, tuple[str, int]] = {
    'антитеза «X, а не Y»': (r'(?:,\s*а не\b|\bне\s[^,.]{2,40},\s+а\b)', 3),
    'связка-костыль «Значит / Поэтому / Отсюда / то есть»': (
        r'(?:^|[.:;–]\s)(?:Значит|значит|то есть|Отсюда|Поэтому)\b',
        4,
    ),
    'ярлык-двоеточие «Есть: / Нет: / Не закрыто:»': (
        r'(?:^|\s)(?:Есть|Нет|Не закрыто|Известно другое|Факт):\s',
        3,
    ),
    'одинаковый хвост пунктов «Контроль – …»': (r'Контроль\s+–', 3),
    'разговорное «болит / просаживается / проседает»': (
        r'(?:боли[тм]|просаживается|проседает|рв[её]тся|тянет вниз)',
        3,
    ),
}

NUM = re.compile(r'\b\d{1,3}(?:[.,]\d+)?\s?%|\b\d\.\d{2}\b')


def body_of(text: str) -> str:
    return text.split('---', 2)[2] if text.startswith('---') else text


def main() -> None:
    if len(sys.argv) < 2:
        print('usage: tics.py <path.md>', file=sys.stderr)
        raise SystemExit(2)

    text = Path(sys.argv[1]).read_text(encoding='utf-8')
    body = body_of(text)

    flagged = False
    for name, (rx, limit) in TICS.items():
        n = len(re.findall(rx, body, flags=re.M))
        if n > limit:
            flagged = True
            print(f'{n:3}× (порог {limit}) {name}')
    if not flagged:
        print('  шаблонных тиков выше порога нет')

    # одно и то же число в разных секциях = факт живёт в двух местах
    section, per_num = '(лид)', defaultdict(set)
    for line in body.splitlines():
        if line.startswith('#'):
            section = line.lstrip('# ').strip()
            continue
        if line.lstrip().startswith('|'):
            continue
        for val in NUM.findall(line):
            per_num[val.replace(' ', '')].add(section)

    spread = {v: s for v, s in per_num.items() if len(s) > 1}
    if spread:
        print('\nчисло повторено в разных разделах – факт должен остаться в одном:')
        for val, secs in sorted(spread.items(), key=lambda kv: -len(kv[1])):
            print(f'  {val:>6}  {" | ".join(sorted(secs))}')


if __name__ == '__main__':
    main()
