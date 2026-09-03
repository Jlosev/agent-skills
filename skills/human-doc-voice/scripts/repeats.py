#!/usr/bin/env python3
"""Ищет повторяющиеся фразы в читательском теле документа. Только stdout, файл не меняет."""
import collections
import re
import sys

MIN_WORDS = 5
MAX_REPORT = 10


SCAFFOLD = re.compile(r"^\*\*(Действие|Было|Станет)\b")
NOT_FOR_READER = re.compile(r"^#{1,6}\s.*\((не для CF|internal|служебн\w*)\)", re.IGNORECASE)


def reader_body(lines):
    """Читательское тело: без кода, таблиц, frontmatter, служебных блоков патча и цитат «Было»."""
    body, in_code, in_front, skip_quote = [], False, False, False
    for i, raw in enumerate(lines):
        line = raw.strip()
        if i == 0 and line == "---":
            in_front = True
            continue
        if in_front:
            in_front = line != "---"
            continue
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code or line.startswith("|"):
            continue
        if NOT_FOR_READER.match(line):
            break
        if SCAFFOLD.match(line):
            skip_quote = line.startswith("**Было")
            continue
        if skip_quote:
            if not line or line.startswith(">"):
                continue
            skip_quote = False
        body.append(line)
    return body


def words_of(body):
    text = " ".join(body).lower()
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.findall(r"[^\W_]+", text, flags=re.UNICODE)


def repeated_phrases(words):
    shingles = collections.Counter(
        " ".join(words[i : i + MIN_WORDS]) for i in range(len(words) - MIN_WORDS + 1)
    )
    starts = [
        i
        for i in range(len(words) - MIN_WORDS + 1)
        if shingles[" ".join(words[i : i + MIN_WORDS])] > 1
    ]
    # соседние вхождения – одна длинная фраза, а не N пересекающихся
    groups = []
    for i in starts:
        if groups and i <= groups[-1][1] + 1:
            groups[-1][1] = i
        else:
            groups.append([i, i])
    found = collections.Counter(
        " ".join(words[a : b + MIN_WORDS]) for a, b in groups
    )
    return [(phrase, n) for phrase, n in found.items() if n > 1]


def main():
    if len(sys.argv) < 2:
        print("usage: repeats.py <path>", file=sys.stderr)
        return 2
    try:
        with open(sys.argv[1], encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as err:
        print(f"не прочитать файл: {err}")
        return 0

    found = repeated_phrases(words_of(reader_body(lines)))
    if not found:
        print("повторов не найдено")
        return 0

    found.sort(key=lambda item: (-len(item[0].split()), -item[1]))
    for phrase, count in found[:MAX_REPORT]:
        print(f"{count}× «{phrase}»")
    if len(found) > MAX_REPORT:
        print(f"… ещё {len(found) - MAX_REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
