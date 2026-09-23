#!/usr/bin/env python3
"""Строки с пустыми оборотами из lexicon.txt. Код в fence пропускается."""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 3:
        print("usage: lexicon_scan.py <path> <lexicon.txt>", file=sys.stderr)
        raise SystemExit(2)
    path, lex_path = Path(sys.argv[1]), Path(sys.argv[2])
    phrases = []
    for raw in lex_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        phrases.append(line.lower())
    in_fence = False
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if raw.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        low = raw.lower()
        for phrase in phrases:
            if phrase in low:
                print(f"{n}: {raw.strip()} ← {phrase}")
                break


if __name__ == "__main__":
    main()
