"""
The one outbound request CareScribe makes — fetching the model, on request.

This module is deliberately the *only* place in the app that opens a connection
to anything other than loopback, and nothing in the de-identify → review →
approve → generate path imports it. That is what keeps the "no egress" claim
true and testable: the claim is not "this app never uses the network", it is
"patient data never leaves, and the only thing that ever comes in is model
weights the user asked for".

Worth being precise about the direction, because the two get conflated:

* **Downloading a model** moves weights *onto* the computer. No document, no
  identifier, no prompt is sent — the request is a plain HTTP GET for a file.
* **Generating** runs that model locally and opens no socket at all.

Nothing here runs on launch. Every entry point is called from an explicit click.
"""

from __future__ import annotations

import shutil
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator

from . import desktop, ollama_client

# Enough of the file to be confident it is not a truncated download or an error
# page. The real guard is the size check plus llama.cpp refusing to load junk.
GGUF_MAGIC = b"GGUF"
MIN_PLAUSIBLE_BYTES = 100_000_000
CHUNK = 1024 * 256
USER_AGENT = "CareScribe/1.0 (local desktop app)"


class ModelSetupError(RuntimeError):
    """Raised when provisioning fails, with something the user can act on."""


@dataclass
class Progress:
    """One step of a download, for a progress bar."""

    downloaded: int
    total: int
    message: str = ""

    @property
    def fraction(self) -> float:
        if self.total <= 0:
            return 0.0
        return min(1.0, self.downloaded / self.total)


def model_destination(filename: str | None = None) -> Path:
    """Where a downloaded model is written — the per-user app-data dir."""
    return desktop.models_dir() / (filename or desktop.DEFAULT_MODEL_FILENAME)


def is_model_present(filename: str | None = None) -> bool:
    """True if a usable model file is already on this computer.

    This is the marker that makes setup one-time: the file being there *is* the
    persisted state, so there is no separate flag to get out of step with it.
    """
    return desktop.find_local_model(filename or desktop.DEFAULT_MODEL_FILENAME) is not None


def _free_bytes(path: Path) -> int:
    try:
        return shutil.disk_usage(path).free
    except Exception:  # noqa: BLE001
        return 0


def _verify(path: Path, expected: int) -> None:
    """Refuse a file that is truncated or is not actually a model."""
    if not path.is_file():
        raise ModelSetupError("The download did not produce a file.")
    size = path.stat().st_size
    if size < MIN_PLAUSIBLE_BYTES or (expected and size < expected * 0.98):
        raise ModelSetupError(
            f"The download stopped early ({size / 1e9:.2f} GB of "
            f"{expected / 1e9:.2f} GB). Check the connection and try again — "
            "it will resume from where it stopped."
        )
    with path.open("rb") as handle:
        if handle.read(4) != GGUF_MAGIC:
            raise ModelSetupError(
                "The downloaded file is not a valid model. This usually means a "
                "network login page was returned instead. Delete it and retry."
            )


def download_model(
    url: str | None = None,
    filename: str | None = None,
    on_progress: Callable[[Progress], None] | None = None,
) -> Path:
    """Fetch the built-in model to the app-data dir. User-initiated only.

    Resumes a partial download with an HTTP Range request, so a dropped
    connection costs the user the remainder rather than the whole 2 GB.
    """
    url = url or desktop.MODEL_DOWNLOAD_URL
    destination = model_destination(filename)
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")

    already = partial.stat().st_size if partial.is_file() else 0
    expected = desktop.MODEL_APPROX_BYTES

    free = _free_bytes(destination.parent)
    if free and free < (expected - already) * 1.1:
        raise ModelSetupError(
            f"Not enough disk space. About {expected / 1e9:.1f} GB is needed and "
            f"{free / 1e9:.1f} GB is free. Free some space and try again."
        )

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    if already:
        request.add_header("Range", f"bytes={already}-")

    try:
        response = urllib.request.urlopen(request, timeout=60)  # noqa: S310
    except urllib.error.HTTPError as exc:
        if exc.code == 416:  # the range is already complete
            already, response = 0, None
            partial.unlink(missing_ok=True)
            response = urllib.request.urlopen(  # noqa: S310
                urllib.request.Request(url, headers={"User-Agent": USER_AGENT}),
                timeout=60,
            )
        else:
            raise ModelSetupError(
                f"The download was refused by the server (HTTP {exc.code}). "
                "If you are on a clinic network it may be blocked — try a "
                "different connection, or set up Ollama instead."
            ) from exc
    except urllib.error.URLError as exc:
        raise ModelSetupError(
            "Could not reach the download server. Check that this computer is "
            f"online and not behind a blocking proxy.\n\nDetail: {exc.reason}"
        ) from exc

    with response:
        declared = int(response.headers.get("Content-Length") or 0)
        total = (declared + already) if declared else expected
        downloaded = already
        mode = "ab" if already and response.status == 206 else "wb"
        if mode == "wb":
            downloaded = 0

        if on_progress:
            on_progress(Progress(downloaded, total, "Starting…"))

        try:
            with partial.open(mode) as handle:
                while True:
                    block = response.read(CHUNK)
                    if not block:
                        break
                    handle.write(block)
                    downloaded += len(block)
                    if on_progress:
                        on_progress(
                            Progress(
                                downloaded, total,
                                f"{downloaded / 1e9:.2f} of {total / 1e9:.2f} GB",
                            )
                        )
        except OSError as exc:
            raise ModelSetupError(
                f"Writing the model to disk failed: {exc}. This is usually a "
                "full disk."
            ) from exc

    _verify(partial, total)
    partial.replace(destination)
    if on_progress:
        on_progress(Progress(destination.stat().st_size, total, "Done"))
    return destination


def clear_partial_download(filename: str | None = None) -> None:
    """Throw away a partial file so the next attempt starts clean."""
    destination = model_destination(filename)
    destination.with_suffix(destination.suffix + ".part").unlink(missing_ok=True)


def pull_ollama_model(model: str = "llama3.1:8b") -> Iterator[Progress]:
    """Ask the local Ollama daemon to pull a model, yielding progress.

    The request goes to loopback; Ollama does the fetching. Still a download in
    the same sense as :func:`download_model` — weights coming in, nothing going
    out — so it belongs in this module rather than the client.
    """
    import json

    if not ollama_client.is_up():
        raise ModelSetupError(ollama_client.DAEMON_DOWN_MESSAGE)

    payload = json.dumps({"model": model, "stream": True}).encode("utf-8")
    request = urllib.request.Request(
        f"{ollama_client.BASE_URL}/api/pull",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        response = urllib.request.urlopen(request, timeout=None)  # noqa: S310
    except urllib.error.URLError as exc:
        raise ModelSetupError(f"Ollama refused the download: {exc}") from exc

    with response:
        for line in response:
            line = line.decode("utf-8").strip()
            if not line:
                continue
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError:
                continue
            if chunk.get("error"):
                raise ModelSetupError(str(chunk["error"]))
            completed = int(chunk.get("completed") or 0)
            total = int(chunk.get("total") or 0)
            yield Progress(completed, total, str(chunk.get("status") or ""))


OLLAMA_INSTALL_URL = "https://ollama.com/download"

OLLAMA_STEPS = (
    "1. Open ollama.com/download and install Ollama for Windows.",
    "2. Launch it once — it runs quietly in the background.",
    "3. Come back here and click Refresh.",
)


__all__ = [
    "OLLAMA_INSTALL_URL",
    "OLLAMA_STEPS",
    "ModelSetupError",
    "Progress",
    "clear_partial_download",
    "download_model",
    "is_model_present",
    "model_destination",
    "pull_ollama_model",
]
