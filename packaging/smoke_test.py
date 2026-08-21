"""
Headless smoke test for the packaged app.

Runs a synthetic corpus document through load -> de-identify -> approve ->
local generation, with a guard that fails on any non-loopback socket. Checks the
things a build can break that unit tests cannot: that resources resolve, that a
real model loads, and that the app-data directory is writable.

    python packaging/smoke_test.py

Exits non-zero on failure, so a build script can gate on it.
"""
from __future__ import annotations

import socket
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from carescribe.core import backends, batch, carenotes, deidentify, desktop  # noqa: E402

ALLOWED = {"127.0.0.1", "::1", "localhost"}
_egress: list[str] = []
_real_connect = socket.socket.connect


def _guarded(self, address, *args, **kwargs):
    host = address[0] if isinstance(address, tuple) else str(address)
    if host not in ALLOWED:
        _egress.append(str(host))
    return _real_connect(self, address, *args, **kwargs)


def main() -> int:
    socket.socket.connect = _guarded
    failures: list[str] = []

    def check(label: str, ok: bool, detail: str = "") -> None:
        print(f"  {'PASS' if ok else 'FAIL'}  {label}{'  ' + detail if detail else ''}")
        if not ok:
            failures.append(label)

    print("\nCareScribe smoke test")
    print("=" * 62)

    print("\nResources")
    check("app source resolves", desktop.resource_path("carescribe", "app.py").is_file())
    check("streamlit config bundled", desktop.streamlit_config_path().is_file())
    model = desktop.find_local_model()
    check("generation model present", model is not None, str(model or "(will fetch)"))
    verdict = desktop.ram_verdict()
    check("enough RAM for the built-in model", verdict["ok"],
          f"{verdict['total_gb']:.0f} GB")

    print("\nApp data")
    desktop.ensure_dirs()
    check("output dir writable", desktop.output_dir().is_dir(), str(desktop.output_dir()))

    print("\nPipeline")
    source = ROOT / "stress_corpus" / "doc06_psych_clinic_letter.txt"
    documents, errors = batch.load_documents([str(source)])
    check("document loaded", not errors and source.name in documents)
    document = batch.analyze_document(documents[source.name])
    check("identifiers detected", len(document.entities) > 5, f"{len(document.entities)}")
    check("safety sweep clean", deidentify.residual_scan(document.redacted_text) == [])
    check("no real identifier in redacted text",
          not any(v in document.redacted_text for v in document.phi_map.values()))

    print("\nGeneration")
    try:
        kind, backend, label = backends.select_backend()
        check("a backend is available", True, label)
        started = time.monotonic()
        draft = "".join(
            carenotes.generate_document(
                document.redacted_text, "SOAP care note", backend, stream=True,
                phi_values=list(document.phi_map.values()),
            )
        )
        elapsed = time.monotonic() - started
        check("draft produced", len(draft) > 200, f"{len(draft)} chars in {elapsed:.0f}s")
        check("draft leaks no real identifier",
              not any(v.lower() in draft.lower() for v in document.phi_map.values()))
        check("draft kept its placeholders", "[PATIENT]" in draft)
        print("\n--- draft (de-identified) ---")
        print("\n".join(draft.strip().splitlines()[:14]))
        print("---")
    except backends.BackendError as exc:
        check("a backend is available", False, str(exc).splitlines()[0])

    print("\nEgress")
    check("no outbound network connection", not _egress, str(_egress))

    print("\n" + "=" * 62)
    if failures:
        print(f"FAILED: {len(failures)} check(s) — {', '.join(failures)}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
