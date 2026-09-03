# SDK → HTML/CSS/JS mapping (v1)

Reference: `~/.cursor/skills-cursor/canvas/sdk/index.d.ts`. Экспорт **transpiles** JSX tree в static markup – не React runtime.

## In-scope v1

| SDK | Static output | Notes |
| --- | --- | --- |
| `Stack` | `<div class="stack">` | `gap` → `--stack-gap` or `gap: Npx` |
| `Row` | `<div class="row">` | flex row; `align`, `justify`, `wrap` → CSS |
| `Grid` | `<div class="grid">` | `columns` → `grid-template-columns` |
| `Spacer` | `<div class="spacer">` | `flex: 1` |
| `Divider` | `<hr class="divider">` | `stroke.tertiary` color |
| `H1` / `H2` / `H3` | `<h1>` / `<h2>` / `<h3>` | typography from theme |
| `Text` | `<p>` or `<span>` | `tone`, `size`, `weight`, `italic` → CSS classes |
| `Code` | `<code>` | monospace, fill background |
| `Card` | `<section class="card">` | `variant`, `size`; collapsible → `<details>` or JS toggle |
| `CardHeader` | `<header class="card-header">` | plain text + optional `.trailing` |
| `CardBody` | `<div class="card-body">` | padding from tokens |
| `Stat` | `<div class="stat">` | `.stat-value` + `.stat-label`; `tone` → color class |
| `Table` | `<table class="table">` | `headers`, `rows`, `columnAlign`, `rowTone`, `striped`, `framed` |
| `BarChart` | inline `<svg class="chart bar-chart">` | categories + series from props; stacked/normalized/horizontal |
| `LineChart` | inline `<svg class="chart line-chart">` | polyline + optional area fill |
| `PieChart` | inline `<svg class="chart pie-chart">` | slices + optional donut center total |
| `UsageBar` | `<div class="usage-bar">` | segments as proportional spans |
| `useHostTheme()` | CSS vars in `:root` | always **light** palette – `theme-light.css` |

## Chart implementation notes

Charts in SDK are pure inline SVG – replicate in static HTML. Shared helpers: `scripts/canvas_export_lib.py`.

1. **BarChart** – compute bar positions from `categories`, `series`, `stacked`, `horizontal`, `normalized`; Y domain from data + `referenceLines`; **legend only if `series.length >= 2`**.
2. **`showValues` auto** (SDK default): on for single series with ≤8 categories; off otherwise; no effect on stacked/normalized. Print value labels on bar ends.
3. **`referenceLines`** – dashed marker + **chip** (rounded rect + label) at line end, not bare text.
4. **Bars** – slight top/end corner radius; semantic `tone` fills; single-series without tone → per-category palette.
5. **LineChart** – polyline points; optional area path with opacity fill; hover guide optional via `app.js`.
6. **PieChart** – arc paths from `data[].value`; `donut` → inner radius + center text sum.
7. **Tones** – map `success|danger|warning|info|neutral` to palette tokens (`canvasPalette{Dark,Light}` / category palettes).
8. **Theme** – default **light** (`:root`). Embed both palettes; toggle via `html[data-theme="dark|light"]` + corner button (`theme_toggle_html` / `html_document` in `canvas_export_lib.py`). Chart fills use `var(--tone-*)` / `var(--chart-cat-*)` so bars switch with theme.

**Do not use Chart.js / Highcharts / D3 CDN.** They implement a different visual language and cannot match Cursor Canvas SDK. Geometry stays in `canvas_export_lib.py` (or inline SVG).

## Partial / degraded mapping

| SDK | Static behavior |
| --- | --- |
| `Button` | `<button disabled>` or `<span class="btn btn--static">` – no onClick unless pure UI |
| `Link` | `<a href="…">` – only if href is literal in source; external links ok |
| `Pill` | Map if present – same tone classes as Stat |
| `Callout` | Flex row: tone icon (`calloutToneIconGlyph`) + tinted fill/border; not left-border-only |
| `useCanvasState(key, default)` | Default only, no persistence. Exception: closed set of views (pills) – bake all states inline and toggle with local JS |
| `useCanvasAction()` | **Drop** dispatch – remove or static text «IDE action unavailable in export» |

## Out-of-scope v1 (STOP unless user acks skip)

| SDK | Reason |
| --- | --- |
| `DiffView`, `DiffStats` | Complex diff engine |
| `TodoList`, `TodoListCard` | Interactive state |
| `CollapsibleSection` | Can add v1.1 with `<details>` |
| `Checkbox`, `Select`, `Toggle`, form controls | Interactive forms |
| `computeDAGLayout` + custom SVG graphs | Layout engine port – **degraded default:** bake node/edge coordinates into static SVG (no React layout). Full port – out of scope |
| `Swatch` alone | trivial – map if needed |
| npm imports, relative imports | Canvas rule – only `cursor/canvas`; if violated, STOP |

## Extraction algorithm

1. Parse JSX tree (manual or AST via `grep`/structured read – no mandatory tooling).
2. For each component node, emit HTML block per table above.
3. Lift string/number literals from props into HTML text or JSON blob.
4. Replace `theme.*` inline styles with `var(--…)` references.
5. Merge adjacent Text nodes into single elements where valid HTML.

## Theme token map (light)

| `useHostTheme()` path | CSS variable |
| --- | --- |
| `text.primary` | `--text-primary` |
| `text.secondary` | `--text-secondary` |
| `text.tertiary` | `--text-tertiary` |
| `bg.editor` | `--bg-editor` |
| `bg.elevated` | `--bg-elevated` |
| `fill.tertiary` | `--fill-tertiary` |
| `stroke.tertiary` | `--stroke-tertiary` |
| `accent.primary` | `--accent-primary` |
| `text.link` | `--text-link` |

Full values – `theme-light.css` (from `canvasPaletteLight` in SDK).
