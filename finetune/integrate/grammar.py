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

import re

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


def _gbnf_string_literal(text: str) -> str:
    """A GBNF double-quoted literal with the necessary escapes."""
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _placeholder_alt(known_placeholders: list[str]) -> str:
    """Alternation of the inner names of ``[NAME]`` tokens, e.g. ``"PATIENT" | "DATE_1"``."""
    names = []
    for token in known_placeholders:
        m = re.fullmatch(r"\[(.+)\]", token.strip())
        if m:
            names.append(_gbnf_string_literal(m.group(1)))
    return " | ".join(dict.fromkeys(names))  # dedupe, keep order


def build_grammar(form: FormType, known_placeholders: list[str]) -> str:
    """A GBNF grammar string for one form + this document's placeholder set."""
    headings = _FORM_HEADINGS.get(form)
    if headings is None:
        raise ValueError(f"no grammar for {form}")

    alt = _placeholder_alt(list(known_placeholders))
    lines = [
        "root ::= " + " nl ".join(f"section{i}" for i in range(len(headings))),
        "",
    ]
    for i, h in enumerate(headings):
        lines.append(
            f'section{i} ::= "**" {_gbnf_string_literal(h)} "**" nl body'
        )
    lines.append("")
    if alt:
        lines.append(f"body ::= chunk*")
        lines.append(f"chunk ::= safe+ | placeholder")
        lines.append(f"placeholder ::= \"[\" ( {alt} ) \"]\"")
        # any character except '[' (so a bare '[' is impossible outside a placeholder)
        lines.append(r'safe ::= [^[]')
    else:
        lines.append(r'body ::= [^[]*')  # no placeholders in this doc — forbid '[' entirely
    lines.append(r'nl ::= "\n"')
    return "\n".join(lines) + "\n"


def try_compile(grammar: str):
    """Compile with llama-cpp-python if available; return the object or None."""
    try:
        from llama_cpp import LlamaGrammar
    except Exception:  # noqa: BLE001
        return None
    return LlamaGrammar.from_string(grammar)


__all__ = ["build_grammar", "try_compile"]
