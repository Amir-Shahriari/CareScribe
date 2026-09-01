# CareScribe — design system

The visual language of the CareScribe desktop app, as built. It is a
**refinement** of a calm-clinical world already in the codebase, not a new
identity. Implementation: `carescribe/ui/theme.py` (the one stylesheet) and
`carescribe/ui/components.py` (HTML-string helpers + a drawn icon set), injected
over Streamlit by `carescribe/app.py`.

## Direction

**Thesis.** A clinical instrument that always shows the reviewer where they
stand in an irreversible pipeline (load → de-identify → review → approve →
generate). The calm *is* the trust signal — a de-identification tool that looks
experimental reads as unserious with patient data.

**Mode.** Operate. The reviewer completes a task; scanability, consistency and
familiar affordances outrank expression. Brand lives in precise details.

**Signature.** The step tracker fills as the reviewer advances; the connector
into the active step is the one drawn line on the page.

## Palette

Restrained: near-white ground under a barely-there indigo/teal radial wash, one
indigo accent, ink and slate text. Colour never owns a region — it marks state.

| Token | Value | Role |
|---|---|---|
| `--cs-bg` / `--cs-surface` | `#ffffff` | page and card ground |
| `--cs-panel` | `#f7f8fa` | sidebar, insets |
| `--cs-border` / `--cs-line` | `#e7e9ee` / `#eef0f4` | 1px separators; hairlines |
| `--cs-ink` / `--cs-ink-soft` / `--cs-muted` / `--cs-faint` | `#101828` / `#344054` / `#667085` / `#98a2b3` | text, four steps |
| `--cs-accent` (+ `-hover`, `-soft`, `-line`) | `#4f46e5` | the single accent: active step, primary button, focus ring, links, "review" chip |
| `--cs-safe` / `--cs-warn` / `--cs-danger` (+ `-soft`, `-line`) | `#047857` / `#b45309` / `#b91c1c` | status only — approved / caution / blocked & the wipe action |

Light, not by category but by scene: a clinician at a desk, indoors, daylight.

## Type

One superfamily, purpose-built for technical/enterprise products — **not Inter**.

- **IBM Plex Sans** — the interface. 400–700.
- **IBM Plex Mono** (`ss01`) — identifiers, file paths, model names, code, and
  anything read as a value in a column (`font-variant-numeric: tabular-nums`).

Scale (rem): hero title `clamp(1.6, 3.2vw, 2.05)` / -0.03em · card title (`h3`)
1.16 / 650 · section label (`h4`) 0.82 uppercase 0.02em muted · body 0.9–0.95 ·
caption 0.78 · sidebar section label 0.72 uppercase 0.08em faint.

## Space & shape

- Card radius `--cs-radius` 16px; controls `--cs-radius-sm` 11px; chips 999px.
- Depth: `--cs-shadow` `0 1px 2px / 0 10px 28px` at 4–6% — offset **and** blur,
  never a zero-offset halo.
- One rhythm: more space above a heading than below it. Main column
  `max-width: 1000px`. Sidebar `min-width: 15.5rem`.
- Ease: `cubic-bezier(.22,1,.36,1)`, ~.16s controls / ~.35s the tracker.
  `prefers-reduced-motion` drops the connector animation.

## Components (`carescribe/ui/components.py`)

| Helper | What it is |
|---|---|
| `hero(title, subtitle, privacy_state)` | masthead; a lock/shield/database pill that changes with `offline` / `cloud` / `downloading` |
| `step_tracker(active)` | the 5-step tracker in a card; done = check, active = number in an accent ring, upcoming = number; labels hide < 640px |
| `chip` / `status_chip(kind)` | status pill, tone `accent/safe/warn/danger/muted`, drawn icon or a 6px mark |
| `detection_layer(state, name, detail)` | sidebar row: name on line 1, short detail quietly beneath — nothing shares a line the panel can't hold |
| `model_label(stem)` | `carescribe-clinical-phi35-v1.Q4_K_M` → `("CareScribe Clinical", "fine-tuned · v1")`; the raw quantised filename never reaches the UI |
| `privacy_line()` | the compact "all clear" offline box for the sidebar; the loud states stay as `st.warning` / `st.info` |
| `stat_strip` / `empty_state` | the session summary; the drawn-icon "nothing here yet, do X first" block |

**Icons** are drawn SVG (`ICON`), 1.6px stroke, 24-grid, `currentColor` — no
emoji. `:material/` icons are used where a Streamlit alert takes an `icon=`.

## Browser surfaces

Themed from the palette, not left to the browser: text selection, caret, custom
scrollbars (`#cbd0da` thumb), focus rings (2px accent, 2px offset), link
underline-offset, and tabular numerals in every column of figures.

## Sidebar order

By usefulness: **Session** (stats + the destructive wipe) → **Privacy** (compact
when clear, loud when not) → **Setup** (detection layers + the generation model,
reference material, so last and quiet). The model card opens in an `st.dialog`,
never an inline expander in the narrow panel.

## What this system is not

No gradient text, no glass-as-decoration, no coloured `border-left` above 1px,
no zero-blur block shadow, no numbered `01 / 02` eyebrows (the tracker carries
the sequence), no unicode glyph standing in for an icon.
