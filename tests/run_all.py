"""
Run the whole CareScribe suite.

    python tests/run_all.py

Neither suite needs Ollama running — the UI suite fakes the client, and the
logic suite exercises the regex/redaction path directly.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUITES = ["tests/test_logic.py", "tests/test_app.py"]

totals = []
failed = False

for suite in SUITES:
    print(f"\n{'=' * 60}\nRUNNING {suite}\n{'=' * 60}")
    proc = subprocess.run(
        [sys.executable, str(ROOT / suite)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    print(proc.stdout)
    if proc.returncode != 0:
        failed = True
        print(proc.stderr[-2000:], file=sys.stderr)

    summary = [ln for ln in (proc.stdout or "").splitlines() if "passed," in ln]
    totals.append(f"{suite}: {summary[-1] if summary else 'no summary'}")

print("\n" + "=" * 60)
for line in totals:
    print(line)
print("=" * 60)
sys.exit(1 if failed else 0)
