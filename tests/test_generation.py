"""
Local generation: the privacy contract, placeholder integrity, and the gate.

No live model runs here. The backend is mocked throughout — a test suite that
depends on an 8B model being installed tests the machine, not the code, and the
properties that matter are all about what we *hand* the model and what we do
with what comes back.

Everything here is fabricated.
"""

import pytest

from carescribe.core import carenotes, mapping, ollama_client

# A fixture mapping: placeholder -> the real value it stands for.
PHI_MAP = {
    "[PATIENT]": "Mariam Aisha Rahman",
    "[RELATIVE_1]": "Yusuf Rahman",
    "[CLINICIAN_1]": "Dr H. Okonkwo",
    "[MRN]": "990214",
    "[NHS_NO]": "943 476 5919",
    "[DATE_1]": "3 April 1971",
}

DEIDENTIFIED = """Patient: [PATIENT]
NHS No: [NHS_NO]
Hospital No: [MRN]
Date of Birth: [DATE_1]

[PATIENT] was reviewed by [CLINICIAN_1] in clinic. [RELATIVE_1] attended.
Olanzapine 10mg at night was continued. HoNOS was 18.
"""


class RecordingBackend:
    """Captures exactly what generation handed the model."""

    def __init__(self, reply: str = "Draft body."):
        self.reply = reply
        self.system = ""
        self.prompt = ""
        self.calls = 0

    def generate(self, system, prompt, stream=True):
        self.calls += 1
        self.system = system
        self.prompt = prompt
        yield self.reply


# ==========================================================================
# The no-PHI guard — the invariant the whole project rests on
# ==========================================================================

@pytest.mark.parametrize("value", sorted(PHI_MAP.values()))
def test_no_real_identifier_reaches_the_backend(value):
    backend = RecordingBackend()
    list(
        carenotes.generate_document(
            DEIDENTIFIED, "SOAP care note", backend,
            phi_values=list(PHI_MAP.values()),
        )
    )
    assert value not in backend.prompt
    assert value not in backend.system


def test_the_prompt_carries_the_placeholders_instead():
    backend = RecordingBackend()
    list(carenotes.generate_document(DEIDENTIFIED, "SOAP care note", backend))
    for placeholder in PHI_MAP:
        assert placeholder in backend.prompt


def test_generation_refuses_text_that_still_holds_a_mapping_value():
    """A bug upstream must crash here, not send quietly."""
    leaky = DEIDENTIFIED + "\nSigned: Mariam Aisha Rahman\n"
    backend = RecordingBackend()
    with pytest.raises(carenotes.CareNoteError) as excinfo:
        list(
            carenotes.generate_document(
                leaky, "SOAP care note", backend,
                phi_values=list(PHI_MAP.values()),
            )
        )
    assert "identity mapping" in str(excinfo.value)
    assert backend.calls == 0


def test_generation_refuses_an_identifier_no_layer_ever_detected():
    """The complement of the mapping-value check: a leaked identifier that was
    never detected is not in `phi_values`, so only a residual re-scan catches
    it. This is the NER-recall backstop, at the last possible moment."""
    leaky = DEIDENTIFIED + "\nCall 07700 900461 if the picture changes.\n"
    backend = RecordingBackend()
    with pytest.raises(carenotes.CareNoteError) as excinfo:
        list(
            carenotes.generate_document(
                leaky, "SOAP care note", backend,
                phi_values=list(PHI_MAP.values()),
            )
        )
    assert "07700 900461" in str(excinfo.value)
    assert backend.calls == 0


def test_a_finding_the_reviewer_cleared_does_not_block_generation():
    """`acknowledged` carries the residual-sweep findings approval accepted
    (a town used as a place of care, say). Generation must not re-litigate
    them."""
    kept = DEIDENTIFIED + "\nSeen at the community clinic in Harrogate.\n"
    backend = RecordingBackend()
    list(
        carenotes.generate_document(
            kept, "SOAP care note", backend,
            phi_values=list(PHI_MAP.values()),
            acknowledged=["Harrogate"],
        )
    )
    assert backend.calls == 1


def test_refine_also_rescans_the_source_for_missed_identifiers():
    leaky = DEIDENTIFIED + "\nSigned by Adeyinka Okonkwo.\n"
    backend = RecordingBackend()
    with pytest.raises(carenotes.CareNoteError):
        list(
            carenotes.refine_document(
                leaky, "A prior draft body.", "make the plan shorter", backend,
                phi_values=list(PHI_MAP.values()),
            )
        )
    assert backend.calls == 0


def test_assert_no_residual_identifiers_is_a_standalone_check():
    carenotes.assert_no_residual_identifiers("[PATIENT] was reviewed on the ward.")
    with pytest.raises(carenotes.CareNoteError):
        carenotes.assert_no_residual_identifiers("Ring 0161 496 0245 for the ward.")
    carenotes.assert_no_residual_identifiers(
        "Ring 0161 496 0245 for the ward.", acknowledged=["0161 496 0245"]
    )


def test_the_mapping_itself_is_never_a_parameter_to_the_backend():
    """`phi_values` exists to assert absence, never to be forwarded."""
    backend = RecordingBackend()
    list(
        carenotes.generate_document(
            DEIDENTIFIED, "SOAP care note", backend,
            phi_values=list(PHI_MAP.values()),
        )
    )
    for placeholder, value in PHI_MAP.items():
        assert f"{placeholder}: {value}" not in backend.prompt


# ==========================================================================
# Templates
# ==========================================================================

@pytest.mark.parametrize("template", list(carenotes.TEMPLATES))
def test_each_template_renders_a_well_formed_prompt(template):
    custom = "My house format:\n1. Summary\n2. Plan"
    prompt = carenotes.render_prompt(DEIDENTIFIED, template, custom)
    assert DEIDENTIFIED.strip() in prompt
    assert "{document}" not in prompt
    assert "{instruction}" not in prompt
    assert len(prompt) > len(DEIDENTIFIED)


def test_the_custom_template_carries_the_clinicians_own_format():
    custom = "SECTION A: background\nSECTION B: risk"
    prompt = carenotes.render_prompt(DEIDENTIFIED, carenotes.CUSTOM_TEMPLATE, custom)
    assert "SECTION A: background" in prompt
    assert "SECTION B: risk" in prompt


def test_the_custom_template_needs_instructions():
    with pytest.raises(carenotes.CareNoteError):
        carenotes.render_prompt(DEIDENTIFIED, carenotes.CUSTOM_TEMPLATE, "   ")


def test_an_unknown_template_is_refused():
    with pytest.raises(carenotes.CareNoteError):
        carenotes.render_prompt(DEIDENTIFIED, "Interpretive dance", "")


def test_the_system_prompt_carries_the_load_bearing_rules():
    system = carenotes.system_prompt()
    assert "[not documented]" in system
    assert "Do NOT invent" in system
    assert "EXACTLY as written" in system


# ==========================================================================
# Task 7 — anti-fabrication and the review banner
# ==========================================================================

def test_absent_fields_come_back_as_not_documented():
    """Spot-check the instruction is honoured, with the model mocked."""
    backend = RecordingBackend(
        "S - Subjective\n[PATIENT] reported low mood.\n"
        "O - Objective\n[not documented]\n"
        "A - Assessment\n[not documented]\n"
        "P - Plan\nReview in four weeks.\n"
    )
    draft = "".join(
        carenotes.generate_document(DEIDENTIFIED, "SOAP care note", backend)
    )
    assert draft.count("[not documented]") == 2
    assert "normal" not in draft.casefold()


def test_every_draft_carries_the_review_banner():
    assert carenotes.with_banner("Body").startswith("> **DRAFT")
    assert "requires clinician review" in carenotes.with_banner("Body")


def test_the_banner_is_not_duplicated_on_refinement():
    once = carenotes.with_banner("Body")
    assert carenotes.with_banner(once) == once


# ==========================================================================
# Task 4 — placeholder integrity
# ==========================================================================

MANGLED_DRAFT = """[PATIENT] was reviewed by [CLINICIAN_1].
The record number is [MATIENT_2] and the NHS number is [NHS_NO].
"""


def test_a_mangled_placeholder_is_detected():
    issues = mapping.check_placeholder_integrity(
        "[MATIENT_2] attended.", ["[PATIENT_2]", "[MRN]"]
    )
    mangled = [i for i in issues if i.kind == mapping.ISSUE_MANGLED]
    assert mangled
    assert mangled[0].token == "[MATIENT_2]"
    assert mangled[0].suggestion == "[PATIENT_2]"


def test_a_mangled_placeholder_is_repaired_during_reidentification():
    text, unresolved = mapping.reidentify_document(
        "[MATIENT_2] attended.", {"[PATIENT_2]": "Wei Chen"}
    )
    assert text == "Wei Chen attended."
    assert unresolved == []


def test_a_missing_placeholder_is_reported():
    issues = mapping.check_placeholder_integrity("[PATIENT] only.", ["[PATIENT]", "[MRN]"])
    missing = [i for i in issues if i.kind == mapping.ISSUE_MISSING]
    assert [i.token for i in missing] == ["[MRN]"]


def test_an_invented_placeholder_is_reported_as_unknown():
    issues = mapping.check_placeholder_integrity(
        "[CONSULTANT_ONCOLOGIST] said so.", ["[PATIENT]"]
    )
    assert any(i.kind == mapping.ISSUE_UNKNOWN for i in issues)


def test_an_ambiguous_mangle_is_not_guessed():
    """Between [MRN_1] and [MRN_2], refusing is the only safe answer."""
    issues = mapping.check_placeholder_integrity(
        "[MRN_3] was recorded.", ["[MRN_1]", "[MRN_2]"]
    )
    assert all(i.kind != mapping.ISSUE_MANGLED for i in issues)


# ==========================================================================
# Task 4 — re-identification and the release gate
# ==========================================================================

DRAFT = """> **DRAFT — requires clinician review.**

[PATIENT] was reviewed by [CLINICIAN_1]. [RELATIVE_1] attended.
NHS [NHS_NO], record [MRN], born [DATE_1].
"""


def test_every_placeholder_resolves_to_its_real_value():
    text, unresolved = mapping.reidentify_document(DRAFT, PHI_MAP)
    assert unresolved == []
    for value in PHI_MAP.values():
        assert value in text


def test_no_placeholder_survives_reidentification():
    text, _ = mapping.reidentify_document(DRAFT, PHI_MAP)
    assert mapping.PLACEHOLDER_RE.search(text) is None


def test_a_missing_mapping_entry_is_reported_and_blocks():
    incomplete = {k: v for k, v in PHI_MAP.items() if k != "[MRN]"}
    text, unresolved = mapping.reidentify_document(DRAFT, incomplete)
    assert "[MRN]" in unresolved
    # The caller blocks on a non-empty unresolved list; the token is still there
    # to be seen rather than silently dropped.
    assert "[MRN]" in text


def test_finalise_is_the_release_gate():
    text, unresolved = carenotes.finalise(DRAFT, PHI_MAP)
    assert unresolved == []
    assert mapping.PLACEHOLDER_RE.search(text) is None


def test_finalise_blocks_on_an_unresolvable_placeholder():
    _, unresolved = carenotes.finalise(DRAFT, {"[PATIENT]": "Wei Chen"})
    assert unresolved


# ==========================================================================
# Task 6 — refinement stays on de-identified text
# ==========================================================================

def test_refinement_sends_no_real_identifier():
    backend = RecordingBackend("Revised draft.")
    list(
        carenotes.refine_document(
            DEIDENTIFIED, DRAFT, "make the plan more concise", backend,
            phi_values=list(PHI_MAP.values()),
        )
    )
    for value in PHI_MAP.values():
        assert value not in backend.prompt


def test_refinement_carries_the_running_history():
    backend = RecordingBackend()
    list(
        carenotes.refine_document(
            DEIDENTIFIED, DRAFT, "add a risk paragraph", backend,
            history=[("keep the plan short", "")],
        )
    )
    assert "keep the plan short" in backend.prompt
    assert "add a risk paragraph" in backend.prompt


def test_refinement_needs_a_draft_and_an_instruction():
    backend = RecordingBackend()
    with pytest.raises(carenotes.CareNoteError):
        list(carenotes.refine_document(DEIDENTIFIED, "", "shorten it", backend))
    with pytest.raises(carenotes.CareNoteError):
        list(carenotes.refine_document(DEIDENTIFIED, DRAFT, "  ", backend))


# ==========================================================================
# Task 1 — the localhost pin
# ==========================================================================

def test_the_client_targets_loopback():
    assert ollama_client.OLLAMA_HOST == "127.0.0.1"
    assert ollama_client.BASE_URL == "http://127.0.0.1:11434"


def test_a_set_ollama_host_is_ignored(monkeypatch):
    """The documented way to point Ollama elsewhere must not work here."""
    monkeypatch.setenv("OLLAMA_HOST", "http://evil.example.com:11434")
    import importlib

    reloaded = importlib.reload(ollama_client)
    try:
        assert reloaded.OLLAMA_HOST == "127.0.0.1"
        assert "evil.example.com" not in reloaded.BASE_URL
    finally:
        monkeypatch.delenv("OLLAMA_HOST", raising=False)
        importlib.reload(ollama_client)


def test_the_source_never_reads_the_env_var():
    """Belt and braces: the string must not appear as an os.environ lookup."""
    from pathlib import Path

    source = Path(ollama_client.__file__).read_text(encoding="utf-8")
    assert "environ" not in source
    assert "getenv" not in source


def test_a_missing_model_names_the_pull_command():
    message = ollama_client.missing_model_message("llama3.1:8b", ["qwen2.5:7b"])
    assert "ollama pull llama3.1:8b" in message
    assert "qwen2.5:7b" in message


def test_the_daemon_down_message_says_how_to_start_it():
    assert "ollama serve" in ollama_client.DAEMON_DOWN_MESSAGE


def test_default_model_prefers_an_8b_instruct_model():
    assert ollama_client.default_model(["mistral:7b", "llama3.1:8b"]) == "llama3.1:8b"
    assert ollama_client.default_model(["tinyllama:1.1b"]) == "tinyllama:1.1b"
    assert ollama_client.default_model([]) is None


# ==========================================================================
# Task 5 — the approval gate
# ==========================================================================

def test_generation_is_unavailable_until_the_document_is_approved():
    from carescribe import app as carescribe_app
    from carescribe.core import batch

    document = batch.Document(
        name="note.txt", raw_text="x", redacted_text="[PATIENT] seen.", approved=False
    )
    assert not document.approved
    # The panel only ever receives approved documents.
    assert "approve the document first" in carescribe_app.carenotes.DISABLED_MESSAGE


def test_drafts_are_wiped_with_the_rest_of_the_session():
    from carescribe import app as carescribe_app

    assert "drafts" in carescribe_app.PHI_KEYS


def test_form_drafts_are_wiped_with_the_rest_of_the_session():
    from carescribe import app as carescribe_app

    # form_drafts holds the clinical-form equivalent of "drafts" — merged
    # identity maps, re-identified field values, and typed header values.
    # It must be wiped by the same "Wipe PHI" action, or it leaks past it.
    assert "form_drafts" in carescribe_app.PHI_KEYS


# ==========================================================================
# Task 8 — generate/refine overrides for the clinical-form pipeline
# ==========================================================================

def test_generate_document_accepts_a_system_and_user_prompt_override():
    backend = RecordingBackend()
    list(carenotes.generate_document(
        "irrelevant for this call",
        "SOAP care note",  # ignored — user_prompt short-circuits render_prompt
        backend,
        stream=False,
        user_prompt="MY CUSTOM PROMPT",
        system="MY CUSTOM SYSTEM",
    ))
    assert backend.system == "MY CUSTOM SYSTEM"
    assert backend.prompt == "MY CUSTOM PROMPT"


def test_generate_document_default_behaviour_is_unchanged():
    backend = RecordingBackend()
    list(carenotes.generate_document(
        "Patient: [PATIENT]\nSeen in clinic.", "SOAP care note", backend, stream=False,
    ))
    assert backend.system == carenotes.system_prompt()
    assert "Patient: [PATIENT]" in backend.prompt


def test_refine_document_accepts_a_system_and_refine_prompt_override():
    backend = RecordingBackend()
    list(carenotes.refine_document(
        "source", "draft with <<FIELD:x>> content", "make it shorter", backend,
        stream=False, system="MY CUSTOM SYSTEM", refine_prompt_name="refine_form.txt",
    ))
    assert backend.system == "MY CUSTOM SYSTEM"
    assert "<<FIELD:" in backend.prompt
    assert "make it shorter" in backend.prompt


def test_refine_document_default_behaviour_is_unchanged():
    backend = RecordingBackend()
    list(carenotes.refine_document(
        "source", "draft text", "make it shorter", backend, stream=False,
    ))
    assert backend.system == carenotes.system_prompt()
