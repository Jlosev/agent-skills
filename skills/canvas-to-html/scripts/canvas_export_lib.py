#!/usr/bin/env python3
"""Closer-to-SDK static render helpers for canvas-to-html.

Mirrors defaults from ~/.cursor/skills-cursor/canvas/sdk/*.d.ts
(showValues auto, reference-line chips, callout tone icons, chart tones).
No external chart libs — Canvas SDK is proprietary inline SVG; Chart.js/etc.
would look *different*, not closer.
"""
from __future__ import annotations

import html
from typing import Any

# Semantic tones (light / dark). Dark aligns with canvasPaletteDark + categoryPaletteDark.
TONES_LIGHT = {
    "success": "#1f8a65",
    "danger": "#cf2d56",
    "warning": "#b87500",
    "info": "#3685bf",
    "neutral": "#1414148a",
}
TONES_DARK = {
    "success": "#3fa266",
    "danger": "#fc6b83",
    "warning": "#f1b467",
    "info": "#7bafe9",
    "neutral": "#e4e4e48a",
}

# chartPalette (opaque-ish) for auto-assign when series has no tone
CHART_AUTO = [
    "#2E79B5E0",
    "#1F8A65E8",
    "#7B64B8F0",
    "#F0A040E0",
    "#C85898E0",
    "#5A6CC0F0",
    "#2A9A8AE0",
    "#E8C030E0",
    "#8888A8E0",
]

# Single-series per-category colors (SDK: different color by category)
CATEGORY_AUTO_DARK = [
    "#7BAFE9",
    "#3FA266",
    "#F1B467",
    "#9386F2",
    "#FC6B83",
    "#81A1C1",
    "#DD7F76",
    "#B48EAD",
]
CATEGORY_AUTO_LIGHT = [
    "#3685BF",
    "#1F8A65",
    "#C08532",
    "#7754D9",
    "#CF2D56",
    "#4C7F8C",
    "#D75C4E",
    "#B8448B",
]


def esc(s: object) -> str:
    return html.escape(str(s), quote=True)


def esc_text(s: object) -> str:
    return html.escape(str(s))


# Shared non-color tokens (identical in light/dark)
_THEME_SCALE = """
  --font-h1-size: 24px;
  --font-h1-line: 30px;
  --font-h2-size: 18px;
  --font-h2-line: 24px;
  --font-h3-size: 16px;
  --font-h3-line: 22px;
  --font-body-size: 14px;
  --font-body-line: 20px;
  --font-small-size: 12px;
  --font-small-line: 16px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
"""

_LIGHT_COLORS = """
  --text-primary: #141414f0;
  --text-secondary: #141414bd;
  --text-tertiary: #1414148a;
  --text-quaternary: #1414145c;
  --text-link: #3685bf;
  --text-on-accent: #fcfcfc;
  --bg-editor: #fcfcfc;
  --bg-chrome: #f8f8f8;
  --bg-elevated: #fcfcfc;
  --fill-primary: #14141433;
  --fill-secondary: #14141424;
  --fill-tertiary: #14141414;
  --fill-quaternary: #1414140f;
  --stroke-primary: #14141433;
  --stroke-secondary: #1414141f;
  --stroke-tertiary: #14141414;
  --accent-primary: #3685bf;
  --accent-control: #3685bf;
  --tone-success: #1f8a65;
  --tone-danger: #cf2d56;
  --tone-warning: #b87500;
  --tone-info: #3685bf;
  --tone-neutral: #1414148a;
  --chart-grid: #14141414;
  --chart-label: #1414148a;
  --chart-cat-0: #3685BF;
  --chart-cat-1: #1F8A65;
  --chart-cat-2: #C08532;
  --chart-cat-3: #7754D9;
  --chart-cat-4: #CF2D56;
  --chart-cat-5: #4C7F8C;
  --chart-cat-6: #D75C4E;
  --chart-cat-7: #B8448B;
  --tip-bg: #141414f0;
  --tip-fg: #fcfcfc;
"""

_DARK_COLORS = """
  --text-primary: #e4e4e4eb;
  --text-secondary: #e4e4e48d;
  --text-tertiary: #e4e4e45e;
  --text-quaternary: #e4e4e442;
  --text-link: #87c3ff;
  --text-on-accent: #191c22;
  --bg-editor: #181818;
  --bg-chrome: #141414;
  --bg-elevated: #181818;
  --fill-primary: #e4e4e430;
  --fill-secondary: #e4e4e41e;
  --fill-tertiary: #e4e4e411;
  --fill-quaternary: #e4e4e40a;
  --stroke-primary: #e4e4e433;
  --stroke-secondary: #e4e4e41f;
  --stroke-tertiary: #e4e4e414;
  --accent-primary: #599ce7;
  --accent-control: #599ce7;
  --tone-success: #3fa266;
  --tone-danger: #fc6b83;
  --tone-warning: #f1b467;
  --tone-info: #7bafe9;
  --tone-neutral: #e4e4e48a;
  --chart-grid: #e4e4e414;
  --chart-label: #e4e4e45e;
  --chart-cat-0: #7BAFE9;
  --chart-cat-1: #3FA266;
  --chart-cat-2: #F1B467;
  --chart-cat-3: #9386F2;
  --chart-cat-4: #FC6B83;
  --chart-cat-5: #81A1C1;
  --chart-cat-6: #DD7F76;
  --chart-cat-7: #B48EAD;
  --tip-bg: #e4e4e4f0;
  --tip-fg: #181818;
"""


def theme_css(default: str = "light") -> str:
    """Embed light + dark palettes. Default theme is light (`:root`).

    Toggle via `html[data-theme="dark"]` / `html[data-theme="light"]`.
    Chart fills use `var(--tone-*)` / `var(--chart-cat-*)` so they switch too.
    """
    # :root = light always (share-back default). data-theme overrides both ways.
    return f"""
:root {{
{_LIGHT_COLORS}
{_THEME_SCALE}
}}
html[data-theme="dark"] {{
{_DARK_COLORS}
}}
html[data-theme="light"] {{
{_LIGHT_COLORS}
}}
"""


def theme_toggle_html() -> str:
    """Fixed top-right light/dark control."""
    return """
<button type="button" class="theme-toggle" id="theme-toggle" aria-label="Переключить тему" title="Светлая / тёмная тема">
  <span class="theme-toggle__icon theme-toggle__icon--moon" aria-hidden="true">◐</span>
  <span class="theme-toggle__label">Тема</span>
</button>
"""


COMPONENT_CSS = """
*, *::before, *::after { box-sizing: border-box; }
body {
  margin: 0;
  padding: var(--space-6);
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  font-size: var(--font-body-size);
  line-height: var(--font-body-line);
  color: var(--text-primary);
  background: var(--bg-editor);
}
.page { max-width: 1000px; margin: 0 auto; padding: var(--space-5); --stack-gap: 22px; }
.stack { display: flex; flex-direction: column; gap: var(--stack-gap, var(--space-4)); }
.row { display: flex; flex-direction: row; gap: var(--row-gap, var(--space-2)); align-items: stretch; }
.row--wrap { flex-wrap: wrap; }
.divider { border: none; border-top: 1px solid var(--stroke-tertiary); margin: var(--space-2) 0; }
h1 { margin: 0; font-size: var(--font-h1-size); line-height: var(--font-h1-line); font-weight: 590; }
h2 { margin: 0; font-size: var(--font-h2-size); line-height: var(--font-h2-line); font-weight: 590; }
p { margin: 0; }
.caption { color: var(--text-tertiary); font-size: var(--font-small-size); line-height: var(--font-small-line); }
.text-small { font-size: var(--font-small-size); line-height: var(--font-small-line); }
.text-secondary { color: var(--text-secondary); }
.text-semibold { font-weight: 590; }

.theme-toggle {
  position: fixed;
  top: 12px;
  right: 12px;
  z-index: 50;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border: 1px solid var(--stroke-secondary);
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  font: 12px/1 system-ui, sans-serif;
  cursor: pointer;
}
.theme-toggle:hover { color: var(--text-primary); border-color: var(--stroke-primary); }
.theme-toggle__icon { font-size: 14px; line-height: 1; }

.card {
  border: 1px solid var(--stroke-secondary);
  border-radius: var(--radius-lg);
  background: var(--bg-elevated);
  overflow: hidden;
}
.card--flex { flex: 1; min-width: 280px; }
.card-header {
  padding: var(--space-2) var(--space-3);
  font-size: var(--font-small-size);
  color: var(--text-secondary);
  border-bottom: 1px solid var(--stroke-tertiary);
}
.card-body { padding: var(--space-4); }

.stat { min-width: 100px; }
.stat-value { font-size: var(--font-h2-size); font-weight: 590; line-height: var(--font-h2-line); }
.stat-label { font-size: var(--font-small-size); color: var(--text-secondary); margin-top: var(--space-1); }
.stat--success .stat-value { color: var(--tone-success); }
.stat--danger .stat-value { color: var(--tone-danger); }
.stat--warning .stat-value { color: var(--tone-warning); }
.stat--info .stat-value { color: var(--tone-info); }

.table { width: 100%; border-collapse: collapse; font-size: var(--font-body-size); }
.table th, .table td {
  padding: var(--space-2) var(--space-3);
  text-align: left;
  border-bottom: 1px solid var(--stroke-tertiary);
  vertical-align: top;
}
.table th { color: var(--text-secondary); font-weight: 590; }

.callout {
  display: flex;
  gap: var(--space-3);
  align-items: flex-start;
  border: 1px solid var(--stroke-secondary);
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-4);
  background: var(--fill-quaternary);
}
.callout-icon {
  flex: 0 0 auto;
  width: 18px;
  height: 18px;
  margin-top: 1px;
}
.callout-body { flex: 1; min-width: 0; }
.callout--info { background: color-mix(in srgb, var(--tone-info) 12%, transparent); border-color: color-mix(in srgb, var(--tone-info) 28%, var(--stroke-secondary)); }
.callout--success { background: color-mix(in srgb, var(--tone-success) 12%, transparent); border-color: color-mix(in srgb, var(--tone-success) 28%, var(--stroke-secondary)); }
.callout--warning { background: color-mix(in srgb, var(--tone-warning) 12%, transparent); border-color: color-mix(in srgb, var(--tone-warning) 28%, var(--stroke-secondary)); }
.callout--danger { background: color-mix(in srgb, var(--tone-danger) 12%, transparent); border-color: color-mix(in srgb, var(--tone-danger) 28%, var(--stroke-secondary)); }
.callout--neutral { background: var(--fill-quaternary); }

.legend {
  display: flex; flex-wrap: wrap; gap: var(--space-3);
  margin-bottom: var(--space-2);
  font-size: var(--font-small-size);
  color: var(--text-secondary);
}
.legend-item { display: flex; align-items: center; gap: 6px; }
.legend-swatch { width: 10px; height: 10px; border-radius: 2px; }
.chart-wrap { width: 100%; overflow-x: auto; }
.chart text { fill: var(--chart-label); font-size: 11px; font-family: system-ui, sans-serif; }
.chart .value-label { fill: var(--text-secondary); font-size: 11px; font-weight: 500; }
.chart .ref-chip-bg { fill: var(--bg-elevated); stroke: var(--stroke-secondary); }
.chart .ref-chip-text { font-size: 10px; font-weight: 590; }
"""


def tones(dark: bool = False) -> dict[str, str]:
    """Legacy hex map (prefer CSS vars via series_fill / tone_var)."""
    return TONES_DARK if dark else TONES_LIGHT


def tone_var(tone: str) -> str:
    return f"var(--tone-{tone})"


def series_fill(
    series: dict[str, Any],
    series_index: int,
    category_index: int,
    n_series: int,
) -> str:
    """Theme-aware fill — switches with data-theme via CSS variables."""
    tone = series.get("tone")
    if tone:
        return tone_var(tone)
    if n_series == 1:
        return f"var(--chart-cat-{category_index % 8})"
    return f"var(--chart-cat-{series_index % 8})"


def series_color(
    series: dict[str, Any],
    series_index: int,
    category_index: int,
    n_series: int,
    dark: bool = False,
) -> str:
    """Back-compat alias for series_fill (dark ignored — use CSS vars)."""
    return series_fill(series, series_index, category_index, n_series)


def tone_mean(m: float) -> str:
    if m >= 4.0:
        return "success"
    if m >= 3.0:
        return "warning"
    return "danger"


def bad_tone(b: float) -> str:
    if b >= 25:
        return "danger"
    if b >= 15:
        return "warning"
    return "success"


def format_value(v: float, prefix: str = "", suffix: str = "") -> str:
    if abs(v - round(v)) < 1e-9:
        body = str(int(round(v)))
    elif abs(v * 10 - round(v * 10)) < 1e-9:
        body = f"{v:.1f}"
    else:
        body = f"{v:.2f}".rstrip("0").rstrip(".")
    return f"{prefix}{body}{suffix}"


def should_show_values(
    series: list[dict[str, Any]],
    categories: list[str],
    *,
    show_values: bool | None,
    stacked: bool,
    normalized: bool,
) -> bool:
    """SDK default: auto on for single series with ≤8 categories; off for stacked."""
    if stacked or normalized:
        return False
    if show_values is True:
        return True
    if show_values is False:
        return False
    return len(series) == 1 and len(categories) <= 8


def _nice_ticks(y_min: float, y_max: float, count: int = 5) -> list[float]:
    if y_max <= y_min:
        return [y_min]
    span = y_max - y_min
    step = span / count
    # Prefer integers when domain is small integers
    if span <= 10 and y_min == int(y_min) and y_max == int(y_max):
        ticks = []
        v = y_min
        while v <= y_max + 1e-9:
            ticks.append(float(v))
            v += max(1, round(step)) or 1
        if ticks[-1] < y_max:
            ticks.append(float(y_max))
        return ticks
    return [y_min + span * i / count for i in range(count + 1)]


def _rounded_bar_path(x: float, y: float, w: float, h: float, r: float = 3.0) -> str:
    """Vertical bar with top corners rounded (SDK-like)."""
    if h <= 0 or w <= 0:
        return ""
    r = min(r, w / 2, h)
    # path: bottom-left → bottom-right → top-right arc → top-left arc → close
    return (
        f"M{x:.1f},{y + h:.1f} "
        f"L{x + w:.1f},{y + h:.1f} "
        f"L{x + w:.1f},{y + r:.1f} "
        f"Q{x + w:.1f},{y:.1f} {x + w - r:.1f},{y:.1f} "
        f"L{x + r:.1f},{y:.1f} "
        f"Q{x:.1f},{y:.1f} {x:.1f},{y + r:.1f} Z"
    )


def _rounded_hbar_path(x: float, y: float, w: float, h: float, r: float = 3.0) -> str:
    """Horizontal bar with right corners rounded."""
    if h <= 0 or w <= 0:
        return ""
    r = min(r, h / 2, w)
    return (
        f"M{x:.1f},{y:.1f} "
        f"L{x + w - r:.1f},{y:.1f} "
        f"Q{x + w:.1f},{y:.1f} {x + w:.1f},{y + r:.1f} "
        f"L{x + w:.1f},{y + h - r:.1f} "
        f"Q{x + w:.1f},{y + h:.1f} {x + w - r:.1f},{y + h:.1f} "
        f"L{x:.1f},{y + h:.1f} Z"
    )


def bar_chart(
    categories: list[str],
    series: list[dict[str, Any]],
    *,
    height: int = 240,
    y_min: float | None = None,
    y_max: float | None = None,
    begin_at_zero: bool = True,
    horizontal: bool = False,
    stacked: bool = False,
    normalized: bool = False,
    reference_lines: list[dict[str, Any]] | None = None,
    show_values: bool | None = None,
    value_prefix: str = "",
    value_suffix: str = "",
    width: int = 920,
    dark: bool = False,
) -> str:
    reference_lines = reference_lines or []
    n_ser = len(series)
    n_cat = len(categories)
    del dark  # colors are CSS vars — theme toggle switches them

    all_vals: list[float] = []
    for s in series:
        all_vals.extend(float(v) for v in s["data"])
    for rl in reference_lines:
        all_vals.append(float(rl["value"]))

    if y_min is None:
        y_min = 0.0 if begin_at_zero else min(all_vals)
    if y_max is None:
        y_max = max(all_vals) * 1.08 if all_vals else 1.0
    # room for value labels on top
    show_vals = should_show_values(
        series, categories, show_values=show_values, stacked=stacked, normalized=normalized
    )
    if show_vals and not horizontal:
        y_max = y_max * 1.06 if y_max > 0 else y_max + 0.2

    pad_l = 44 if not horizontal else 128
    pad_r = 20
    pad_t = 20 if show_vals and not horizontal else 14
    pad_b = 48 if not horizontal else 30
    # extra right pad for ref chips
    if reference_lines and not horizontal:
        pad_r = 72
    if reference_lines and horizontal:
        pad_t = 28

    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b
    grid = "var(--chart-grid)"

    parts: list[str] = [
        f'<svg class="chart bar-chart" viewBox="0 0 {width} {height}" '
        f'width="100%" height="{height}" role="img">'
    ]

    # Legend only for 2+ series (SDK)
    legend_html = ""
    if n_ser >= 2:
        legend_html = '<div class="legend">'
        for si, s in enumerate(series):
            c = series_fill(s, si, 0, n_ser)
            legend_html += (
                f'<span class="legend-item"><span class="legend-swatch" '
                f'style="background:{c}"></span>{esc_text(s["name"])}</span>'
            )
        legend_html += "</div>"

    ticks = _nice_ticks(y_min, y_max, 4)

    def map_val(val: float) -> float:
        return (val - y_min) / (y_max - y_min) if y_max != y_min else 0.0

    if not horizontal:
        for val in ticks:
            y = pad_t + plot_h - map_val(val) * plot_h
            parts.append(
                f'<line x1="{pad_l}" y1="{y:.1f}" x2="{pad_l + plot_w}" y2="{y:.1f}" '
                f'stroke="{grid}" stroke-width="1" />'
            )
            lab = format_value(val)
            parts.append(
                f'<text x="{pad_l - 8}" y="{y + 3.5:.1f}" text-anchor="end">{lab}</text>'
            )

        for rl in reference_lines:
            val = float(rl["value"])
            y = pad_t + plot_h - map_val(val) * plot_h
            c = tone_var(rl.get("tone") or "neutral")
            parts.append(
                f'<line x1="{pad_l}" y1="{y:.1f}" x2="{pad_l + plot_w}" y2="{y:.1f}" '
                f'stroke="{c}" stroke-width="1.5" stroke-dasharray="5 4" />'
            )
            label = rl.get("label") or ""
            if label:
                # chip at line end (SDK: "chip at the line's end")
                chip_w = max(28, len(label) * 6.2 + 12)
                chip_h = 16
                chip_x = pad_l + plot_w - chip_w
                chip_y = y - chip_h / 2
                parts.append(
                    f'<rect class="ref-chip-bg" x="{chip_x:.1f}" y="{chip_y:.1f}" '
                    f'width="{chip_w:.1f}" height="{chip_h}" rx="3" stroke="{c}" stroke-width="1" />'
                )
                parts.append(
                    f'<text class="ref-chip-text" x="{chip_x + chip_w / 2:.1f}" '
                    f'y="{y + 3.5:.1f}" text-anchor="middle" fill="{c}">{esc_text(label)}</text>'
                )

        group_w = plot_w / max(n_cat, 1)
        inner = group_w * 0.72
        bar_w = inner / max(n_ser, 1)
        gap = bar_w * 0.12
        usable = bar_w - gap

        for ci, cat in enumerate(categories):
            group_x = pad_l + ci * group_w + (group_w - inner) / 2
            for si, s in enumerate(series):
                val = float(s["data"][ci])
                bh = map_val(val) * plot_h
                x = group_x + si * bar_w
                y = pad_t + plot_h - bh
                c = series_fill(s, si, ci, n_ser)
                path = _rounded_bar_path(x, y, usable, bh)
                if path:
                    tip = f"{cat}: {format_value(val, value_prefix, value_suffix)}"
                    parts.append(
                        f'<path d="{path}" fill="{c}" data-tip="{esc(tip)}" />'
                    )
                if show_vals:
                    label = format_value(val, value_prefix, value_suffix)
                    parts.append(
                        f'<text class="value-label" x="{x + usable / 2:.1f}" '
                        f'y="{y - 4:.1f}" text-anchor="middle">{esc_text(label)}</text>'
                    )
            cx = pad_l + ci * group_w + group_w / 2
            # wrap-ish: allow longer labels; truncate only if very long
            lab = cat if len(cat) <= 18 else cat[:16] + "…"
            parts.append(
                f'<text x="{cx:.1f}" y="{height - 14}" text-anchor="middle">{esc_text(lab)}</text>'
            )
    else:
        for val in ticks:
            x = pad_l + map_val(val) * plot_w
            parts.append(
                f'<line x1="{x:.1f}" y1="{pad_t}" x2="{x:.1f}" y2="{pad_t + plot_h}" '
                f'stroke="{grid}" stroke-width="1" />'
            )
            parts.append(
                f'<text x="{x:.1f}" y="{height - 10}" text-anchor="middle">'
                f"{format_value(val)}</text>"
            )

        for rl in reference_lines:
            val = float(rl["value"])
            x = pad_l + map_val(val) * plot_w
            c = tone_var(rl.get("tone") or "neutral")
            parts.append(
                f'<line x1="{x:.1f}" y1="{pad_t}" x2="{x:.1f}" y2="{pad_t + plot_h}" '
                f'stroke="{c}" stroke-width="1.5" stroke-dasharray="5 4" />'
            )
            label = rl.get("label") or ""
            if label:
                chip_w = max(28, len(label) * 6.2 + 12)
                chip_h = 16
                chip_x = x - chip_w / 2
                chip_y = pad_t - chip_h - 2
                parts.append(
                    f'<rect class="ref-chip-bg" x="{chip_x:.1f}" y="{chip_y:.1f}" '
                    f'width="{chip_w:.1f}" height="{chip_h}" rx="3" stroke="{c}" stroke-width="1" />'
                )
                parts.append(
                    f'<text class="ref-chip-text" x="{x:.1f}" y="{chip_y + 11.5:.1f}" '
                    f'text-anchor="middle" fill="{c}">{esc_text(label)}</text>'
                )

        row_h = plot_h / max(n_cat, 1)
        bar_h = (row_h * 0.7) / max(n_ser, 1)
        for ci, cat in enumerate(categories):
            row_y = pad_t + ci * row_h + (row_h - bar_h * n_ser) / 2
            parts.append(
                f'<text x="{pad_l - 8}" y="{pad_t + ci * row_h + row_h / 2 + 4:.1f}" '
                f'text-anchor="end">{esc_text(cat)}</text>'
            )
            for si, s in enumerate(series):
                val = float(s["data"][ci])
                bw = map_val(val) * plot_w
                y = row_y + si * bar_h
                c = series_fill(s, si, ci, n_ser)
                path = _rounded_hbar_path(pad_l, y, bw, bar_h * 0.88)
                if path:
                    tip = f"{cat} · {s['name']}: {format_value(val, value_prefix, value_suffix)}"
                    parts.append(
                        f'<path d="{path}" fill="{c}" data-tip="{esc(tip)}" />'
                    )
                if show_vals and n_ser == 1:
                    label = format_value(val, value_prefix, value_suffix)
                    lx = pad_l + bw + 4
                    parts.append(
                        f'<text class="value-label" x="{lx:.1f}" y="{y + bar_h * 0.55:.1f}" '
                        f'text-anchor="start">{esc_text(label)}</text>'
                    )

    parts.append("</svg>")
    return legend_html + '<div class="chart-wrap">' + "".join(parts) + "</div>"


# Lucide-like paths matching calloutToneIconGlyph intents
_CALLOUT_ICONS = {
    "info": (
        # info circle
        '<circle cx="9" cy="9" r="7.25" fill="none" stroke="currentColor" stroke-width="1.5"/>'
        '<path d="M9 8.2v4.2M9 5.8h.01" fill="none" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round"/>'
    ),
    "warning": (
        # triangle
        '<path d="M9 2.8 15.8 14.5H2.2L9 2.8z" fill="none" stroke="currentColor" '
        'stroke-width="1.5" stroke-linejoin="round"/>'
        '<path d="M9 7.2v3.2M9 12.3h.01" fill="none" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round"/>'
    ),
    "success": (
        # circles-check
        '<circle cx="9" cy="9" r="7.25" fill="none" stroke="currentColor" stroke-width="1.5"/>'
        '<path d="M5.8 9.2 8 11.3l4.4-4.6" fill="none" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
    ),
    "danger": (
        # exclamation-circle
        '<circle cx="9" cy="9" r="7.25" fill="none" stroke="currentColor" stroke-width="1.5"/>'
        '<path d="M9 5.5v4.2M9 12.3h.01" fill="none" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round"/>'
    ),
}

_TONE_ICON = {
    "info": "info",
    "success": "success",
    "warning": "warning",
    "danger": "danger",
}


def callout_icon_svg(tone: str) -> str:
    if tone == "neutral":
        return ""
    glyph = _TONE_ICON.get(tone, "info")
    paths = _CALLOUT_ICONS[glyph]
    color = f"var(--tone-{tone})"
    return (
        f'<svg class="callout-icon" viewBox="0 0 18 18" width="18" height="18" '
        f'aria-hidden="true" style="color:{color}">{paths}</svg>'
    )


def callout(tone: str, inner: str) -> str:
    icon = callout_icon_svg(tone)
    return (
        f'<div class="callout callout--{tone}">'
        f"{icon}"
        f'<div class="callout-body stack" style="--stack-gap:4px">{inner}</div>'
        f"</div>"
    )


def stat(label: str, value: object, tone: str | None = None) -> str:
    cls = f"stat stat--{tone}" if tone else "stat"
    return (
        f'<div class="{cls}"><div class="stat-value">{esc_text(value)}</div>'
        f'<div class="stat-label">{esc_text(label)}</div></div>'
    )


def caption(text: str) -> str:
    return f'<p class="caption">{esc_text(text)}</p>'


def text_small(text: str, weight: str | None = None, tone: str | None = None) -> str:
    classes = ["text-small"]
    if weight == "semibold":
        classes.append("text-semibold")
    if tone == "secondary":
        classes.append("text-secondary")
    return f'<p class="{" ".join(classes)}">{esc_text(text)}</p>'


def text_semibold(text: str, size: str | None = None) -> str:
    classes = ["text-semibold"]
    if size == "small":
        classes.append("text-small")
    return f'<p class="{" ".join(classes)}">{esc_text(text)}</p>'


def card(header: str, body: str, flex: bool = False) -> str:
    cls = "card card--flex" if flex else "card"
    return (
        f'<section class="{cls}"><header class="card-header">{esc_text(header)}</header>'
        f'<div class="card-body">{body}</div></section>'
    )


def table(headers: list[str], rows: list[list[str]]) -> str:
    th = "".join(f"<th>{esc_text(h)}</th>" for h in headers)
    trs = []
    for row in rows:
        tds = "".join(f"<td>{esc_text(c)}</td>" for c in row)
        trs.append(f"<tr>{tds}</tr>")
    return (
        f'<table class="table"><thead><tr>{th}</tr></thead>'
        f'<tbody>{"".join(trs)}</tbody></table>'
    )


APP_JS = """// Theme toggle (light default) + hover tips for chart marks
(function () {
  var root = document.documentElement;
  var KEY = 'canvas-export-theme';

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme === 'dark' ? 'dark' : 'light');
    try { localStorage.setItem(KEY, theme === 'dark' ? 'dark' : 'light'); } catch (e) {}
  }

  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  applyTheme(saved === 'dark' ? 'dark' : 'light');

  var btn = document.getElementById('theme-toggle');
  if (btn) {
    btn.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      applyTheme(next);
    });
  }

  var tip = document.createElement('div');
  tip.id = 'chart-tip';
  tip.style.cssText = 'position:fixed;display:none;z-index:10;padding:4px 8px;font:12px system-ui;background:var(--tip-bg);color:var(--tip-fg);border-radius:4px;pointer-events:none;max-width:280px;';
  document.body.appendChild(tip);
  document.querySelectorAll('[data-tip]').forEach(function (el) {
    el.addEventListener('mouseenter', function () {
      tip.textContent = el.getAttribute('data-tip');
      tip.style.display = 'block';
    });
    el.addEventListener('mousemove', function (e) {
      tip.style.left = (e.clientX + 12) + 'px';
      tip.style.top = (e.clientY + 12) + 'px';
    });
    el.addEventListener('mouseleave', function () {
      tip.style.display = 'none';
    });
  });
})();
"""


def html_document(title: str, body: str) -> str:
    """Full page: light default, both themes in CSS, corner toggle."""
    return f"""<!DOCTYPE html>
<html lang="ru" data-theme="light">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc_text(title)}</title>
  <link rel="stylesheet" href="./styles.css" />
</head>
<body>
  {theme_toggle_html()}
  <main class="page stack">
{body}
  </main>
  <script src="./app.js"></script>
</body>
</html>
"""

