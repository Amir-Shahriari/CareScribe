"""
Per-document pass/fail report for the stress corpus.

    python tests/stress_report.py

The pytest suite in ``test_stress_corpus.py`` is the CI gate — one test per
string, so a failure names the leak. This is the human-readable view: which
document, how many identifiers checked, and exactly what leaked or was
over-redacted. Exits non-zero if anything failed, so it can gate a build too.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from carescribe.core import deidentify  # noqa: E402

CORPUS = ROOT / "stress_corpus"
ANSWER_KEY = CORPUS / "answer_key.json"


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def main() -> int:
    if not ANSWER_KEY.exists():
        print(f"No answer key at {ANSWER_KEY}")
        return 2

    documents = json.loads(ANSWER_KEY.read_text(encoding="utf-8"))["documents"]

    total_leaks = 0
    total_over = 0
    total_checked = 0
    failed_documents = 0

    print()
    print("CareScribe stress corpus")
    print("=" * 72)

    for document in documents:
        path = CORPUS / document["file"]
        redacted = normalise(deidentify.deidentify(path.read_text(encoding="utf-8")).redacted_text)

        leaks = [v for v in document["must_redact"] if normalise(v) in redacted]
        over = [v for v in document["must_preserve"] if normalise(v) not in redacted]
        checked = len(document["must_redact"]) + len(document["must_preserve"])

        findings = deidentify.residual_scan(
            deidentify.deidentify(path.read_text(encoding="utf-8")).redacted_text
        )
        structured = [f for f in findings if re.search(r"\d{4}", f) or "@" in f]

        ok = not leaks and not over and not structured
        status = "PASS" if ok else "FAIL"
        if not ok:
            failed_documents += 1

        total_leaks += len(leaks)
        total_over += len(over)
        total_checked += checked

        print(f"\n{status}  {document['file']}")
        print(f"      {checked} assertions "
              f"({len(document['must_redact'])} must-redact, "
              f"{len(document['must_preserve'])} must-preserve)")
        print(f"      covers: {', '.join(document.get('covers', []))}")
        for value in leaks:
            print(f"      LEAK          {value!r} still present")
        for value in over:
            print(f"      OVER-REDACTED {value!r} was removed")
        for value in structured:
            print(f"      SWEEP         structured identifier survived: {value!r}")
        if findings and not structured:
            print(f"      note: sweep flagged {findings} "
                  f"(place names — reviewer dismisses these)")

    print()
    print("=" * 72)
    print(f"{len(documents) - failed_documents}/{len(documents)} documents passed · "
          f"{total_checked} assertions · "
          f"{total_leaks} leaks · {total_over} over-redactions")
    print()
    return 1 if failed_documents else 0


if __name__ == "__main__":
    raise SystemExit(main())
