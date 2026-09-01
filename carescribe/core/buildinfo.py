"""Build information for CareScribe."""

from carescribe import __version__

APP_NAME: str = "CareScribe"


def build_info() -> dict:
    """Return application identity and version."""
    return {"name": APP_NAME, "version": __version__}