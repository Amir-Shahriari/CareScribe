"""
GBNF grammars for constrained local decoding — a structural guarantee on top of
the model.

Two things the grammar makes impossible rather than merely unlikely:

* **A bracket token that is not a known placeholder.** ``[`` may only open one
  of this document's identity-map placeholders, and must be closed with ``]``.
  An 8B model that invents ``[PATIENT_3]`` breaks re-identification; the grammar
  removes the option.
* **A missing or renamed field marker.** For a clinical form, every
  ``<<FIELD:key>>`` marker the parser looks for is in the grammar, in order, so
  the model is offered them at exactly the right point.

Grammar is best-effort: :func:`compile_grammar` returns ``None`` when
``llama-cpp-python`` is absent or the GBNF fails to build, and generation then
proceeds unconstrained rather than failing. Only :class:`LocalGGUFBackend` uses
it — Ollama and cloud generation ignore the argument.
"""

from __future__ import annotations

import re

_PLACEHOLDER_INNER = re.compile(r"^\[(.+)\]$")
_KEY_OK = re.compile(r"^[a-z0-9_.]+$")


def _lit(text: str) -> str:
    """A GBNF double-quoted literal."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _placeholder_rule(known_placeholders) -> str | None:
    """``placeholder ::= "[" ( "PATIENT" | "DATE_1" | ... ) "]"`` or ``None``."""
    names = []
    for token in known_placeholders or []:
        m = _PLACEHOLDER_INNER.match(str(token).strip())
        if m:
            names.append(_lit(m.group(1)))
    names = list(dict.fromkeys(names))
    if not names:
        return None
    return 'placeholder ::= "[" ( ' + " | ".join(names) + ' ) "]"'


def _body_rules(has_placeholders: bool) -> list[str]:
    if has_placeholders:
        return [
            "body ::= piece*",
            "piece ::= placeholder | safe",
            # any char except '[' (reserved for a placeholder) and '<' (reserved
            # for the next field marker); a lone '<' followed by a non-'<' is
            # allowed so clinical prose like "BP < 120" still parses.
            r'safe ::= [^[<] | "<" [^<]',
        ]
    return [r"body ::= ( [^[<] | \"<\" [^<] )*"]


def field_grammar(field_keys, known_placeholders) -> str | None:
    """GBNF for a ``<<FIELD:key>>``-delimited clinical form.

    Requires every marker in ``field_keys`` order; free text between them may
    only bracket a known placeholder. Returns ``None`` if there are no usable
    field keys.
    """
    keys = [k for k in field_keys if _KEY_OK.match(str(k))]
    if not keys:
        return None
    ph = _placeholder_rule(known_placeholders)

    sections = " nl ".join(f"section{i}" for i in range(len(keys)))
    lines = [f"root ::= ws {sections} ws", ""]
    for i, key in enumerate(keys):
        lines.append(f'section{i} ::= {_lit(f"<<FIELD:{key}>>")} ws body')
    lines.append("")
    lines += _body_rules(ph is not None)
    if ph is not None:
        lines.append(ph)
    lines += [r'ws ::= [ \t\r\n]*', r'nl ::= [ \t\r\n]*']
    return "\n".join(lines) + "\n"


def note_grammar(headings, known_placeholders) -> str | None:
    """GBNF for a heading-delimited free-form note (SOAP, care plan, ...).

    Each heading appears as ``**Heading**`` in order; body text between headings
    may only bracket a known placeholder.
    """
    heads = [str(h).strip() for h in headings if str(h).strip()]
    if not heads:
        return None
    ph = _placeholder_rule(known_placeholders)
    sections = " nl ".join(f"section{i}" for i in range(len(heads)))
    lines = [f"root ::= ws {sections} ws", ""]
    for i, h in enumerate(heads):
        lines.append(f'section{i} ::= {_lit("**" + h + "**")} ws body')
    lines.append("")
    lines += _body_rules(ph is not None)
    if ph is not None:
        lines.append(ph)
    lines += [r'ws ::= [ \t\r\n]*', r'nl ::= [ \t\r\n]*']
    return "\n".join(lines) + "\n"


def compile_grammar(gbnf: str | None):
    """Compile a GBNF string with llama-cpp-python, or return ``None``.

    Never raises: a grammar bug must not stop generation.
    """
    if not gbnf:
        return None
    try:
        from llama_cpp import LlamaGrammar

        return LlamaGrammar.from_string(gbnf, verbose=False)
    except Exception:  # noqa: BLE001 — unconstrained generation is the fallback
        return None


__all__ = ["compile_grammar", "field_grammar", "note_grammar"]
