#!/usr/bin/env python3
"""Абзацы с тремя и больше выделениями. Код в fence пропускается."""
from __future__ import annotations

import re
import sys
from pathlib import Path

BOLD = re.compile(r"\*\*[^*\n]+\*\*|__[^_\n]+__")


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: emphasis_scan.py <path>", file=sys.stderr)
        raise SystemExit(2)
    lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
    in_fence = False
    buf: list[str] = []
    start: int | None = None

    def flush() -> None:
        nonlocal buf, start
        if buf and start is not None:
            body = " ".join(buf)
            n = len(BOLD.findall(body))
            if n >= 3:
                print(f"{start}: {n} выделений ← {body[:90]}")
        buf = []
        start = None

    for n, raw in enumerate(lines, 1):
        if raw.strip().startswith("```"):
            in_fence = not in_fence
            flush()
            continue
        if in_fence or not raw.strip():
            flush()
            continue
        if start is None:
            start = n
        buf.append(raw.strip())
    flush()


if __name__ == "__main__":
    main()
