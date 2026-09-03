---
created: 2026-09-03
updated: 2026-09-03

# Canvas to HTML

Exports one Cursor Canvas (`.canvas.tsx`) to a standalone static directory (`index.html` + local CSS/JS).

`{SKILL_DIR}` = directory of this SKILL.md.

## Scope

In: one `.canvas.tsx` (path or name under `~/.cursor/projects/<ws>/canvases/`); map `cursor/canvas` SDK → HTML/CSS/JS; inline/self-hosted charts; neutral light theme  
Out: editing the canvas in the IDE; generating a canvas from scratch; wiki/CMS publish; interactivity that needs Cursor runtime (`useCanvasAction`, fetch)  
Fallback: unsupported component → STOP + unsupported list; canvas not found → ask for a path

## Gotchas

- **Output format.** Entrypoint `index.html`, asset paths only relative (`./styles.css`, `./app.js`), no absolute `/foo.css`.
- **Data inline.** No `fetch()`, no external CDN for JS/CSS/charts. Charts – inline SVG or self-hosted `.js` in the output dir.
- **Theme.** Default **light**. Export embeds light **and** dark tokens; a «Theme» button toggles `html[data-theme]`.
- **Canvas runtime hooks.** `useCanvasAction` – drop or a static stub. `useCanvasState` – freeze default values from source.
- **SDK surface.** Full API – `~/.cursor/skills-cursor/canvas/sdk/index.d.ts`. In-scope v1 – `references/sdk-mapping.md`. `computeDAGLayout` → baked SVG; other out-of-scope without fallback → STOP + ack.
- **One canvas → one output dir.** No monorepo, no extra entrypoints unless asked.

## Preconditions

- [ ] Path to `*.canvas.tsx` **or** a canvas name (no extension) to search in `canvases/`.
- [ ] Canvas source readable (Read).
- [ ] Read `references/sdk-mapping.md` and `references/output-contract.md`.

## Failure modes

| Mode | Action |
| --- | --- |
| Canvas not found | STOP, ask for a full path |
| Read failed | STOP |
| Out-of-scope SDK without fallback | STOP, list unsupported; wait for ack on a degraded export. Exception: `computeDAGLayout` + custom SVG → baked coordinates (degraded OK without ack) |
| `{OUTPUT_DIR}` exists and is not empty | STOP, ask ack to overwrite |
| `verify_export.sh` exit ≠ 0 | STOP, fix output to the contract |

## Algorithm

### Step 0: Resolve input

| Input | Action |
| --- | --- |
| Absolute/relative path to `*.canvas.tsx` | `Read` the file |
| Canvas name (kebab-case) | search `~/.cursor/projects/*/canvases/<name>.canvas.tsx`; if several workspaces – ask |
| Not found | STOP, ask for a full path |

Lock `{CANVAS_PATH}`, `{CANVAS_STEM}`, `{OUTPUT_DIR}` (default `.tmp/canvas-export/{CANVAS_STEM}/` or a user path).

If `{OUTPUT_DIR}` exists and is not empty – **STOP**, ask overwrite ack before Step 2.

### Step 1: Analyze canvas source

1. `Read` `{CANVAS_PATH}` whole.
2. Extract inline data, `cursor/canvas` imports, hooks.
3. Match imports to **In-scope v1** in `references/sdk-mapping.md`.
4. If **Out-of-scope v1** without fallback – **STOP**.

Reference SDK (read-only): `~/.cursor/skills-cursor/canvas/sdk/index.d.ts`.

### Step 2: Generate static files

Create `{OUTPUT_DIR}/` per `references/output-contract.md`:

```text
{OUTPUT_DIR}/
  index.html
  styles.css
  app.js          # optional
  assets/         # optional
```

Order: `styles.css` via `scripts/canvas_export_lib.py` → `index.html` → charts as inline SVG → theme on CSS vars (do not bake hex into SVG).

Forbidden in output: absolute paths, `fetch()` / XHR, Cursor IDE action links, external CDNs.

### Step 3: Verify

```bash
bash "{SKILL_DIR}/scripts/verify_export.sh" "{OUTPUT_DIR}"
```

If HTML was assembled by a one-off script with hardcoded strings (not a live transpile), copy UI copy from the current canvas first, then:

```bash
python3 "{SKILL_DIR}/scripts/assert_export_matches_canvas.py" \
  "{CANVAS_PATH}" "{OUTPUT_DIR}"
```

Exit ≠ 0 → **STOP**. Then open preview in the system browser (do not ask):

```bash
open "{OUTPUT_DIR}/index.html"          # macOS
# xdg-open "{OUTPUT_DIR}/index.html"    # Linux
```

If sandbox blocks `open` – retry with full permissions. Skipping preview = fail DoD.

Forbidden: `python3 -m http.server` or any local static server.

### Step 4: Report

Path, file list, SDK coverage, how it was opened.

## Hard Stop Rules

- **Do not** modify the source `.canvas.tsx`.
- **Do not** use external CDNs for CSS/JS/charts.
- **Do not** use absolute asset paths.
- **Do not** continue on unsupported SDK without fallback / ack (except baked `computeDAGLayout` SVG).
- **Do not** overwrite a non-empty `{OUTPUT_DIR}` without ack.
- **Do not** start a local HTTP server for preview.

## Definition of Done

- `{OUTPUT_DIR}/index.html` exists and opens locally
- Asset refs relative
- Data inline; no network calls
- In-scope v1 components mapped (or STOP with gaps)
- Light theme via CSS vars (+ dark toggle)
- Preview opened via `open` / `xdg-open`

## Check commands

```bash
SKILL_DIR="<path-to-this-skill>"
test -f "$SKILL_DIR/references/sdk-mapping.md"
test -f "$SKILL_DIR/references/output-contract.md"
test -x "$SKILL_DIR/scripts/verify_export.sh"
```

## Example

**In:** `review.canvas.tsx` in `~/.cursor/projects/…/canvases/`  
**Out:** `.tmp/canvas-export/review/index.html` + `styles.css` + inline SVG charts
