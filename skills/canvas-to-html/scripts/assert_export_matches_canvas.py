#!/usr/bin/env python3
"""Fail if static export HTML does not contain key strings from the live .canvas.tsx.

Prevents publishing a stale hand-ported one-off exporter while the canvas moved on.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def extract_h1(canvas: str) -> str | None:
    m = re.search(r"<H1>\s*([^<{]+?)\s*</H1>", canvas)
    if not m:
        return None
    return re.sub(r"\s+", " ", m.group(1)).strip()


def extract_first_captions(canvas: str, n: int = 2) -> list[str]:
    """Caption>{text}</Caption> or <Caption>\n text \n</Caption>."""
    found: list[str] = []
    for m in re.finditer(
        r"<Caption>\s*([^<{]+?)\s*</Caption>",
        canvas,
        flags=re.S,
    ):
        t = re.sub(r"\s+", " ", m.group(1)).strip()
        if len(t) >= 24:
            found.append(t)
        if len(found) >= n:
            break
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("canvas", type=Path)
    ap.add_argument("export_dir", type=Path)
    args = ap.parse_args()

    canvas_text = args.canvas.read_text(encoding="utf-8")
    html_path = args.export_dir / "index.html"
    if not html_path.is_file():
        print(f"FAIL: missing {html_path}", file=sys.stderr)
        return 1
    html = html_path.read_text(encoding="utf-8")

    h1 = extract_h1(canvas_text)
    if not h1:
        print("FAIL: could not extract <H1> from canvas", file=sys.stderr)
        return 1

    checks = [("H1", h1)]
    for i, cap in enumerate(extract_first_captions(canvas_text, 2), 1):
        # use a distinctive slice – full caption may wrap differently in HTML
        slice_ = cap[:80] if len(cap) > 80 else cap
        checks.append((f"Caption[{i}][:80]", slice_))

    failed = False
    for label, needle in checks:
        if needle not in html:
            print(f"FAIL: {label} from canvas not found in index.html", file=sys.stderr)
            print(f"  expected to contain: {needle!r}", file=sys.stderr)
            failed = True
        else:
            print(f"OK: {label}")

    if failed:
        print(
            "\nExport is STALE relative to canvas. Re-port the one-off exporter "
            "from the current .canvas.tsx (do not upload).",
            file=sys.stderr,
        )
        return 1

    print(f"Freshness OK: {args.export_dir} matches {args.canvas.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
