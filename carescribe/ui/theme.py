"""
CareScribe visual identity — one stylesheet, injected once per rerun.

DIRECTION (refinement of the incumbent calm-clinical world, identity kept)
THESIS: a clinical instrument that always shows the reviewer where they stand
in an irreversible pipeline; the calm is the trust signal, not decoration.
OWN-WORLD: near-white ground under a barely-there indigo/teal wash; ink
#101828 and slate #667085 text; a single indigo accent (#4f46e5); 16px card
radius; IBM Plex Sans for the interface, IBM Plex Mono for identifiers, paths
and model names (one superfamily); drawn 1.5px-stroke icons, never emoji.
FIRST VIEWPORT: a quiet masthead (name, one-line purpose, an "offline —
nothing leaves this computer" lock pill), then a horizontal step tracker
(Load / De-identify / Review / Approve / Generate) with done, active and
upcoming states, then the first step card.
SIGNATURE: the tracker fills as the reviewer advances; the connector to the
active step is the one drawn line on the page.
FINISH: unreviewed and undocumented is unfinished; this build ends with the
finish review, the verdict, DESIGN.md, and every shipping raster carrying its
provenance.

Streamlit theming only reaches five colour tokens and a font family
(``.streamlit/config.toml``); everything below — the type scale, the component
state vocabulary, the step tracker, chips, the destructive-button treatment,
the browser surfaces — is this file.
"""

from __future__ import annotations

# One superfamily, purpose-built for technical / enterprise products: IBM Plex
# Sans for the interface, IBM Plex Mono for identifiers, paths and model names.
# Not Inter — the surface is an instrument, and the type system should read as
# one designed object rather than the AI-interface default.
FONT_IMPORT = (
    "@import url('https://fonts.googleapis.com/css2?"
    "family=IBM+Plex+Mono:wght@400;500&"
    "family=IBM+Plex+Sans:wght@400;450;500;600;700&display=swap');"
)

CSS = f"""
<style>
{FONT_IMPORT}

:root {{
  --cs-bg:#ffffff; --cs-surface:#ffffff; --cs-panel:#f7f8fa;
  --cs-border:#e7e9ee; --cs-line:#eef0f4;
  --cs-ink:#101828; --cs-ink-soft:#344054; --cs-muted:#667085; --cs-faint:#98a2b3;
  --cs-accent:#4f46e5; --cs-accent-hover:#4338ca; --cs-accent-soft:#eef2ff; --cs-accent-line:#c7d2fe;
  --cs-safe:#047857; --cs-safe-soft:#ecfdf5; --cs-safe-line:#a7f3d0;
  --cs-warn:#b45309; --cs-warn-soft:#fff7ed; --cs-warn-line:#fed7aa;
  --cs-danger:#b91c1c; --cs-danger-soft:#fef2f2; --cs-danger-line:#fecaca;
  --cs-radius:16px; --cs-radius-sm:11px; --cs-radius-xs:8px;
  --cs-shadow:0 1px 2px rgba(16,24,40,.04), 0 10px 28px rgba(16,24,40,.06);
  --cs-shadow-sm:0 1px 2px rgba(16,24,40,.05), 0 4px 12px rgba(16,24,40,.05);
  --cs-ease:cubic-bezier(.22,1,.36,1);
}}

/* ---------- typography ---------- */
html, body, [data-testid="stAppViewContainer"], .stApp,
button, input, textarea, select, [data-testid="stMarkdownContainer"],
h1, h2, h3, h4, h5, h6, [data-testid="stHeadingContainer"] {{
  font-family: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif !important;
  -webkit-font-smoothing: antialiased;
}}
code, kbd, pre, [data-testid="stCode"] *, .stCode *,
[data-testid="stCodeBlock"] *, .cs-mono {{
  font-family: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace !important;
  font-feature-settings: "ss01";
}}
/* aligned digits everywhere a number is read in a column */
[data-testid="stDataFrame"], [data-testid="stTable"], .cs-steps, .cs-stat b {{
  font-variant-numeric: tabular-nums;
}}

/* ---------- page canvas: calm, centred, a soft wash ---------- */
[data-testid="stAppViewContainer"], .stApp {{
  background:
    radial-gradient(1100px 460px at 84% -14%, rgba(79,70,229,.055), transparent 62%),
    radial-gradient(820px 380px at -12% 6%, rgba(4,120,87,.04), transparent 58%),
    var(--cs-bg);
}}
[data-testid="stMain"] {{ background: transparent; }}
[data-testid="stAppViewContainer"], [data-testid="stMain"], .stApp {{ overflow-x: clip; }}
[data-testid="stMainBlockContainer"], .stMainBlockContainer, section.main .block-container {{
  max-width: 1000px !important;
  padding-top: 2.4rem !important;
  padding-bottom: 5rem !important;
  padding-inline: clamp(1rem, 4vw, 2rem) !important;
}}
/* nothing but a self-contained scroller may push the page wider than the viewport */
.cs-hero, .cs-hero__row, .cs-steps, .cs-stats {{ max-width: 100%; }}
.cs-hero__title {{ overflow-wrap: anywhere; }}

/* strip Streamlit's dev chrome — this ships as a local clinical tool */
[data-testid="stDecoration"], [data-testid="stToolbar"], [data-testid="stStatusWidget"] {{ display: none; }}
[data-testid="stHeader"] {{ background: transparent; border-bottom: 0; height: 0; }}

/* the built-in st.title is replaced by components.hero(); keep it tidy if used */
[data-testid="stAppViewContainer"] h1 {{
  font-size: 1.5rem; font-weight: 700; letter-spacing: -0.022em; padding: 0; margin: 0 0 0.15rem;
}}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * {{ color: var(--cs-muted); }}

/* ---------- masthead ---------- */
.cs-hero {{ margin: 0.2rem 0 0.2rem; }}
.cs-hero__row {{ display:flex; align-items:flex-start; justify-content:space-between; gap:1.25rem 2rem; flex-wrap:wrap; }}
.cs-hero__row > div {{ flex: 1 1 24rem; min-width: 0; }}
.cs-hero__row > .cs-lockpill {{ flex: 0 0 auto; margin-top: 0.35rem; }}
.cs-hero__title {{
  font-size: clamp(1.6rem, 3.2vw, 2.05rem); font-weight: 700; letter-spacing: -0.03em;
  color: var(--cs-ink); line-height: 1.14; margin: 0;
}}
.cs-hero__sub {{ color: var(--cs-muted); font-size: 0.95rem; margin: 0.45rem 0 0; max-width: 58ch; line-height: 1.5; }}
.cs-lockpill {{
  display:inline-flex; align-items:center; gap:0.5rem; white-space:nowrap;
  background: var(--cs-safe-soft); color: var(--cs-safe);
  border: 1px solid var(--cs-safe-line); border-radius: 999px;
  padding: 0.42rem 0.85rem; font-size: 0.8rem; font-weight: 600;
}}
.cs-lockpill svg {{ width: 14px; height: 14px; }}
.cs-lockpill[data-tone="warn"]   {{ background: var(--cs-warn-soft); color: var(--cs-warn); border-color: var(--cs-warn-line); }}
.cs-lockpill[data-tone="accent"] {{ background: var(--cs-accent-soft); color: var(--cs-accent); border-color: var(--cs-accent-line); }}

/* ---------- step tracker: the one drawn line on the page ---------- */
.cs-steps {{
  display: grid; grid-auto-flow: column; grid-auto-columns: 1fr;
  margin: 0.9rem 0 0.1rem; gap: 0;
  padding: 0.95rem 0.5rem 0.85rem;
  border: 1px solid var(--cs-line); border-radius: var(--cs-radius);
  background: var(--cs-surface);
  box-shadow: var(--cs-shadow-sm);
}}
.cs-step {{ position: relative; display:flex; flex-direction:column; align-items:center; gap:0.5rem; text-align:center; padding: 0 0.4rem; }}
.cs-step__dot {{
  width: 34px; height: 34px; border-radius: 999px; display:grid; place-items:center;
  border: 1.5px solid var(--cs-border); background: var(--cs-surface);
  color: var(--cs-faint); flex: none;
  font-size: 0.85rem; font-weight: 650; font-variant-numeric: tabular-nums;
  transition: border-color .35s var(--cs-ease), background .35s var(--cs-ease), color .35s var(--cs-ease), box-shadow .35s var(--cs-ease);
}}
.cs-step__dot svg {{ width: 15px; height: 15px; }}
.cs-step__label {{ font-size: 0.8rem; font-weight: 550; color: var(--cs-faint); letter-spacing: -0.006em; transition: color .35s var(--cs-ease); }}
/* connector: drawn from the previous dot to this one */
.cs-step::before {{
  content: ""; position: absolute; top: 17px; right: 50%; left: -50%; height: 2px;
  background: var(--cs-border); z-index: 0; border-radius: 999px;
  transform: scaleX(1); transform-origin: right center;
}}
.cs-step:first-child::before {{ display: none; }}
.cs-step__dot, .cs-step__label {{ position: relative; z-index: 1; }}
.cs-step[data-state="done"] .cs-step__dot {{ border-color: var(--cs-accent); background: var(--cs-accent); color: #fff; }}
.cs-step[data-state="done"] .cs-step__label {{ color: var(--cs-ink-soft); }}
.cs-step[data-state="done"]::before {{ background: var(--cs-accent); }}
.cs-step[data-state="active"] .cs-step__dot {{
  border-color: var(--cs-accent); color: var(--cs-accent); background: var(--cs-accent-soft);
  box-shadow: 0 0 0 5px rgba(79,70,229,.12);
}}
.cs-step[data-state="active"] .cs-step__label {{ color: var(--cs-ink); font-weight: 650; }}
.cs-step[data-state="active"]::before {{ background: linear-gradient(90deg, var(--cs-accent), var(--cs-accent-line)); animation: cs-draw .55s var(--cs-ease); }}
@keyframes cs-draw {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
@media (max-width: 640px) {{
  .cs-step__label {{ display: none; }}
  .cs-steps {{ margin-top: 0.8rem; padding: 0.85rem 0.25rem; }}
  .cs-step__dot {{ width: 30px; height: 30px; font-size: 0.8rem; }}
  .cs-step::before {{ top: 15px; }}
  .cs-hero__row {{ gap: 0.9rem; }}
  .cs-hero__row > .cs-lockpill {{ margin-top: 0; }}
  [data-testid="stMainBlockContainer"] {{ padding-top: 1.6rem !important; }}
}}
@media (prefers-reduced-motion: reduce) {{ .cs-step[data-state="active"]::before {{ animation: none !important; }} }}

/* ---------- cards: one per numbered step ----------
   Only the step containers opened in main() carry a `.cs-card` marker as their
   first child; scoping to that keeps the treatment off Streamlit's own border
   wrappers (the sidebar shell, the file-uploader, the main block wrapper). */
.cs-card {{ display: none; }}
[data-testid="stElementContainer"]:has(> div > [data-testid="stMarkdownContainer"] > .cs-card) {{
  display: none;
}}
[data-testid="stVerticalBlockBorderWrapper"]:has(
  > div > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:first-child .cs-card
) {{
  background: var(--cs-surface);
  border: 1px solid var(--cs-border) !important;
  border-radius: var(--cs-radius) !important;
  box-shadow: var(--cs-shadow);
  padding: clamp(1.3rem, 2.4vw, 2.1rem) !important;
  margin-top: 1.4rem;
}}

/* step heading = card title */
[data-testid="stAppViewContainer"] h3 {{
  font-size: 1.16rem; font-weight: 650; letter-spacing: -0.014em;
  margin: 0 0 0.3rem; padding: 0; border: 0;
}}
[data-testid="stAppViewContainer"] h2 {{
  font-size: 1rem; font-weight: 600; margin: 1.5rem 0 0.45rem; padding: 0; border: 0;
}}
[data-testid="stAppViewContainer"] h4, [data-testid="stAppViewContainer"] h5 {{
  font-size: 0.82rem; font-weight: 650; color: var(--cs-muted);
  letter-spacing: 0.02em; text-transform: uppercase;
  margin: 1.5rem 0 0.5rem;
}}
[data-testid="stAppViewContainer"] hr {{ margin: 1.5rem 0; border-color: var(--cs-line); }}

[data-testid="stText"], .stText {{ color: var(--cs-ink); }}
[data-testid="stCode"], pre, [data-testid="stCodeBlock"] {{
  border: 1px solid var(--cs-border) !important;
  border-radius: var(--cs-radius-sm) !important;
  background: #fafbfd !important;
}}

/* ---------- chips (status pills) ---------- */
.cs-chip {{
  display:inline-flex; align-items:center; gap:0.4rem; white-space:nowrap;
  border-radius: 999px; padding: 0.2rem 0.6rem 0.2rem 0.5rem;
  font-size: 0.78rem; font-weight: 600; line-height: 1.3;
  border: 1px solid var(--cs-border); background: var(--cs-panel); color: var(--cs-ink-soft);
}}
.cs-chip svg {{ width: 12px; height: 12px; flex: none; }}
.cs-chip__mark {{ width: 6px; height: 6px; border-radius: 999px; background: currentColor; flex: none; }}
.cs-chip[data-tone="accent"] {{ background: var(--cs-accent-soft); border-color: var(--cs-accent-line); color: var(--cs-accent); }}
.cs-chip[data-tone="safe"]   {{ background: var(--cs-safe-soft);  border-color: var(--cs-safe-line);  color: var(--cs-safe); }}
.cs-chip[data-tone="warn"]   {{ background: var(--cs-warn-soft);  border-color: var(--cs-warn-line);  color: var(--cs-warn); }}
.cs-chip[data-tone="danger"] {{ background: var(--cs-danger-soft);border-color: var(--cs-danger-line);color: var(--cs-danger); }}
.cs-chip[data-tone="muted"]  {{ background: var(--cs-panel); border-color: var(--cs-border); color: var(--cs-muted); }}

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] {{ background: var(--cs-panel); border-right: 1px solid var(--cs-border); }}
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
[data-testid="stSidebar"] > div:first-child > div:first-child {{ min-width: 15.5rem; }}
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{ padding-top: 1.4rem; }}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {{
  font-size: 0.72rem; font-weight: 650; letter-spacing: .08em; text-transform: uppercase;
  color: var(--cs-faint); border: 0; margin: 1.5rem 0 0.45rem;
}}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{ font-size: 0.78rem; line-height: 1.45; }}
[data-testid="stSidebar"] hr {{ display: none; }}

.cs-brand {{
  display:flex; align-items:center; gap:0.5rem;
  font-size: 1.02rem; font-weight: 700; letter-spacing: -0.01em; color: var(--cs-ink);
  margin: 0 0 0.2rem;
}}
.cs-brand span {{ color: var(--cs-accent); display:inline-flex; }}
.cs-brand svg {{ width: 18px; height: 18px; }}

.cs-stat {{
  display:flex; align-items:baseline; justify-content:space-between; gap:0.75rem;
  padding: 0.38rem 0; border-bottom: 1px solid var(--cs-line); font-size: 0.8rem;
}}
.cs-stat:last-child {{ border-bottom: 0; }}
.cs-stat span {{ color: var(--cs-muted); }}
.cs-stat b {{ color: var(--cs-ink); font-weight: 650; font-size: 0.88rem; }}

/* detection rows: name on top, short detail quietly beneath — never on one
   line the narrow sidebar cannot hold */
.cs-layer {{ display:flex; align-items:flex-start; gap:0.5rem; padding: 0.3rem 0; }}
.cs-layer svg {{ width: 15px; height: 15px; flex: none; margin-top: 1px; }}
.cs-layer > span {{ min-width: 0; display:flex; flex-direction:column; line-height: 1.35; }}
.cs-layer b {{ font-size: 0.82rem; font-weight: 600; color: var(--cs-ink); overflow-wrap: anywhere; }}
.cs-layer small {{ font-size: 0.72rem; color: var(--cs-muted); overflow-wrap: anywhere; }}
.cs-layer[data-state="on"]  svg {{ color: var(--cs-safe); }}
.cs-layer[data-state="off"] svg, .cs-layer[data-state="wait"] svg {{ color: var(--cs-faint); }}
.cs-layer[data-state="warn"] svg {{ color: var(--cs-warn); }}

.cs-setup-label {{
  font-size: 0.72rem; font-weight: 600; color: var(--cs-muted);
  letter-spacing: 0.02em; margin: 0.2rem 0 0.15rem;
}}

/* generation model — a readable label, never the raw quantised filename */
.cs-model {{ display:flex; align-items:flex-start; gap:0.5rem; margin: 0.9rem 0 0.5rem; }}
.cs-model svg {{ width: 15px; height: 15px; flex: none; margin-top: 2px; color: var(--cs-accent); }}
.cs-model > span {{ display:flex; flex-direction:column; line-height: 1.3; min-width: 0; }}
.cs-model b {{ font-size: 0.85rem; font-weight: 600; color: var(--cs-ink); }}
.cs-model small {{ font-size: 0.72rem; color: var(--cs-muted); }}

/* compact 'all clear' privacy statement (loud states stay as st.warning/info) */
.cs-privacy {{
  display:flex; align-items:flex-start; gap:0.55rem;
  background: var(--cs-safe-soft); border: 1px solid var(--cs-safe-line);
  border-radius: 12px; padding: 0.7rem 0.8rem;
}}
.cs-privacy svg {{ width: 15px; height: 15px; flex: none; margin-top: 2px; color: var(--cs-safe); }}
.cs-privacy span {{ font-size: 0.78rem; line-height: 1.45; color: var(--cs-safe); }}
.cs-privacy b {{ color: var(--cs-safe); font-weight: 650; }}

[data-testid="stSidebar"] .stButton > button {{ font-size: 0.82rem; padding: 0.5rem 1rem; }}
.st-key-open_model_card [data-testid="stBaseButton-secondary"] {{ font-weight: 550; color: var(--cs-muted); }}

/* ---------- empty state ---------- */
.cs-empty {{ text-align:center; padding: 1.6rem 1rem; color: var(--cs-muted); }}
.cs-empty svg {{ width: 30px; height: 30px; color: var(--cs-faint); margin-bottom: 0.6rem; }}
.cs-empty b {{ display:block; color: var(--cs-ink); font-weight: 600; font-size: 0.95rem; margin-bottom: 0.2rem; }}
.cs-empty span {{ font-size: 0.86rem; }}

/* ---------- buttons: one shape, full state vocabulary ---------- */
.stButton > button, [data-testid="stBaseButton-secondary"],
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-secondaryFormSubmit"] {{
  border-radius: var(--cs-radius-sm);
  font-weight: 600; font-size: 0.9rem;
  padding: 0.6rem 1.25rem;
  border: 1px solid var(--cs-border);
  transition: background .16s var(--cs-ease), border-color .16s var(--cs-ease), color .16s var(--cs-ease), box-shadow .16s var(--cs-ease), transform .12s var(--cs-ease);
}}
[data-testid="stBaseButton-secondary"] {{ background: var(--cs-surface); color: var(--cs-ink); }}
[data-testid="stBaseButton-secondary"]:hover:not(:disabled) {{
  border-color: var(--cs-accent); color: var(--cs-accent); background: var(--cs-accent-soft);
}}
[data-testid="stBaseButton-primary"] {{
  background: var(--cs-accent); border-color: var(--cs-accent); color: #fff;
  box-shadow: 0 4px 14px rgba(79,70,229,.26);
}}
[data-testid="stBaseButton-primary"]:hover:not(:disabled) {{
  background: var(--cs-accent-hover); border-color: var(--cs-accent-hover); transform: translateY(-1px);
}}
.stButton > button:active:not(:disabled) {{ transform: translateY(0); }}
.stButton > button:disabled, [data-testid^="stBaseButton"]:disabled {{ opacity: 0.5; box-shadow: none; }}
.stButton > button:focus-visible, [data-testid^="stBaseButton"]:focus-visible {{
  outline: 2px solid var(--cs-accent); outline-offset: 2px;
}}

.st-key-wipe_phi_btn [data-testid="stBaseButton-primary"] {{
  background: var(--cs-danger-soft); border-color: var(--cs-danger-line); color: var(--cs-danger); box-shadow: none;
}}
.st-key-wipe_phi_btn [data-testid="stBaseButton-primary"]:hover:not(:disabled) {{
  background: var(--cs-danger); border-color: var(--cs-danger); color: #fff; transform: none;
}}

/* ---------- inputs ---------- */
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input, [data-baseweb="select"] > div {{
  border-radius: var(--cs-radius-sm) !important;
  border-color: var(--cs-border) !important;
  background: var(--cs-surface) !important;
  transition: border-color .16s var(--cs-ease), box-shadow .16s var(--cs-ease);
}}
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {{
  border-color: var(--cs-accent) !important;
  box-shadow: 0 0 0 3px rgba(79,70,229,.12) !important;
}}

/* ---------- tabs: a segmented pill ---------- */
[data-baseweb="tab-list"] {{
  background: #f3f4f6; border-radius: 10px; padding: 4px; gap: 4px;
  border-bottom: 0; display: inline-flex;
}}
[data-baseweb="tab"] {{
  border-radius: 8px; padding: 0.4rem 1rem;
  font-size: 0.88rem; font-weight: 550; color: var(--cs-muted);
  transition: background .15s var(--cs-ease), color .15s var(--cs-ease), box-shadow .15s var(--cs-ease);
}}
[data-baseweb="tab"][aria-selected="true"] {{
  background: #fff; color: var(--cs-ink); box-shadow: 0 1px 3px rgba(0,0,0,.09);
}}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {{ display: none; }}

/* ---------- expanders, alerts, dataframe, dropzone ---------- */
[data-testid="stExpander"] details {{
  border: 1px solid var(--cs-border); border-radius: 12px; background: var(--cs-surface);
}}
[data-testid="stExpander"] summary:hover {{ color: var(--cs-accent); }}

[data-testid="stAlert"] {{ border-radius: 12px; border: 1px solid var(--cs-border); }}
[data-testid="stAlertContentInfo"] {{ background: var(--cs-accent-soft); border-color: var(--cs-accent-line); }}
[data-testid="stAlertContentSuccess"] {{ background: var(--cs-safe-soft); border-color: var(--cs-safe-line); }}
[data-testid="stAlertContentWarning"] {{ background: var(--cs-warn-soft); border-color: var(--cs-warn-line); }}
[data-testid="stAlertContentError"] {{ background: var(--cs-danger-soft); border-color: var(--cs-danger-line); }}

[data-testid="stDataFrame"], [data-testid="stTable"] {{
  border: 1px solid var(--cs-border); border-radius: 12px; overflow: hidden;
}}

/* hand-rolled batch-status table (section_batch_status) */
.cs-table-wrap {{ overflow-x: auto; margin-top: 0.6rem; }}
.cs-table {{ width: 100%; min-width: 34rem; border-collapse: collapse; }}
.cs-table th {{
  text-align: left; font-size: 0.72rem; font-weight: 650;
  letter-spacing: 0.04em; text-transform: uppercase; color: var(--cs-faint);
  padding: 0 0.7rem 0.5rem; border-bottom: 1px solid var(--cs-border);
}}
.cs-table td {{
  font-size: 0.86rem; color: var(--cs-ink-soft);
  padding: 0.6rem 0.7rem; border-bottom: 1px solid var(--cs-line);
  vertical-align: middle;
}}
.cs-table tr:last-child td {{ border-bottom: 0; }}
.cs-table th:first-child, .cs-table td:first-child {{ padding-left: 0; width: 2.2rem; color: var(--cs-faint); }}
.cs-table th:last-child, .cs-table td:last-child {{ padding-right: 0; }}
.cs-table td:nth-child(4) {{ text-align: right; font-variant-numeric: tabular-nums; }}
.cs-table th:nth-child(4) {{ text-align: right; }}
.cs-table .cs-mono {{ font-size: 0.8rem; color: var(--cs-ink-soft); overflow-wrap: anywhere; }}

[data-testid="stFileUploaderDropzone"] {{
  border: 1.5px dashed #cdd2dc; border-radius: 14px; background: #fafbfd;
  transition: border-color .16s var(--cs-ease), background .16s var(--cs-ease), color .16s var(--cs-ease);
}}
[data-testid="stFileUploaderDropzone"]:hover {{
  border-color: var(--cs-accent); background: var(--cs-accent-soft); color: var(--cs-accent);
}}

[data-testid="stProgress"] > div > div > div {{ background: var(--cs-accent); }}
[data-testid="stRadio"] label, [data-testid="stCheckbox"] label {{ transition: color .16s var(--cs-ease); }}

/* ---------- browser surfaces ---------- */
::selection {{ background: rgba(79,70,229,.18); }}
* {{ scrollbar-width: thin; scrollbar-color: #cbd0da transparent; }}
::-webkit-scrollbar {{ width: 11px; height: 11px; }}
::-webkit-scrollbar-thumb {{ background: #cbd0da; border-radius: 999px; border: 3px solid transparent; background-clip: content-box; }}
::-webkit-scrollbar-thumb:hover {{ background: #aab1bf; background-clip: content-box; }}
a {{ color: var(--cs-accent); text-underline-offset: 2px; }}
</style>
"""


def inject() -> None:
    """Apply the stylesheet. Import Streamlit lazily so the module stays cheap."""
    import streamlit as st

    st.markdown(CSS, unsafe_allow_html=True)


__all__ = ["CSS", "FONT_IMPORT", "inject"]
