"""
GBNF grammars for constrained decoding — the belt-and-braces guarantee on top
of the fine-tune.

For each built-in form the grammar pins the heading skeleton (exact text, exact
order) and constrains body text so that **every ``[`` opens a known
placeholder** — the model cannot emit ``[`` unless it is starting one of the
tokens from this document's identity map, and it must close it with ``]``. That
makes "invented a bracket token" and "dropped a required section" structurally
impossible, not merely discouraged.

`llama-cpp-python` accepts a GBNF string via ``LlamaGrammar.from_string``.
"""

from __future__ import annotations

from finetune.datagen.schema import FormType

_FORM_HEADINGS: dict[FormType, list[str]] = {
    FormType.SOAP: ["S — Subjective", "O — Objective", "A — Assessment", "P — Plan"],
    FormType.PROGRESS_NOTE: [
        "Interval History",
        "Current Status",
        "Response to Treatment",
        "Assessment",
        "Plan / Next Steps",
    ],
    FormType.CARE_PLAN: [
        "Problem List",
        "Interventions",
        "Safety & Risk Considerations",
        "Patient / Carer Education",
        "Follow-up",
    ],
    FormType.HANDOVER: ["Situation", "Background", "Assessment", "Recommendation"],
}


def build_grammar(form: FormType, known_placeholders: list[str]) -> str:
    """A GBNF grammar string for one form + this document's placeholder set.

    Delegates the GBNF construction to :mod:`carescribe.core.grammar` so the
    fine-tune and the shipping app use one grammar implementation.
    """
    headings = _FORM_HEADINGS.get(form)
    if headings is None:
        raise ValueError(f"no grammar for {form}")

    from carescribe.core.grammar import note_grammar

    gbnf = note_grammar(headings, list(known_placeholders))
    if gbnf is None:  # pragma: no cover - headings are always non-empty here
        raise ValueError(f"could not build a grammar for {form}")
    return gbnf


def try_compile(grammar: str):
    """Compile with llama-cpp-python if available; return the object or None."""
    from carescribe.core.grammar import compile_grammar

    return compile_grammar(grammar)


__all__ = ["build_grammar", "try_compile"]
