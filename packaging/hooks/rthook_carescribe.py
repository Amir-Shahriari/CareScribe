"""
PyInstaller runtime hook — runs before anything else in the frozen app.

Two jobs: make the bundled package importable, and make Streamlit behave in an
environment that has no console, no browser, and no writable install directory.
"""
import os
import sys

if hasattr(sys, "_MEIPASS"):
    meipass = sys._MEIPASS
    if meipass not in sys.path:
        sys.path.insert(0, meipass)

    # Loopback only, headless, no telemetry — set before Streamlit reads config
    # so a stray user-level config file cannot widen the binding.
    os.environ.setdefault("STREAMLIT_SERVER_ADDRESS", "127.0.0.1")
    os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
    os.environ.setdefault("STREAMLIT_SERVER_FILE_WATCHER_TYPE", "none")
    os.environ.setdefault("STREAMLIT_GLOBAL_DEVELOPMENT_MODE", "false")

    # A frozen app has no stdout/stderr when built windowed; Streamlit and
    # llama.cpp both write to them.
    for stream in ("stdout", "stderr"):
        if getattr(sys, stream, None) is None:
            setattr(sys, stream, open(os.devnull, "w"))
