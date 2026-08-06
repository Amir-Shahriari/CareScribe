"""
CareScribe — local, privacy-preserving de-identification and review.

Run with:  streamlit run carescribe/app.py

Privacy model
-------------
* CPU-only and fully offline. This stage makes no network calls of any kind:
  no LLM, no provider, no telemetry. The server binds to 127.0.0.1 (see
  ``.streamlit/config.toml``).
* Raw document text, the detected identifiers, and the identity mapping
  (real value -> placeholder) live ONLY in ``st.session_state`` — server-side
  RAM. None of it is written to disk, ever.
* The single write path is approval, and it writes de-identified text only, to
  ``carescribe/output/deidentified/``.

Generation is deliberately not wired up. See :mod:`carescribe.core.carenotes`.
"""

from __future__ import annotations

import html
import io
import sys
import time
from pathlib import Path

import pandas as pd
import streamlit as st

# Allow `streamlit run carescribe/app.py` to resolve the `carescribe` package
# by putting its parent directory on sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from carescribe.core import (  # noqa: E402
    batch, carenotes, deidentify, ingest, mapping, ollama_client,
    review_checklist, review_flags,
)

st.set_page_config(page_title="CareScribe", page_icon="🩺", layout="wide")

TABLE_COLUMNS = ["value", "type", "placeholder", "action"]


# --------------------------------------------------------------------------
# Session state
#
# Every key here can hold PHI or PHI-derived data. "Wipe PHI" clears exactly
# this list, so a new PHI-bearing key means a new entry here too.
# --------------------------------------------------------------------------

PHI_KEYS: dict = {
    "docs": {},        # filename -> batch.Document (raw text, entities, map)
    "order": [],       # filenames, in batch order
    "selected": "",    # filename currently under review
    "load_errors": [],
    # Reviewer decisions, keyed by filename. A dismissal key carries the text of
    # the span that was dismissed — which is precisely a string someone decided
    # was not an identifier, and could be wrong. It belongs on this list.
    "checklist": {},        # filename -> set of ticked checklist keys
    "flag_dismissed": {},   # filename -> list of dismissed flag keys
    "flag_redacted": {},    # filename -> count redacted from highlights
    # Generated drafts. The de-identified draft is safe; the re-identified one
    # holds real identifiers, so it lives here and is wiped with everything else.
    "drafts": {},
}

DEFAULTS = {**PHI_KEYS, "uploader_nonce": 0, "folder_path": ""}


def init_state() -> None:
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value.copy() if isinstance(value, (dict, list)) else value


def wipe_phi() -> None:
    """Drop every document, identifier table, and identity map from memory."""
    for key, value in PHI_KEYS.items():
        st.session_state[key] = value.copy() if isinstance(value, (dict, list)) else value
    # Force the uploader to forget its files by rotating its widget key.
    st.session_state.uploader_nonce = st.session_state.get("uploader_nonce", 0) + 1


init_state()


def documents() -> dict[str, batch.Document]:
    return st.session_state.docs


def current() -> batch.Document | None:
    return documents().get(st.session_state.selected)


def refresh(document: batch.Document, entities: list[dict]) -> None:
    """Re-derive the preview and map from an edited entity list."""
    result = deidentify.rebuild(document.raw_text, entities)
    document.entities = result.entities
    document.redacted_text = result.redacted_text
    document.phi_map = result.phi_map
    document.known_as = result.known_as
    # Any edit invalidates a previous approval decision.
    document.approved = False
    document.residual = []


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------

def render_sidebar() -> None:
    st.sidebar.title("🩺 CareScribe")
    st.sidebar.caption("Local, CPU-only. No network calls in this stage.")

    st.sidebar.subheader("Detection layers")
    status = deidentify.engine_status()

    st.sidebar.markdown("✅ **1. Structured regex** — always on")

    if status["ner"]:
        st.sidebar.markdown(f"✅ **2. Presidio + spaCy** — `{status['ner_model']}`")
    elif status["ner_error"]:
        st.sidebar.markdown("⚠️ **2. Presidio + spaCy** — unavailable")
        st.sidebar.caption(status["ner_error"])
    else:
        st.sidebar.markdown("⏳ **2. Presidio + spaCy** — loads on first document")

    if status["gliner"]:
        st.sidebar.markdown("✅ **3. GLiNER** — loaded")
    else:
        st.sidebar.markdown("➖ **3. GLiNER** — not installed (optional)")

    st.sidebar.caption(
        "In-prose dates: "
        + ("redacted" if status["inprose_dates"] else "kept unless identity-anchored")
    )

    st.sidebar.divider()

    st.sidebar.subheader("Session")
    docs = documents()
    approved = sum(1 for doc in docs.values() if doc.approved)
    identifiers = sum(len(doc.entities) for doc in docs.values())
    st.sidebar.caption(
        f"In memory: {len(docs)} documents, {identifiers} identifiers, "
        f"{approved} approved."
    )

    if st.sidebar.button("🧹 Clear session / wipe PHI", type="primary", use_container_width=True):
        wipe_phi()
        st.rerun()

    st.sidebar.caption(
        "Wipe drops every document, identifier table, and identity map from "
        "memory. None of it was ever written to disk. Approved de-identified "
        "files already on disk are left alone."
    )


# --------------------------------------------------------------------------
# 1. Load a batch
# --------------------------------------------------------------------------

def ingest_sources(sources: list) -> None:
    """Extract text from uploads/paths into session state."""
    with st.spinner(f"Reading {len(sources)} file(s)…"):
        loaded, errors = batch.load_documents(sources)

    st.session_state.docs = loaded
    st.session_state.order = list(loaded)
    st.session_state.selected = st.session_state.order[0] if st.session_state.order else ""
    st.session_state.load_errors = errors


def section_load() -> None:
    st.subheader("1. Load a batch")
    st.caption(
        "Files are read into memory only. Nothing is copied to disk at this "
        "stage, and the originals are never modified."
    )

    upload_tab, folder_tab = st.tabs(["Upload files", "Point at a local folder"])

    with upload_tab:
        nonce = st.session_state.uploader_nonce
        uploaded = st.file_uploader(
            "Choose PDF, DOCX, or TXT files",
            type=list(ingest.SUPPORTED_EXTENSIONS),
            accept_multiple_files=True,
            key=f"uploader_{nonce}",
        )
        if uploaded and st.button("Load uploaded files", type="primary"):
            ingest_sources(list(uploaded))
            st.rerun()

    with folder_tab:
        folder = st.text_input(
            "Folder path",
            key="folder_path",
            placeholder=r"C:\Users\you\Documents\batch",
            help="Read non-recursively. Files already ending in .deid.txt are skipped.",
        )
        if st.button("Load folder", disabled=not folder):
            try:
                paths = batch.list_folder(folder)
            except batch.BatchError as exc:
                st.error(str(exc))
            else:
                ingest_sources([str(p) for p in paths])
                st.rerun()

    for message in st.session_state.load_errors:
        st.warning(message)

    docs = documents()
    if docs:
        st.success(f"Loaded **{len(docs)}** document(s) into memory.")
        oversized = [
            name for name, doc in docs.items()
            if len(doc.raw_text) > deidentify.SOFT_CHAR_LIMIT
        ]
        if oversized:
            st.info(
                "Long document(s) — expect a slower review pass: "
                + ", ".join(f"`{name}`" for name in oversized)
            )


# --------------------------------------------------------------------------
# 2. Process the batch, one document at a time
# --------------------------------------------------------------------------

def section_process() -> None:
    docs = documents()
    order = st.session_state.order
    if not docs:
        return

    st.divider()
    st.subheader("2. De-identify")

    pending = [name for name in order if not docs[name].analyzed]
    st.caption(
        "Documents are processed one at a time on the CPU. The first one also "
        "pays for loading the spaCy model."
    )

    if pending and st.button(
        f"Run de-identification on {len(pending)} document(s)", type="primary"
    ):
        progress = st.progress(0.0)
        label = st.empty()
        total = len(pending)
        for index, name in enumerate(pending, start=1):
            label.write(f"Document {index} of {total} — `{name}`")
            progress.progress((index - 1) / total)
            batch.analyze_document(docs[name])
            progress.progress(index / total)
        label.write(f"Processed {total} document(s).")
        st.rerun()

    analyzed = sum(1 for doc in docs.values() if doc.analyzed)
    st.progress(analyzed / len(order) if order else 0.0)
    st.caption(f"{analyzed} of {len(order)} documents analysed.")

    failures = [doc for doc in docs.values() if doc.error]
    for doc in failures:
        st.error(f"`{doc.name}`: {doc.error}")


# --------------------------------------------------------------------------
# 3. Review & approve, per document
# --------------------------------------------------------------------------

def entity_frame(document: batch.Document) -> pd.DataFrame:
    rows = [
        {
            "value": entity.get("value", ""),
            "type": entity.get("type", "OTHER_ID"),
            "placeholder": entity.get("placeholder", ""),
            "action": mapping.normalise_action(entity.get("action")),
        }
        for entity in document.entities
    ]
    return pd.DataFrame(rows, columns=TABLE_COLUMNS)


def render_entity_table(document: batch.Document) -> None:
    st.markdown("#### Detected identifiers")
    st.caption(
        "Fix a type, correct a value, delete a false positive, or switch an "
        "action to **Keep** to leave that string in the document."
    )

    edited = st.data_editor(
        entity_frame(document),
        num_rows="dynamic",
        use_container_width=True,
        height=420,
        key=f"editor_{document.name}",
        column_config={
            "value": st.column_config.TextColumn(
                "Detected text", required=True, width="large",
                help="Must match the document verbatim. Line breaks inside a "
                     "name are handled for you.",
            ),
            "type": st.column_config.SelectboxColumn(
                "Type", options=list(mapping.ENTITY_TYPES), required=True, width="medium"
            ),
            "placeholder": st.column_config.TextColumn(
                "Placeholder", width="medium",
                help="Leave blank to auto-assign, e.g. [CLINICIAN_1].",
            ),
            "action": st.column_config.SelectboxColumn(
                "Action", options=[mapping.REDACT, mapping.KEEP], required=True, width="small",
                help="Keep leaves the text in place — use it for a false positive "
                     "you would rather not delete from the table.",
            ),
        },
    )

    if st.button("Apply table edits", use_container_width=True, key=f"apply_{document.name}"):
        refresh(document, edited.fillna("").to_dict("records"))
        st.rerun()


def render_add_missed(document: batch.Document) -> None:
    st.markdown("#### Add a missed identifier")
    st.caption(
        "Anything the layers missed. It is variant-expanded like a detected "
        "value, so a full name also covers the title+surname and initials forms."
    )

    value_column, type_column, button_column = st.columns([3, 2, 1])
    with value_column:
        value = st.text_input(
            "Value", key=f"missed_value_{document.name}", label_visibility="collapsed",
            placeholder="Paste the exact text as it appears in the document",
        )
    with type_column:
        entity_type = st.selectbox(
            "Type", list(mapping.ENTITY_TYPES), key=f"missed_type_{document.name}",
            label_visibility="collapsed",
        )
    with button_column:
        add = st.button("Add", use_container_width=True, key=f"missed_add_{document.name}")

    if add:
        try:
            result = deidentify.add_manual_entity(
                document.raw_text, document.entities, value, entity_type
            )
        except deidentify.DeidentificationError as exc:
            st.error(str(exc))
        else:
            document.entities = result.entities
            document.redacted_text = result.redacted_text
            document.phi_map = result.phi_map
            document.approved = False
            document.residual = []
            if value.strip() and value.strip() not in document.raw_text:
                st.warning(
                    f"'{value.strip()}' was added, but that exact string does not "
                    "appear in the document — check spelling and spacing."
                )
            st.rerun()


def render_coverage(document: batch.Document) -> None:
    expanded = mapping.surface_forms(document.entities, document.known_as)

    with st.expander(
        f"Surface forms covered — {len(expanded.forms)} strings from "
        f"{len(document.entities)} rows",
        expanded=False,
    ):
        st.caption(
            "Each row also redacts these derived forms: title+surname, initials, "
            "first+surname, and organisation short forms. Every variant of one "
            "person maps to that person's single placeholder."
        )
        for placeholder, forms in expanded.by_placeholder.items():
            st.markdown(f"**`{placeholder}`** — " + ", ".join(f"`{f}`" for f in sorted(forms)))

    if expanded.ambiguous:
        st.warning(
            "These forms are claimed by more than one identifier and were "
            "assigned to the first: "
            + ", ".join(f"`{form}` → `{kept}`" for form, kept, _ in expanded.ambiguous[:10])
            + ". They are still redacted."
        )

    leftovers = mapping.residual_values(
        document.redacted_text, document.entities, document.known_as
    )
    if leftovers:
        st.warning(
            "These table values still appear in the preview — check for spelling "
            "differences against the document: "
            + ", ".join(f"`{value}`" for value in leftovers[:10])
        )


def write_approved_word(document: batch.Document) -> None:
    """Redact the original .docx using the map the reviewer just approved.

    Detection is not re-run. The map comes from the approved entity table, so
    the Word file cannot drift from the text the reviewer signed off on. The
    write itself re-scans the finished document and refuses it if anything
    identifying survives, so the Word path clears the same bar as the text one.
    """
    if not document.source_bytes:
        return
    try:
        document.approved_docx_path = str(
            batch.write_approved_docx(
                document.name,
                document.source_bytes,
                batch.approved_map(document.entities, document.known_as),
                acknowledged=document.dismissed,
            )
        )
    except batch.BatchError as exc:
        document.approved_docx_path = ""
        st.error(f"Word output blocked — {exc}")


def render_docx_download(document: batch.Document) -> None:
    """Offer the redacted .docx, but only once it has cleared the sweep."""
    if not document.source_bytes:
        return
    if not document.approved_docx_path:
        st.warning(
            "The Word version was not written — the safety sweep found "
            "something in it. The de-identified text above was still approved; "
            "resolve the finding and approve again to get the .docx."
        )
        return

    path = Path(document.approved_docx_path)
    if not path.exists():
        return
    st.download_button(
        "⬇ Download redacted Word document",
        data=path.read_bytes(),
        file_name=path.name,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        key=f"download_docx_{document.name}",
    )
    st.caption(
        f"`{path.name}` keeps the original's tables, styles, headers and "
        "footers. Only the redacted document is written — never the mapping."
    )


_FLAG_TINTS = {
    review_flags.KIND_NAME: "#fff3bf",
    review_flags.KIND_ID: "#ffd8a8",
    review_flags.KIND_DATE: "#d0ebff",
    review_flags.KIND_INITIALS: "#e5dbff",
}


def document_flags(document: batch.Document) -> list:
    """Candidate residuals for this document, recomputed from current text."""
    return review_flags.candidate_residuals(document.redacted_text)


def outstanding_flags(document: batch.Document) -> list:
    return review_flags.outstanding(document_flags(document), flag_dismissals(document))


def flag_dismissals(document: batch.Document) -> list[str]:
    return st.session_state.flag_dismissed.setdefault(document.name, [])


def render_highlighted_preview(document: batch.Document) -> None:
    """The redacted text with candidate residuals tinted in place.

    Tints, not alarm colours: everything highlighted here is a *maybe*, and
    colouring the whole preview red would train the reviewer to ignore it.
    """
    text = document.redacted_text
    remaining = outstanding_flags(document)
    if not remaining:
        st.text_area(
            "Redacted", text, height=420,
            label_visibility="collapsed", disabled=True,
            key=f"preview_clean_{document.name}",
        )
        st.caption("No candidate residuals highlighted in this document.")
        return

    spans = sorted(remaining, key=lambda f: f.char_start)
    parts: list[str] = []
    cursor = 0
    for flag in spans:
        parts.append(html.escape(text[cursor : flag.char_start]))
        tint = _FLAG_TINTS.get(flag.kind, "#f1f3f5")
        parts.append(
            f'<mark style="background:{tint};padding:0 2px;border-radius:2px" '
            f'title="{html.escape(flag.why)}">{html.escape(flag.text)}</mark>'
        )
        cursor = flag.char_end
    parts.append(html.escape(text[cursor:]))

    st.markdown(
        '<div style="white-space:pre-wrap;font-family:ui-monospace,monospace;'
        'font-size:0.82rem;line-height:1.5;max-height:360px;overflow:auto;'
        'border:1px solid rgba(128,128,128,.35);border-radius:6px;padding:10px">'
        + "".join(parts)
        + "</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        f"{len(remaining)} highlighted span(s) need a decision below. "
        "Highlighting is deliberately over-inclusive — most will be nothing."
    )
    # The highlighted view is an aid; this is the authoritative text, and it is
    # byte-for-byte what approval writes.
    st.text_area(
        "Redacted", text, height=200,
        label_visibility="collapsed", disabled=True,
        key=f"preview_exact_{document.name}",
    )


def render_flag_decisions(document: batch.Document) -> None:
    """Redact-or-dismiss, one decision per distinct highlighted value."""
    remaining = outstanding_flags(document)
    if not remaining:
        return

    st.markdown("#### Highlighted spans to check")
    st.caption(
        "Each of these could be an identifier the layers missed. Redact it, or "
        "dismiss it if it is genuinely not identifying. Dismissals apply to "
        "this document only and are never saved."
    )
    for flag in remaining:
        left, middle, right = st.columns([5, 1.4, 1.4])
        with left:
            st.markdown(f"`{flag.text}` — {flag.why}")
        with middle:
            if st.button("Redact this", key=f"flagred_{document.name}_{flag.key}"):
                try:
                    result = deidentify.add_manual_entity(
                        document.raw_text, document.entities, flag.text
                    )
                except deidentify.DeidentificationError as exc:
                    st.error(str(exc))
                else:
                    document.entities = result.entities
                    document.redacted_text = result.redacted_text
                    document.phi_map = result.phi_map
                    document.approved = False
                    st.session_state.flag_redacted[document.name] = (
                        st.session_state.flag_redacted.get(document.name, 0) + 1
                    )
                    st.rerun()
        with right:
            if st.button("Not an identifier", key=f"flagdis_{document.name}_{flag.key}"):
                flag_dismissals(document).append(flag.key)
                st.rerun()


def render_checklist(document: batch.Document) -> list:
    """The adaptive checklist. Returns the items so the gate can read them."""
    flags = document_flags(document)
    features = review_checklist.describe(document, flags, flag_dismissals(document))
    items = review_checklist.build_checklist(features)

    ticked = st.session_state.checklist.setdefault(document.name, set())
    st.markdown("#### Reviewer checklist")
    for item in items:
        disabled = not item.auto_satisfied
        checked = st.checkbox(
            item.label,
            value=item.key in ticked and not disabled,
            disabled=disabled,
            key=f"chk_{document.name}_{item.key}",
        )
        if checked and not disabled:
            ticked.add(item.key)
        else:
            ticked.discard(item.key)
        if item.hint:
            st.caption(item.hint)

    # The text-box affirmation and the Word path's B6 acknowledgement are the
    # same statement; ticking one is ticking the other.
    if any(item.key == "textboxes" for item in items):
        document.text_boxes_acknowledged = "textboxes" in ticked
    return items


def render_approval(document: batch.Document) -> None:
    st.divider()
    st.warning(
        "**Human review required.** Automated de-identification is not a "
        "guarantee. Read the preview in full before approving."
    )

    if document.residual:
        st.error(
            "**Approval blocked — the safety sweep found what still look like "
            "identifiers:**\n\n"
            + "\n".join(f"- `{value}`" for value in document.residual)
        )
        st.caption(
            "Handle each one: add it as a missed identifier above so it gets "
            "redacted, or — if it is genuinely not identifying (a town used as a "
            "place of care, a ward name) — dismiss it. Dismissals apply to this "
            "document only and are not saved anywhere."
        )
        for value in document.residual:
            if st.button(
                f"Dismiss `{value}` — not an identifier",
                key=f"dismiss_{document.name}_{value}",
            ):
                document.dismissed.append(value)
                document.residual = batch.sweep(document.redacted_text, document.dismissed)
                st.rerun()

    if document.dismissed:
        st.caption("Dismissed this document: " + ", ".join(f"`{v}`" for v in document.dismissed))

    if document.approved:
        st.success(f"Approved. Written to `{document.approved_path}`")
        render_docx_download(document)

    # A .docx whose text boxes this pass cannot reach must not slip through on
    # the reviewer's assumption that the preview covered everything. The
    # checklist item below carries the acknowledgement.
    if document.has_text_boxes:
        st.error(
            "**This document contains text boxes, shapes, or embedded objects.** "
            "Their contents are **not** redacted automatically and do not appear "
            "in the preview above. Open the original and check them by hand."
        )

    items = render_checklist(document)
    ticked = st.session_state.checklist.get(document.name, set())
    reason = review_checklist.blocking_reason(
        items, ticked, document.residual, len(outstanding_flags(document))
    )

    if st.button(
        "✅ Run safety sweep and approve",
        type="primary",
        disabled=bool(reason) or not document.redacted_text,
        key=f"approve_{document.name}",
    ):
        document.residual = batch.sweep(document.redacted_text, document.dismissed)
        if document.residual:
            document.approved = False
        else:
            try:
                path = batch.write_approved(
                    document.name, document.redacted_text, acknowledged=document.dismissed
                )
            except batch.BatchError as exc:
                st.error(str(exc))
            else:
                document.approved = True
                document.approved_path = str(path)
                write_approved_word(document)
                batch.write_review_record(
                    document.name,
                    ticked=sorted(ticked),
                    entities=document.entities,
                    flags_shown=len(document_flags(document)),
                    flags_redacted=st.session_state.flag_redacted.get(document.name, 0),
                    flags_dismissed=len(flag_dismissals(document)),
                )
        st.rerun()

    if reason:
        st.caption(f"Approve is disabled — {reason}")

    st.caption(
        f"Approved files are written to `{batch.OUTPUT_DIR}` as de-identified "
        "text only. The identity mapping stays in memory and is never saved."
    )


def section_review() -> None:
    docs = documents()
    order = st.session_state.order
    if not docs:
        return

    ready = [name for name in order if docs[name].analyzed and not docs[name].error]
    if not ready:
        return

    st.divider()
    st.subheader("3. Review & approve")

    if st.session_state.selected not in ready:
        st.session_state.selected = ready[0]

    def label(name: str) -> str:
        doc = docs[name]
        position = order.index(name) + 1
        mark = "✅" if doc.approved else ("⛔" if doc.residual else "🔵")
        return f"{mark} {position}/{len(order)} — {name}"

    # The index is computed rather than keyed, so the selector survives a
    # document being removed or the batch being reloaded.
    st.session_state.selected = st.radio(
        "Document under review",
        ready,
        index=ready.index(st.session_state.selected),
        format_func=label,
    )

    document = docs[st.session_state.selected]
    st.markdown(f"### `{document.name}`")
    st.caption(
        f"Document {order.index(document.name) + 1} of {len(order)} — "
        f"{len(document.raw_text):,} characters, {len(document.entities)} identifiers detected."
    )

    left, right = st.columns(2)
    with left:
        render_entity_table(document)
    with right:
        st.markdown("#### Redacted preview")
        st.caption("This exact text is what approval writes to disk.")
        render_highlighted_preview(document)

    render_flag_decisions(document)
    render_add_missed(document)
    render_coverage(document)

    with st.expander("View original text (contains PHI)", expanded=False):
        st.text_area(
            "Original", document.raw_text, height=300,
            label_visibility="collapsed", disabled=True,
            key=f"raw_{document.name}",
        )

    render_approval(document)


# --------------------------------------------------------------------------
# 4. Batch status
# --------------------------------------------------------------------------

def section_batch_status() -> None:
    docs = documents()
    order = st.session_state.order
    if not docs:
        return

    st.divider()
    st.subheader("4. Batch status")

    rows = []
    for position, name in enumerate(order, start=1):
        doc = docs[name]
        if doc.error:
            state = "❌ Failed"
        elif doc.approved:
            state = "✅ Approved"
        elif doc.residual:
            state = "⛔ Blocked by safety sweep"
        elif doc.analyzed:
            state = "🔍 Awaiting review"
        else:
            state = "⏳ Not yet processed"
        rows.append(
            {
                "#": position,
                "Document": name,
                "Status": state,
                "Identifiers": len(doc.entities),
                "Approved output": doc.approved_path or "—",
            }
        )

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    approved = sum(1 for doc in docs.values() if doc.approved)
    st.caption(f"{approved} of {len(order)} approved.")


# --------------------------------------------------------------------------
# 5. Handoff — deliberately not wired up
# --------------------------------------------------------------------------

def _draft_state(name: str) -> dict:
    return st.session_state.drafts.setdefault(
        name, {"deidentified": "", "reidentified": "", "history": [], "unresolved": []}
    )


def render_generation_status() -> dict:
    """Daemon and model status, with the fix if something is missing."""
    status = ollama_client.status()
    if not status["up"]:
        st.error("Local model backend is not running.")
        st.code(status["message"], language="text")
        return status
    if not status["models"]:
        st.warning("Ollama is running but no model is installed.")
        st.code("ollama pull llama3.1:8b", language="bash")
        return status
    st.success(
        f"Ollama running on {status['host']} · "
        f"{len(status['models'])} model(s) installed"
    )
    return status


def render_generation_panel(document: batch.Document) -> None:
    """Generate, refine, re-identify and export — for one approved document."""
    state = _draft_state(document.name)
    status = render_generation_status()

    left, right = st.columns([1, 1])
    with left:
        model = st.selectbox(
            "Model",
            status["models"] or ["(none installed)"],
            index=(
                status["models"].index(status["default_model"])
                if status["default_model"] in (status["models"] or [])
                else 0
            ),
            key=f"model_{document.name}",
            disabled=not status["models"],
        )
    with right:
        template = st.selectbox(
            "Template", carenotes.template_names(), key=f"tpl_{document.name}"
        )

    custom = ""
    if template == carenotes.CUSTOM_TEMPLATE:
        custom = st.text_area(
            "Your template / instructions",
            key=f"custom_{document.name}",
            height=140,
            placeholder="Paste your house format here…",
        )

    ready = bool(status["up"] and status["models"])
    if st.button(
        "✨ Generate draft",
        type="primary",
        disabled=not ready,
        key=f"gen_{document.name}",
    ):
        _run_generation(document, model, template, custom, state)

    if state["deidentified"]:
        render_draft(document, state)


def _stream_into(placeholder, chunks, started: float) -> str:
    """Render a stream token by token so a slow local model looks alive."""
    collected: list[str] = []
    for chunk in chunks:
        collected.append(chunk)
        placeholder.markdown(
            "".join(collected) + " ▌"
            + f"\n\n*{time.monotonic() - started:.0f}s elapsed*"
        )
    return "".join(collected)


def _run_generation(document, model, template, custom, state) -> None:
    """First-pass generation. The model receives de-identified text only."""
    placeholder = st.empty()
    started = time.monotonic()
    try:
        with st.spinner("Drafting locally — an 8B model on CPU takes a minute…"):
            chunks = carenotes.generate_document(
                document.redacted_text,
                template,
                carenotes.OllamaBackend(model),
                stream=True,
                custom_instruction=custom,
                # Passed only so generation can assert these are absent.
                phi_values=list(document.phi_map.values()),
            )
            draft = _stream_into(placeholder, chunks, started)
    except carenotes.CareNoteError as exc:
        placeholder.empty()
        st.error(str(exc))
        return

    placeholder.empty()
    state["deidentified"] = carenotes.with_banner(draft)
    state["reidentified"] = ""
    state["unresolved"] = []
    state["history"] = []
    st.rerun()


def render_draft(document: batch.Document, state: dict) -> None:
    """The de-identified draft, refinement, re-identification, and exports."""
    st.markdown("#### Draft (de-identified)")
    st.caption(
        "Still contains placeholders — safe to display, share, and save. This "
        "is what the model produced."
    )
    st.markdown(state["deidentified"])

    stem = batch.safe_stem(document.name)
    col_md, col_txt, col_docx = st.columns(3)
    with col_md:
        st.download_button(
            "⬇ .md", state["deidentified"], file_name=f"{stem}.draft.md",
            mime="text/markdown", key=f"dl_md_{document.name}",
        )
    with col_txt:
        st.download_button(
            "⬇ .txt", state["deidentified"], file_name=f"{stem}.draft.txt",
            mime="text/plain", key=f"dl_txt_{document.name}",
        )
    with col_docx:
        st.download_button(
            "⬇ .docx", _as_docx(state["deidentified"]),
            file_name=f"{stem}.draft.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key=f"dl_docx_{document.name}",
        )

    render_refinement(document, state)
    render_reidentification(document, state)


def render_refinement(document: batch.Document, state: dict) -> None:
    """Follow-up instructions, on de-identified text only."""
    with st.expander("Refine this draft", expanded=False):
        st.caption(
            "Refinement runs on the same de-identified source and the current "
            "draft. No real identifier enters this loop."
        )
        for instruction, _ in state["history"]:
            st.markdown(f"- _{instruction}_")
        instruction = st.text_input(
            "What would you like changed?",
            key=f"refine_{document.name}",
            placeholder="e.g. make the plan more concise; add a risk paragraph",
        )
        status = ollama_client.status()
        if st.button(
            "Apply", key=f"refine_go_{document.name}",
            disabled=not instruction or not status["models"],
        ):
            placeholder = st.empty()
            started = time.monotonic()
            try:
                with st.spinner("Revising…"):
                    chunks = carenotes.refine_document(
                        document.redacted_text,
                        state["deidentified"],
                        instruction,
                        carenotes.OllamaBackend(
                            st.session_state.get(
                                f"model_{document.name}", status["default_model"]
                            )
                        ),
                        stream=True,
                        history=state["history"],
                        phi_values=list(document.phi_map.values()),
                    )
                    revised = _stream_into(placeholder, chunks, started)
            except carenotes.CareNoteError as exc:
                placeholder.empty()
                st.error(str(exc))
                return
            placeholder.empty()
            state["history"].append((instruction, ""))
            state["deidentified"] = carenotes.with_banner(revised)
            state["reidentified"] = ""
            state["unresolved"] = []
            st.rerun()


def render_reidentification(document: batch.Document, state: dict) -> None:
    """Opt-in, local-only substitution of placeholders back to real values."""
    st.markdown("#### Re-identify for the patient record (local only)")
    st.warning(
        "**This produces a document containing real patient identifiers.** It "
        "is for saving into your own local record. It happens entirely in "
        "Python on this machine — the model never sees it, and the identity "
        "mapping is still never written to disk."
    )

    issues = mapping.check_placeholder_integrity(
        state["deidentified"], list(document.phi_map)
    )
    mangled = [i for i in issues if i.kind == mapping.ISSUE_MANGLED]
    if mangled:
        st.caption(
            "Placeholders the model corrupted, repaired automatically: "
            + ", ".join(f"`{i.token}` → `{i.suggestion}`" for i in mangled)
        )

    if st.button(
        "🔓 Re-identify locally", key=f"reid_{document.name}",
        disabled=not document.phi_map,
    ):
        text, unresolved = carenotes.finalise(state["deidentified"], document.phi_map)
        state["reidentified"] = text
        state["unresolved"] = unresolved
        st.rerun()

    if state["unresolved"]:
        st.error(
            "**Blocked — these placeholders could not be resolved:** "
            + ", ".join(f"`{token}`" for token in state["unresolved"])
            + "\n\nA report filed with a placeholder still in it is worse than "
            "no report. Refine the draft or correct the identifier table, then "
            "re-identify again."
        )
        return

    if state["reidentified"]:
        st.success("Re-identified. Every placeholder resolved.")
        st.markdown(state["reidentified"])
        stem = batch.safe_stem(document.name)
        col_md, col_docx = st.columns(2)
        with col_md:
            st.download_button(
                "⬇ .md (contains PHI)", state["reidentified"],
                file_name=f"{stem}.record.md", mime="text/markdown",
                key=f"dlr_md_{document.name}",
            )
        with col_docx:
            st.download_button(
                "⬇ .docx (contains PHI)", _as_docx(state["reidentified"]),
                file_name=f"{stem}.record.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"dlr_docx_{document.name}",
            )


def _as_docx(text: str) -> bytes:
    """Render generated text to a .docx in memory — nothing touches disk."""
    from docx import Document as DocxDocument

    buffer = io.BytesIO()
    doc = DocxDocument()
    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("### "):
            doc.add_heading(stripped[4:], level=3)
        elif stripped.startswith("## "):
            doc.add_heading(stripped[3:], level=2)
        elif stripped.startswith("# "):
            doc.add_heading(stripped[2:], level=1)
        else:
            doc.add_paragraph(line)
    doc.save(buffer)
    return buffer.getvalue()


def section_handoff() -> None:
    docs = documents()
    st.divider()
    st.subheader("5. Generate report")

    approved = [doc for doc in docs.values() if doc.approved]
    if not approved:
        st.button(
            "Generate report", disabled=True,
            help=carenotes.DISABLED_MESSAGE, use_container_width=False,
        )
        st.info(carenotes.DISABLED_MESSAGE)
        st.caption(
            "Generation runs only on approved text. The model receives the "
            "de-identified document and nothing else — the identity mapping "
            "has no path out of this process."
        )
        return

    st.caption(
        f"{len(approved)} approved document(s). The model receives the "
        "de-identified text only; re-identification happens afterwards, "
        "locally, in Python."
    )
    chosen = st.selectbox(
        "Document", [doc.name for doc in approved], key="gen_doc"
    )
    document = documents().get(chosen)
    if document is not None:
        render_generation_panel(document)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> None:
    render_sidebar()

    st.title("CareScribe — de-identification & review")
    st.caption(
        "Load a batch, de-identify each document locally on the CPU, review and "
        "correct what was found, then approve. Nothing leaves this machine."
    )

    section_load()
    section_process()
    section_review()
    section_batch_status()
    section_handoff()


main()
