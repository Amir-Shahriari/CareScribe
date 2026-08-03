"""
CareScribe — local, privacy-preserving clinical documentation.

Run with:  streamlit run carescribe/app.py

Privacy model
-------------
* All inference goes to a local Ollama server on 127.0.0.1. No cloud calls.
* Uploaded documents, detected identifiers, and the PHI map live only in
  ``st.session_state`` (server-side RAM). Nothing is written to disk.
* Files reach the filesystem only when the user clicks a download button.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Allow `streamlit run carescribe/app.py` to resolve the `carescribe` package
# by putting its parent directory on sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from carescribe.core import carenotes, deidentify, ingest, mapping, ollama_client  # noqa: E402
from carescribe.prompts.carenotes_prompt import CUSTOM_TEMPLATE_LABEL  # noqa: E402

STEPS = ["Upload", "De-identify", "Generate notes", "Export"]

# Telemetry is also disabled in .streamlit/config.toml; this is belt and braces.
st.set_page_config(page_title="CareScribe", page_icon="🩺", layout="wide")


# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------

# Every key that can hold PHI or PHI-derived data. "Wipe PHI" clears exactly this
# list, so adding a new PHI-bearing key means adding it here too.
PHI_KEYS = {
    "raw_text": "",
    "file_name": "",
    "entities": [],          # [{type, value, placeholder}]
    "redacted_text": "",
    "phi_map": {},           # placeholder -> original value
    "deid_confirmed": False,
    "note_text": "",
    "note_reidentified": "",
    "custom_instruction": "",
    "placeholder_repairs": [],  # [(mangled, repaired)] from the last generation
}

DEFAULTS = {**PHI_KEYS, "step": 0, "use_separate_model": False, "template": "SOAP note"}


def init_state() -> None:
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            # Copy mutables so the defaults dict isn't shared across sessions.
            st.session_state[key] = value.copy() if isinstance(value, (dict, list)) else value


def wipe_phi() -> None:
    """Drop every piece of PHI from memory and return to step 1."""
    for key, value in PHI_KEYS.items():
        st.session_state[key] = value.copy() if isinstance(value, (dict, list)) else value
    st.session_state.step = 0
    # Force the file uploader to forget its file by rotating its widget key.
    st.session_state.uploader_nonce = st.session_state.get("uploader_nonce", 0) + 1


init_state()


# --------------------------------------------------------------------------
# Sidebar: Ollama status, model selection, wipe
# --------------------------------------------------------------------------

def render_sidebar() -> tuple[str, str]:
    """Draw the sidebar. Returns ``(deid_model, notes_model)``."""
    st.sidebar.title("🩺 CareScribe")
    st.sidebar.caption("Local-only. No data leaves this machine.")

    available = ollama_client.is_available()
    models = ollama_client.list_models() if available else []

    if available:
        st.sidebar.success("🟢 Ollama connected")
    else:
        st.sidebar.error("🔴 Ollama unreachable")
        st.sidebar.info(ollama_client.NOT_RUNNING_HINT)

    if st.sidebar.button("↻ Refresh connection", use_container_width=True):
        st.rerun()

    st.sidebar.divider()

    deid_model = ""
    notes_model = ""

    if available and not models:
        st.sidebar.warning(
            "Ollama is running but no models are installed.\n\n"
            "Run:  `ollama pull llama3.1:8b`"
        )
    elif models:
        st.sidebar.subheader("Models")
        deid_model = st.sidebar.selectbox(
            "De-identification model", models, key="deid_model",
            help="Reliable JSON output matters most here. llama3.1:8b is a safe default.",
        )

        use_separate = st.sidebar.toggle(
            "Use a separate model for care notes",
            key="use_separate_model",
            help="On a single 8GB GPU, leaving this off is faster — swapping models "
                 "forces a reload between stages.",
        )
        if use_separate:
            notes_model = st.sidebar.selectbox("Care note model", models, key="notes_model")
        else:
            notes_model = deid_model

    st.sidebar.divider()

    st.sidebar.subheader("Session")
    held = sum(
        1 for key in ("raw_text", "redacted_text", "note_text") if st.session_state.get(key)
    )
    st.sidebar.caption(
        f"In memory: {len(st.session_state.entities)} identifiers, {held}/3 text blocks."
    )

    if st.sidebar.button("🧹 Clear session / wipe PHI", type="primary", use_container_width=True):
        wipe_phi()
        st.rerun()

    st.sidebar.caption(
        "Wipe clears the document, identifier table, and name map from memory. "
        "Nothing was ever written to disk."
    )

    return deid_model, notes_model


# --------------------------------------------------------------------------
# Step navigation
# --------------------------------------------------------------------------

def render_stepper() -> None:
    columns = st.columns(len(STEPS))
    for index, (column, label) in enumerate(zip(columns, STEPS)):
        with column:
            if index < st.session_state.step:
                column.markdown(f"✅ **{index + 1}. {label}**")
            elif index == st.session_state.step:
                column.markdown(f"🔵 **{index + 1}. {label}**")
            else:
                column.markdown(f"⚪ {index + 1}. {label}")
    st.divider()


def nav_buttons(can_advance: bool, next_label: str = "Next →") -> None:
    """Back / Next footer. ``can_advance`` gates the Next button."""
    st.divider()
    back_column, _, next_column = st.columns([1, 4, 1])

    with back_column:
        if st.session_state.step > 0 and st.button("← Back", use_container_width=True):
            st.session_state.step -= 1
            st.rerun()

    with next_column:
        if st.session_state.step < len(STEPS) - 1:
            if st.button(
                next_label, disabled=not can_advance, type="primary", use_container_width=True
            ):
                st.session_state.step += 1
                st.rerun()


# --------------------------------------------------------------------------
# Step 1 — Upload
# --------------------------------------------------------------------------

def step_upload() -> None:
    st.subheader("1. Upload a patient document")
    st.caption("The file is read into memory only. It is never saved to disk.")

    nonce = st.session_state.get("uploader_nonce", 0)
    uploaded = st.file_uploader(
        "Choose a PDF, DOCX, or TXT file",
        type=list(ingest.SUPPORTED_EXTENSIONS),
        key=f"uploader_{nonce}",
    )

    if uploaded is not None and uploaded.name != st.session_state.file_name:
        try:
            with st.spinner("Extracting text…"):
                st.session_state.raw_text = ingest.extract_text(uploaded)
            st.session_state.file_name = uploaded.name
            # A new document invalidates everything downstream.
            st.session_state.entities = []
            st.session_state.redacted_text = ""
            st.session_state.phi_map = {}
            st.session_state.deid_confirmed = False
            st.session_state.note_text = ""
            st.session_state.note_reidentified = ""
        except ingest.IngestError as exc:
            st.error(str(exc))

    if st.session_state.raw_text:
        characters = len(st.session_state.raw_text)
        st.success(f"Loaded **{st.session_state.file_name}** — {characters:,} characters.")

        if characters > deidentify.SOFT_CHAR_LIMIT:
            st.warning(
                f"This document is long ({characters:,} characters). It may exceed the "
                f"model's context window, and identifiers past the cutoff would go "
                f"undetected. Consider splitting it into sections."
            )

        with st.expander("View extracted raw text (contains PHI)", expanded=False):
            st.text_area(
                "Raw text", st.session_state.raw_text, height=400,
                label_visibility="collapsed", disabled=True,
            )

    nav_buttons(can_advance=bool(st.session_state.raw_text))


# --------------------------------------------------------------------------
# Step 2 — De-identify
# --------------------------------------------------------------------------

def step_deidentify(deid_model: str) -> None:
    st.subheader("2. De-identify")
    st.caption(
        "The model detects identifiers; replacement is done deterministically in "
        "Python. Review and correct the table before continuing."
    )

    run_label = "Re-run de-identification" if st.session_state.entities else "Run de-identification"
    if st.button(run_label, type="primary", disabled=not deid_model):
        if not deid_model:
            st.error("Select a model in the sidebar first.")
        else:
            try:
                with st.spinner(f"Scanning for identifiers with {deid_model}…"):
                    result = deidentify.deidentify(deid_model, st.session_state.raw_text)
                st.session_state.entities = result.entities
                st.session_state.redacted_text = result.redacted_text
                st.session_state.phi_map = result.phi_map
                st.session_state.deid_confirmed = False
                if result.retried:
                    st.info("The model's first reply wasn't valid JSON; the retry succeeded.")
            except (deidentify.DeidentificationError, ollama_client.OllamaError) as exc:
                st.error(str(exc))

    if not st.session_state.entities and not st.session_state.redacted_text:
        st.info("Run de-identification to continue.")
        nav_buttons(can_advance=False)
        return

    left, right = st.columns(2)

    # --- (a) editable identifier table ---
    with left:
        st.markdown("#### Detected identifiers")
        st.caption("Edit values, fix types, add missed identifiers, or delete false positives.")

        frame = pd.DataFrame(
            st.session_state.entities or [], columns=["type", "value", "placeholder"]
        )

        edited = st.data_editor(
            frame,
            num_rows="dynamic",
            use_container_width=True,
            height=420,
            key="entity_editor",
            column_config={
                "type": st.column_config.SelectboxColumn(
                    "Type", options=list(mapping.ENTITY_TYPES), required=True, width="medium"
                ),
                "value": st.column_config.TextColumn(
                    "Original value", required=True, width="large",
                    help="Must match the document verbatim.",
                ),
                "placeholder": st.column_config.TextColumn(
                    "Placeholder", width="medium",
                    help="Leave blank to auto-assign, e.g. [MRN_1].",
                ),
            },
        )

        if st.button("Apply table edits", use_container_width=True):
            records = edited.fillna("").to_dict("records")
            result = deidentify.rebuild(st.session_state.raw_text, records)
            st.session_state.entities = result.entities
            st.session_state.redacted_text = result.redacted_text
            st.session_state.phi_map = result.phi_map
            st.session_state.deid_confirmed = False
            st.rerun()

    # --- (b) redacted preview ---
    with right:
        st.markdown("#### Redacted text preview")
        st.caption("This is the only text passed to the care note stage.")
        st.text_area(
            "Redacted", st.session_state.redacted_text, height=420,
            label_visibility="collapsed", disabled=True,
        )

    # Detected from the raw text: the redacted copy no longer contains the
    # "Known as" field to read it back out of.
    known_as = mapping.find_known_as(st.session_state.raw_text)

    # Show the reviewer every string that will actually be matched, not just the
    # table rows — variant expansion means one row covers many surface forms.
    expanded = mapping.surface_forms(st.session_state.entities, known_as)
    with st.expander(
        f"Surface forms covered ({len(expanded.forms)} strings from "
        f"{len(st.session_state.entities)} rows)",
        expanded=False,
    ):
        st.caption(
            "Each row above also redacts these derived forms — title+surname, "
            "initials, first+surname, and facility short forms. All variants of "
            "one person map to that person's single placeholder."
        )
        for placeholder, forms in expanded.by_placeholder.items():
            st.markdown(
                f"**`{placeholder}`** — " + ", ".join(f"`{f}`" for f in sorted(forms))
            )

    if expanded.ambiguous:
        st.warning(
            "These forms are claimed by more than one identifier and were "
            "assigned to the first: "
            + ", ".join(f"`{form}` → `{kept}`" for form, kept, _ in expanded.ambiguous[:10])
            + ". They are still redacted, but re-identification may restore the "
            "wrong name for that form."
        )

    # Self-check: did every form actually get replaced?
    leftovers = mapping.residual_values(
        st.session_state.redacted_text, st.session_state.entities, known_as
    )
    if leftovers:
        st.warning(
            "These forms still appear in the redacted text — check for "
            "spelling differences between the table and the document: "
            + ", ".join(f"`{value}`" for value in leftovers[:10])
        )

    st.divider()
    st.warning(
        "**Human review required.** LLM de-identification is not a guarantee. "
        "Read the redacted preview in full and confirm no identifiers remain."
    )

    if st.session_state.deid_confirmed:
        st.success("De-identification confirmed.")
    if st.button(
        "✔ Confirm de-identification",
        type="primary",
        disabled=st.session_state.deid_confirmed or not st.session_state.redacted_text,
    ):
        st.session_state.deid_confirmed = True
        st.rerun()

    nav_buttons(can_advance=st.session_state.deid_confirmed)


# --------------------------------------------------------------------------
# Step 3 — Generate care notes
# --------------------------------------------------------------------------

def step_generate(notes_model: str) -> None:
    st.subheader("3. Generate care notes")
    st.caption(f"Only the de-identified text is sent to the model (`{notes_model or 'no model'}`).")

    if not st.session_state.deid_confirmed:
        st.error("Confirm de-identification in step 2 first.")
        nav_buttons(can_advance=False)
        return

    template = st.radio(
        "Template", carenotes.TEMPLATE_LABELS, horizontal=True, key="template"
    )

    if template == CUSTOM_TEMPLATE_LABEL:
        st.text_area(
            "Custom instruction",
            key="custom_instruction",
            height=120,
            placeholder="e.g. Write a discharge summary for the community nursing team, "
                        "max 300 words, bullet points under each heading.",
        )

    reinsert = st.checkbox(
        "Re-insert real names into final notes",
        value=False,
        help="Placeholders are mapped back to originals AFTER generation, in Python. "
             "The model never sees the real values. The result contains PHI.",
    )

    if st.button("Generate", type="primary", disabled=not notes_model):
        container = st.container()
        container.markdown("#### Generated note")
        target = container.empty()
        collected: list[str] = []

        try:
            stream = carenotes.generate_stream(
                model=notes_model,
                deidentified_text=st.session_state.redacted_text,
                template=template,
                custom_instruction=st.session_state.custom_instruction,
            )
            for delta in stream:
                collected.append(delta)
                target.markdown("".join(collected))

            note = "".join(collected).strip()
            st.session_state.note_text = note

            # Tolerant re-identification: the note model sometimes corrupts a
            # placeholder while rewriting ([MATIENT_2] for [PATIENT_2]).
            restored = mapping.reidentify_detailed(note, st.session_state.phi_map)
            st.session_state.note_reidentified = restored.text
            st.session_state.placeholder_repairs = restored.corrected
            st.rerun()

        except (carenotes.CareNoteError, ollama_client.OllamaError) as exc:
            st.error(str(exc))

    if st.session_state.note_text:
        st.markdown("#### Generated note")

        display = (
            st.session_state.note_reidentified if reinsert else st.session_state.note_text
        )
        if reinsert:
            st.error("⚠ The note below contains real PHI.")

        st.markdown(display)

        repairs = st.session_state.get("placeholder_repairs") or []
        if repairs:
            st.info(
                "The model corrupted some placeholders while writing; these were "
                "repaired automatically: "
                + ", ".join(f"`{bad}` → `{good}`" for bad, good in repairs)
            )

        unknown = carenotes.find_unknown_placeholders(
            st.session_state.note_text, st.session_state.phi_map
        )
        if unknown:
            st.warning(
                "The model produced placeholders that aren't in the map and are "
                "too corrupted to match confidently, so they cannot be "
                "re-identified: " + ", ".join(f"`{p}`" for p in unknown)
            )

    nav_buttons(can_advance=bool(st.session_state.note_text))


# --------------------------------------------------------------------------
# Step 4 — Export
# --------------------------------------------------------------------------

def step_export() -> None:
    st.subheader("4. Export")
    st.caption("Nothing is written to disk until you click a download button.")

    stem = Path(st.session_state.file_name or "carescribe").stem

    include_phi = st.checkbox(
        "Include a PHI version of the care note (names re-inserted)",
        value=False,
        help="Only tick this if you are saving to an approved, secure location.",
    )
    if include_phi:
        st.error("⚠ The PHI download below is not de-identified. Handle accordingly.")

    st.markdown("#### De-identified text")
    text_column, markdown_column = st.columns(2)
    with text_column:
        st.download_button(
            "⬇ Download .txt",
            data=st.session_state.redacted_text,
            file_name=f"{stem}_deidentified.txt",
            mime="text/plain",
            disabled=not st.session_state.redacted_text,
            use_container_width=True,
        )
    with markdown_column:
        st.download_button(
            "⬇ Download .md",
            data=f"# De-identified document\n\n{st.session_state.redacted_text}\n",
            file_name=f"{stem}_deidentified.md",
            mime="text/markdown",
            disabled=not st.session_state.redacted_text,
            use_container_width=True,
        )

    st.markdown("#### Care note (de-identified)")
    note_text_column, note_markdown_column = st.columns(2)
    with note_text_column:
        st.download_button(
            "⬇ Download .txt",
            data=st.session_state.note_text,
            file_name=f"{stem}_carenote.txt",
            mime="text/plain",
            disabled=not st.session_state.note_text,
            use_container_width=True,
            key="note_txt",
        )
    with note_markdown_column:
        st.download_button(
            "⬇ Download .md",
            data=st.session_state.note_text,
            file_name=f"{stem}_carenote.md",
            mime="text/markdown",
            disabled=not st.session_state.note_text,
            use_container_width=True,
            key="note_md",
        )

    if include_phi:
        st.markdown("#### Care note (PHI re-inserted) ⚠")
        phi_text_column, phi_markdown_column = st.columns(2)
        with phi_text_column:
            st.download_button(
                "⬇ Download .txt (contains PHI)",
                data=st.session_state.note_reidentified,
                file_name=f"{stem}_carenote_PHI.txt",
                mime="text/plain",
                disabled=not st.session_state.note_reidentified,
                use_container_width=True,
                key="phi_txt",
            )
        with phi_markdown_column:
            st.download_button(
                "⬇ Download .md (contains PHI)",
                data=st.session_state.note_reidentified,
                file_name=f"{stem}_carenote_PHI.md",
                mime="text/markdown",
                disabled=not st.session_state.note_reidentified,
                use_container_width=True,
                key="phi_md",
            )

    st.divider()
    st.info(
        "Finished? Click **Clear session / wipe PHI** in the sidebar to drop the "
        "document, the identifier table, and the name map from memory."
    )

    nav_buttons(can_advance=False)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> None:
    deid_model, notes_model = render_sidebar()

    st.title("CareScribe")
    st.caption(
        "De-identify patient documents with a local LLM, then draft care notes "
        "from the de-identified text. Nothing leaves this machine."
    )

    render_stepper()

    step = st.session_state.step
    if step == 0:
        step_upload()
    elif step == 1:
        step_deidentify(deid_model)
    elif step == 2:
        step_generate(notes_model)
    else:
        step_export()


main()
