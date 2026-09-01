"""
Post-build smoke check: does the frozen CareScribe binary actually start?

A PyInstaller freeze can succeed and still ship a binary that dies on launch —
a missing hidden import, a data file that did not travel, a hook that dropped a
submodule. This launches the built executable in its headless server mode (the
``--carescribe-server`` marker that ``run_app.py`` already handles), waits for
Streamlit's health endpoint to answer, and fails the build if it never does.

    python packaging/verify_frozen.py [dist/CareScribe | dist/CareScribe.app]

Stdlib only, so it runs on a clean CI runner before the app's own dependencies
are guaranteed importable outside the bundle. Does NOT require a GGUF — CI
builds set CARESCRIBE_BUNDLE_MODEL=0 and this check only asserts the server
comes up.

Exits 0 on success, non-zero on any failure.
"""

from __future__ import annotations

import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HEALTH_PATH = "/_stcore/health"
STARTUP_TIMEOUT_SECONDS = 150
POLL_INTERVAL = 1.0


def _default_dist() -> Path:
    root = Path(__file__).resolve().parent.parent
    if sys.platform == "darwin":
        return root / "dist" / "CareScribe.app"
    return root / "dist" / "CareScribe"


def find_executable(app_dir: Path) -> Path:
    """Locate the frozen entry-point inside a PyInstaller output directory."""
    if sys.platform == "darwin" and app_dir.suffix == ".app":
        exe = app_dir / "Contents" / "MacOS" / "CareScribe"
        if exe.is_file():
            return exe
    candidates = [
        app_dir / "CareScribe.exe",
        app_dir / "CareScribe",
        app_dir / "Contents" / "MacOS" / "CareScribe",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"no CareScribe executable under {app_dir}")


def bundled_app_py(app_dir: Path) -> Path:
    """The Streamlit script inside the bundle."""
    for base in (
        app_dir / "_internal" / "carescribe" / "app.py",          # onedir (win/linux)
        app_dir / "carescribe" / "app.py",
        app_dir / "Contents" / "Resources" / "carescribe" / "app.py",  # .app
        app_dir / "Contents" / "Frameworks" / "carescribe" / "app.py",
    ):
        if base.is_file():
            return base
    raise FileNotFoundError(f"no bundled carescribe/app.py under {app_dir}")


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def main(argv: list[str]) -> int:
    app_dir = Path(argv[1]).resolve() if len(argv) > 1 else _default_dist()
    if not app_dir.exists():
        print(f"FAIL  build output not found: {app_dir}")
        return 2

    try:
        exe = find_executable(app_dir)
        app_py = bundled_app_py(app_dir)
    except FileNotFoundError as exc:
        print(f"FAIL  {exc}")
        return 2

    port = free_port()
    cmd = [
        str(exe),
        "--carescribe-server",
        "run",
        str(app_py),
        "--server.address=127.0.0.1",
        f"--server.port={port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--global.developmentMode=false",
    ]
    print(f"      launching {exe.name} (port {port})")
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    url = f"http://127.0.0.1:{port}{HEALTH_PATH}"
    deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
    healthy = False
    try:
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                print(f"FAIL  process exited early (code {proc.returncode})")
                break
            try:
                with urllib.request.urlopen(url, timeout=2) as resp:  # noqa: S310
                    if resp.status == 200 and b"ok" in resp.read().lower():
                        healthy = True
                        break
            except (urllib.error.URLError, OSError):
                time.sleep(POLL_INTERVAL)
        else:
            print(f"FAIL  no healthy response within {STARTUP_TIMEOUT_SECONDS}s")
    finally:
        proc.terminate()
        try:
            out, _ = proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, _ = proc.communicate()

    if healthy:
        elapsed = STARTUP_TIMEOUT_SECONDS - (deadline - time.monotonic())
        print(f"PASS  frozen app served {HEALTH_PATH} in ~{elapsed:.0f}s")
        return 0

    tail = "\n".join((out or "").splitlines()[-25:])
    if tail:
        print("---- captured output ----")
        print(tail)
        print("-------------------------")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
