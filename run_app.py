"""
CareScribe desktop launcher — the app's entry point.

Starts the Streamlit server headless on a free loopback port, waits for it to
answer, and shows it in a native desktop window. Not a browser tab: a clinician
double-clicks an icon and gets a window, with no address bar suggesting the
thing is on the internet and no console behind it.

The server is bound to 127.0.0.1 and given a port the OS picked as free, so two
copies of the app cannot collide and nothing is reachable from the network.
Closing the window shuts the server down.
"""

from __future__ import annotations

import atexit
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

if __package__ in (None, "") and str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from carescribe.core import desktop  # noqa: E402

WINDOW_TITLE = "CareScribe"
STARTUP_TIMEOUT_SECONDS = 180
POLL_INTERVAL = 0.25

_server: subprocess.Popen | None = None


def free_port() -> int:
    """A port the OS says is free, on loopback."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _no_window_kwargs() -> dict:
    """Keep a console from flashing up behind the window on Windows."""
    if sys.platform != "win32":
        return {}
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return {
        "startupinfo": startupinfo,
        "creationflags": subprocess.CREATE_NO_WINDOW,
    }


def server_command(port: int) -> list[str]:
    """The command that runs the Streamlit app, frozen or from source."""
    app_path = str(desktop.resource_path("carescribe", "app.py"))
    args = [
        "run", app_path,
        "--server.address=127.0.0.1",
        f"--server.port={port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--server.fileWatcherType=none",
        "--global.developmentMode=false",
    ]
    if desktop.is_frozen():
        # In a bundle there is no python.exe to call; re-invoke this executable
        # with a marker the __main__ guard below picks up.
        return [sys.executable, "--carescribe-server", *args]
    return [sys.executable, "-m", "streamlit", *args]


def start_server(port: int) -> subprocess.Popen:
    environment = dict(os.environ)
    environment["STREAMLIT_SERVER_ADDRESS"] = "127.0.0.1"
    environment["STREAMLIT_SERVER_HEADLESS"] = "true"
    environment["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    # Outputs belong in the per-user app-data directory, never beside the .exe.
    environment["CARESCRIBE_OUTPUT_DIR"] = str(desktop.output_dir())

    return subprocess.Popen(
        server_command(port),
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        **_no_window_kwargs(),
    )


def wait_until_up(port: int, timeout: float = STARTUP_TIMEOUT_SECONDS) -> bool:
    """Poll the loopback port until Streamlit answers."""
    url = f"http://127.0.0.1:{port}/_stcore/health"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if _server is not None and _server.poll() is not None:
            return False  # the server died on startup
        try:
            with urllib.request.urlopen(url, timeout=2) as response:  # noqa: S310
                if response.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            time.sleep(POLL_INTERVAL)
    return False


def close_splash() -> None:
    """Dismiss the bootloader splash, if this is a frozen build that has one.

    ``pyi_splash`` only exists inside a PyInstaller bundle built with a Splash,
    so every failure mode here — running from source, a build without a splash,
    a splash already gone — is expected and silent.
    """
    try:
        import pyi_splash  # type: ignore[import-not-found]

        pyi_splash.close()
    except Exception:  # noqa: BLE001
        pass


def stop_server() -> None:
    global _server
    if _server is None:
        return
    process, _server = _server, None
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=8)
    except subprocess.TimeoutExpired:
        process.kill()


def main() -> int:
    global _server

    desktop.ensure_dirs()
    port = free_port()
    _server = start_server(port)
    atexit.register(stop_server)

    if not wait_until_up(port):
        stop_server()
        close_splash()
        _fatal(
            "CareScribe could not start.\n\n"
            "If this keeps happening, reinstall the app."
        )
        return 1

    url = f"http://127.0.0.1:{port}"
    close_splash()

    try:
        import webview
    except ImportError:
        # No native window available — fall back to the default browser rather
        # than leaving the user with a running server and nothing to look at.
        import webbrowser

        webbrowser.open(url)
        try:
            while _server and _server.poll() is None:
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        stop_server()
        return 0

    window = webview.create_window(
        WINDOW_TITLE, url, width=1400, height=920, min_size=(1024, 700),
    )
    window.events.closed += lambda: threading.Thread(target=stop_server).start()

    webview.start()
    stop_server()
    return 0


def _fatal(message: str) -> None:
    """Report a startup failure without a console to print it to."""
    try:
        import webview

        webview.create_window(WINDOW_TITLE, html=f"<pre>{message}</pre>")
        webview.start()
        return
    except Exception:  # noqa: BLE001
        pass
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(0, message, WINDOW_TITLE, 0x10)
            return
        except Exception:  # noqa: BLE001
            pass
    print(message, file=sys.stderr)


if __name__ == "__main__":
    # In a frozen build the same executable serves as its own Python: this
    # marker means "you are the server child, run Streamlit".
    if "--carescribe-server" in sys.argv:
        sys.argv = [arg for arg in sys.argv if arg != "--carescribe-server"]
        from streamlit.web.cli import main as streamlit_main

        sys.exit(streamlit_main())
    sys.exit(main())
