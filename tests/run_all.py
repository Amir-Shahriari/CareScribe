"""
Run the whole CareScribe suite.

    python tests/run_all.py

Equivalent to `pytest tests -q`, kept as a shortcut. Nothing here needs a
server, a GPU, or a network connection — the stage under test is entirely
local. The first run pays a few seconds to load the spaCy model; it is then
cached for the rest of the session.

This includes the stress corpus (``stress_corpus/`` checked against its
``answer_key.json``). For a per-document breakdown of what leaked or was
over-redacted rather than a pass count, run ``python tests/stress_report.py``.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.exit(
    subprocess.run(
        [sys.executable, "-W", "ignore", "-m", "pytest", "tests", "-q"], cwd=ROOT
    ).returncode
)
