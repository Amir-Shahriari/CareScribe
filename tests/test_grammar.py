"""GBNF grammars for constrained local decoding."""

from __future__ import annotations

from carescribe.core import grammar


def test_field_grammar_requires_every_marker_in_order():
    g = grammar.field_grammar(
        ["reason", "clinical.diagnoses", "homework.compliance"],
        ["[PATIENT]", "[DATE_1]"],
    )
    assert g is not None
    assert '"<<FIELD:reason>>"' in g
    assert '"<<FIELD:clinical.diagnoses>>"' in g
    assert '"<<FIELD:homework.compliance>>"' in g
    # section order is fixed by the root rule
    assert "root ::= ws section0 nl section1 nl section2 ws" in g


def test_field_grammar_constrains_brackets_to_known_placeholders():
    g = grammar.field_grammar(["a", "b"], ["[PATIENT]", "[DOCA_NHS_NO]", "[PATIENT]"])
    assert 'placeholder ::= "[" ( "PATIENT" | "DOCA_NHS_NO" ) "]"' in g
    assert "piece ::= placeholder | safe" in g


def test_field_grammar_with_no_placeholders_still_forbids_bare_brackets():
    g = grammar.field_grammar(["a"], [])
    assert "placeholder ::=" not in g
    assert "[^[<]" in g  # a bare '[' cannot appear in the body


def test_field_grammar_rejects_unusable_keys():
    assert grammar.field_grammar([], []) is None
    assert grammar.field_grammar(["bad key!", "<<x>>"], []) is None


def test_note_grammar_pins_headings():
    g = grammar.note_grammar(["S — Subjective", "O — Objective"], ["[PATIENT]"])
    assert g is not None
    assert '"**S — Subjective**"' in g
    assert '"**O — Objective**"' in g


def test_compile_grammar_is_best_effort():
    # a real grammar compiles when llama-cpp-python is present, else returns None
    out = grammar.compile_grammar(grammar.field_grammar(["a"], ["[X]"]))
    try:
        import llama_cpp  # noqa: F401
    except Exception:
        assert out is None
    else:
        assert out is not None
    # empty / missing input returns None
    assert grammar.compile_grammar(None) is None
    assert grammar.compile_grammar("") is None
    # genuinely broken GBNF never raises out of compile_grammar
    grammar.compile_grammar("root ::= <<<unbalanced")  # no exception
