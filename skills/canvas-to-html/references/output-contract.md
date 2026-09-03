# Output contract – static prototype directory

Минимальный контракт выходной директории. Совместим с локальным `file://` и любым static host.

## Directory layout

```text
<output-dir>/
  index.html          # required – single entrypoint
  styles.css          # required – theme + components
  app.js              # optional – chart hover, collapsible sections
  assets/             # optional – only when SVG/binary too large for inline
    chart-*.svg
```

## index.html rules

| Rule | Requirement |
| --- | --- |
| Entry | Always named `index.html` at output root |
| Asset refs | Relative only – `./styles.css`, `./app.js`, `./assets/…` |
| Forbidden | Absolute paths `/…`, protocol-relative `//…`, external CDN |
| Data | Inline in HTML, `<script type="application/json">`, or const in `app.js` |
| Network | No `fetch`, XHR, WebSocket, import maps to remote URLs |
| Meta | `charset=utf-8`, viewport for mobile-readable dashboards |
| Title | From canvas H1 or `{CANVAS_STEM}` |

## styles.css rules

- CSS custom properties for theme – see `theme-light.css`
- No `@import` from external URLs
- Flat surfaces – no box-shadow (match canvas slop rules)
- System font stack – no external web fonts required

## app.js rules (optional)

- Vanilla JS only – no bundler required at runtime
- Self-contained in output dir
- Chart hover/tooltips – pointer events on inline SVG
- No module imports from CDN

## Verification checklist

Запуск из workspace:

```bash
bash .agents/skills/canvas-to-html/scripts/verify_export.sh "<output-dir>"
```

Exit 0 = pass. Ручной чеклист:

- [ ] `index.html` exists
- [ ] Opens in browser without console network errors
- [ ] All `href`/`src` are `./…`, `#…`, or `data:…`
- [ ] No `fetch(` in any output file
- [ ] Charts render without external libs
- [ ] Tables and text readable on light background

## Anti-patterns

- `href="/styles.css"` – breaks when served under a path prefix
- `<script src="https://cdn.jsdelivr.net/…">` – forbidden
