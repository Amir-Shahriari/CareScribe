"""
HTML-string UI helpers for CareScribe. Every function returns a string to hand
to ``st.markdown(..., unsafe_allow_html=True)``. No Streamlit import, no state,
no side effects — presentation only.

Icons are drawn (1.5px stroke, 24x24, ``currentColor``), never emoji.
"""

from __future__ import annotations

import html as _html

# --------------------------------------------------------------------------
# Drawn icon set — one stroke weight, one grid.
# --------------------------------------------------------------------------

_SVG = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{}</svg>'
)

ICON = {
    "lock": _SVG.format(
        '<rect x="4.5" y="10.5" width="15" height="10" rx="2.2"/>'
        '<path d="M8 10.5V7a4 4 0 0 1 8 0v3.5"/><circle cx="12" cy="15.4" r="1.3"/>'
    ),
    "shield": _SVG.format(
        '<path d="M12 3.2 5 6v5.4c0 4.6 3 7.9 7 9.4 4-1.5 7-4.8 7-9.4V6z"/>'
        '<path d="m9 12 2 2 4-4.5"/>'
    ),
    "check": _SVG.format('<path d="m5 12.8 4.2 4L19 7.5"/>'),
    "upload": _SVG.format(
        '<path d="M12 15.5V4.5"/><path d="m7.5 9 4.5-4.5L16.5 9"/>'
        '<path d="M5 15.5v2.5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-2.5"/>'
    ),
    "scan": _SVG.format(
        '<path d="M4 8V6a2 2 0 0 1 2-2h2"/><path d="M20 8V6a2 2 0 0 0-2-2h-2"/>'
        '<path d="M4 16v2a2 2 0 0 0 2 2h2"/><path d="M20 16v2a2 2 0 0 1-2 2h-2"/>'
        '<path d="M4 12h16"/>'
    ),
    "eye": _SVG.format(
        '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12Z"/>'
        '<circle cx="12" cy="12" r="2.6"/>'
    ),
    "stamp": _SVG.format(
        '<path d="M12 3.5a3 3 0 0 0-3 3c0 1.7 1.2 2.5 1.2 4.2 0 1.3-1 1.8-2.4 1.8H8a2 2 0 0 0-2 2v.5h12V15a2 2 0 0 0-2-2h-.2c-1.4 0-2.4-.5-2.4-1.8 0-1.7 1.2-2.5 1.2-4.2a3 3 0 0 0-2.6-3Z"/>'
        '<rect x="4.5" y="18.5" width="15" height="2" rx="1"/>'
    ),
    "pen": _SVG.format(
        '<path d="M14.5 5.5 18.5 9.5 9 19H5v-4z"/><path d="M12.5 7.5 16.5 11.5"/>'
    ),
    "alert": _SVG.format(
        '<path d="M12 4.5 21 19.5H3z"/><path d="M12 10v4.2"/><circle cx="12" cy="17" r=".6" fill="currentColor"/>'
    ),
    "x": _SVG.format('<path d="M7 7 17 17"/><path d="M17 7 7 17"/>'),
    "minus": _SVG.format('<path d="M6 12h12"/>'),
    "clock": _SVG.format('<circle cx="12" cy="12" r="8"/><path d="M12 7.5V12l3 2"/>'),
    "dot": _SVG.format('<circle cx="12" cy="12" r="3.2" fill="currentColor" stroke="none"/>'),
    "cpu": _SVG.format(
        '<rect x="7" y="7" width="10" height="10" rx="2"/>'
        '<path d="M10 3.5V6M14 3.5V6M10 18v2.5M14 18v2.5M3.5 10H6M3.5 14H6M18 10h2.5M18 14h2.5"/>'
    ),
    "database": _SVG.format(
        '<ellipse cx="12" cy="6" rx="7" ry="3"/>'
        '<path d="M5 6v6c0 1.7 3.1 3 7 3s7-1.3 7-3V6"/>'
        '<path d="M5 12v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"/>'
    ),
}


def icon(name: str, cls: str = "") -> str:
    svg = ICON.get(name) or ICON["dot"]
    if cls:
        svg = svg.replace("<svg ", f'<svg class="{_html.escape(cls)}" ', 1)
    return svg


def _esc(text: object) -> str:
    return _html.escape(str(text))


# --------------------------------------------------------------------------
# Masthead
# --------------------------------------------------------------------------

_PRIVACY_PILL = {
    "offline": ("safe", "lock", "Offline — nothing leaves this computer"),
    "cloud": ("warn", "shield", "Cloud generation enabled — placeholders only"),
    "downloading": ("accent", "database", "Downloading the model — weights in, no data out"),
}


def hero(title: str, subtitle: str, privacy_state: str = "offline") -> str:
    tone, ic, text = _PRIVACY_PILL.get(privacy_state, _PRIVACY_PILL["offline"])
    return (
        '<div class="cs-hero"><div class="cs-hero__row">'
        f'<div><h1 class="cs-hero__title">{_esc(title)}</h1>'
        f'<p class="cs-hero__sub">{_esc(subtitle)}</p></div>'
        f'<span class="cs-lockpill" data-tone="{tone}">{ICON[ic]}{_esc(text)}</span>'
        '</div></div>'
    )


# --------------------------------------------------------------------------
# Step tracker
# --------------------------------------------------------------------------

STEPS = ("Load", "De-identify", "Review", "Approve", "Generate")


def step_tracker(active: int) -> str:
    """A 5-step progress tracker. ``active`` is a 0-based index; steps before it
    render done (a check), that one active, the rest upcoming — each showing its
    step number, because the sequence is the information."""
    cells = []
    for i, label in enumerate(STEPS):
        state = "done" if i < active else ("active" if i == active else "upcoming")
        mark = ICON["check"] if state == "done" else str(i + 1)
        cells.append(
            f'<div class="cs-step" data-state="{state}">'
            f'<span class="cs-step__dot">{mark}</span>'
            f'<span class="cs-step__label">{_esc(label)}</span></div>'
        )
    return f'<div class="cs-steps">{"".join(cells)}</div>'


# --------------------------------------------------------------------------
# Chips
# --------------------------------------------------------------------------

def chip(label: str, tone: str = "muted", icon_name: str | None = None) -> str:
    inner = icon(icon_name) if icon_name else '<span class="cs-chip__mark"></span>'
    return f'<span class="cs-chip" data-tone="{_esc(tone)}">{inner}{_esc(label)}</span>'


_DOC_STATUS = {
    "approved": ("Approved", "safe", "check"),
    "blocked": ("Blocked by safety sweep", "danger", "alert"),
    "review": ("Awaiting review", "accent", "eye"),
    "pending": ("Not yet processed", "muted", "clock"),
    "failed": ("Failed", "danger", "x"),
}


def status_chip(kind: str) -> str:
    label, tone, ic = _DOC_STATUS.get(kind, _DOC_STATUS["pending"])
    return chip(label, tone, ic)


# --------------------------------------------------------------------------
# Sidebar pieces
# --------------------------------------------------------------------------

def detection_layer(state: str, name: str, detail: str | None = None) -> str:
    """One row of the detection list. ``state`` in on/off/wait/warn.

    Name on the first line, the (optional) short detail quietly under it — the
    sidebar is narrow, so nothing shares a line that it cannot fit."""
    marks = {"on": "check", "warn": "alert"}
    ic = icon(marks.get(state, "minus"))
    tail = f'<small>{_esc(detail)}</small>' if detail else ""
    return (
        f'<div class="cs-layer" data-state="{_esc(state)}">{ic}'
        f'<span><b>{_esc(name)}</b>{tail}</span></div>'
    )


def model_label(stem: str) -> tuple[str, str]:
    """A readable (title, note) for a GGUF file stem, so the raw filename with
    its quantisation suffix never lands in the UI."""
    import re as _re

    s = _re.sub(
        r"[.\-_](gguf|q\d[_.]?k[_.]?[ms]|q\d_\d|f16|bf16|fp16)$",
        "",
        stem,
        flags=_re.IGNORECASE,
    )
    low = s.lower()
    if low.startswith("carescribe-clinical"):
        rest = s.split("carescribe-clinical", 1)[1].strip("-_ .")
        ver = ""
        for part in rest.replace("_", "-").split("-"):
            if part and (part[0] in "vV" and part[1:].isdigit()):
                ver = part.lower()
        return "CareScribe Clinical", f"fine-tuned{(' · ' + ver) if ver else ''}"
    # a stock base model — tidy the name, mark it built-in
    pretty = (
        s.replace("-Instruct", "")
        .replace("-instruct", "")
        .replace("_K_M", "")
        .replace("-", " ")
        .strip()
    )
    return pretty or stem, "built-in"


def stat_strip(items: list[tuple[str, object]]) -> str:
    rows = "".join(
        f'<div class="cs-stat"><span>{_esc(k)}</span><b>{_esc(v)}</b></div>'
        for k, v in items
    )
    return f'<div class="cs-stats">{rows}</div>'


def privacy_line() -> str:
    """The compact 'all clear' offline statement for the sidebar. The loud
    states (cloud enabled, model downloading) stay as full Streamlit alerts —
    only the reassuring default is quiet."""
    return (
        f'<div class="cs-privacy">{ICON["lock"]}'
        "<span><b>Fully offline.</b> Documents are read into memory, "
        "de-identified and drafted here — nothing is uploaded.</span></div>"
    )


# --------------------------------------------------------------------------
# Empty state
# --------------------------------------------------------------------------

def empty_state(icon_name: str, title: str, body: str) -> str:
    return (
        f'<div class="cs-empty">{icon(icon_name)}'
        f'<b>{_esc(title)}</b><span>{_esc(body)}</span></div>'
    )


__all__ = [
    "ICON",
    "STEPS",
    "chip",
    "detection_layer",
    "empty_state",
    "hero",
    "icon",
    "model_label",
    "privacy_line",
    "stat_strip",
    "status_chip",
    "step_tracker",
]
