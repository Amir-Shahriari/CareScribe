"""
Edge cases for carescribe.core.applog — the packaged app's only evidence trail.

The module carries a stated promise: no PHI is ever logged, and an unwritable
log directory must not stop the app. Neither was tested. Everything here is
fabricated.
"""

import logging
import logging.handlers

import pytest

from carescribe.core import applog


@pytest.fixture(autouse=True)
def isolated_logger(monkeypatch, tmp_path):
    """Keep the process-wide 'carescribe' logger out of the rest of the suite.

    get_logger() configures a module-level flag and attaches a file handler to a
    shared logger, so without saving and restoring both, one test here would
    leave a handler writing into another test's temp directory. propagate is
    saved too: get_logger() flips it to False, and once it is False pytest's
    logging plugin starts attaching its own capture handlers directly to this
    logger at every phase boundary, which would both leak capture state into
    these tests and hide the leak from the rest of the suite.
    """
    logger = logging.getLogger(applog.LOGGER_NAME)
    saved_handlers, saved_level = logger.handlers[:], logger.level
    saved_propagate = logger.propagate
    logger.handlers = []
    monkeypatch.setattr(applog, "_configured", False)
    monkeypatch.setattr(applog.desktop, "app_data_dir", lambda: tmp_path)
    yield logger
    for handler in logger.handlers:
        handler.close()
    logger.handlers, logger.level = saved_handlers, saved_level
    logger.propagate = saved_propagate


def _log_text() -> str:
    for handler in logging.getLogger(applog.LOGGER_NAME).handlers:
        handler.flush()
    return applog.log_path().read_text(encoding="utf-8")


def test_log_path_lives_in_logs_under_app_data_dir(isolated_logger, tmp_path):
    path = applog.log_path()
    assert path == tmp_path / "logs" / "carescribe.log"
    assert path.parent.name == "logs"
    assert path.name == "carescribe.log"


def test_get_logger_configures_once_and_does_not_stack_handlers(isolated_logger):
    first = applog.get_logger()
    second = applog.get_logger()
    assert first is second
    assert first is logging.getLogger(applog.LOGGER_NAME)
    assert len(first.handlers) == 1


def test_handler_is_rotating_bounded_and_does_not_propagate(isolated_logger):
    applog.get_logger()
    assert len(isolated_logger.handlers) == 1
    handler = isolated_logger.handlers[0]
    assert isinstance(handler, logging.handlers.RotatingFileHandler)
    assert handler.maxBytes == applog.MAX_BYTES
    assert handler.backupCount == applog.BACKUPS
    assert isolated_logger.propagate is False
    assert applog.log_path().exists()


def test_unwritable_log_directory_does_not_stop_the_app(isolated_logger, monkeypatch):
    def boom(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(applog.logging.handlers, "RotatingFileHandler", boom)
    logger = applog.get_logger()
    assert logger is logging.getLogger(applog.LOGGER_NAME)
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.NullHandler)
    applog.log("hi")
    applog.warn("still alive")


def test_log_writes_at_info_level():
    applog.log("hello %s", "world")
    text = _log_text()
    line = [ln for ln in text.splitlines() if "hello world" in ln][0]
    assert "INFO" in line


def test_warn_writes_at_warning_level():
    applog.warn("careful %s", "now")
    text = _log_text()
    line = [ln for ln in text.splitlines() if "careful now" in ln][0]
    assert "WARNING" in line


def test_exception_writes_traceback_at_error_level():
    try:
        raise ValueError("disk on fire")
    except ValueError:
        applog.exception("handler blew up")
    text = _log_text()
    line = [ln for ln in text.splitlines() if "handler blew up" in ln][0]
    assert "ERROR" in line
    assert "Traceback" in text
    assert "ValueError: disk on fire" in text


def test_timed_success_logs_start_and_done_with_fields():
    with applog.timed("ingest", pages=12, bytes=3400):
        pass
    text = _log_text()
    start_lines = [ln for ln in text.splitlines() if "ingest: start" in ln]
    done_lines = [ln for ln in text.splitlines() if "ingest: done in" in ln]
    assert len(start_lines) == 1
    assert len(done_lines) == 1
    assert "pages=12" in start_lines[0]
    assert "bytes=3400" in start_lines[0]
    assert "pages=12" in done_lines[0]
    assert "bytes=3400" in done_lines[0]


def test_timed_failure_logs_failed_and_reraises_original_exception():
    with pytest.raises(RuntimeError, match="kaboom"):
        with applog.timed("render", rows=3):
            raise RuntimeError("kaboom")
    text = _log_text()
    failed_lines = [ln for ln in text.splitlines() if "render: FAILED after" in ln]
    assert len(failed_lines) == 1
    assert "rows=3" in failed_lines[0]
    assert "Traceback" in text
    assert "RuntimeError: kaboom" in text
    assert "render: done in" not in text


def test_timed_without_fields_logs_cleanly():
    with applog.timed("quiet"):
        pass
    text = _log_text()
    assert "quiet: start" in text
    assert "quiet: done in" in text
    assert "%" not in text


def test_no_phi_is_ever_logged_lengths_and_counts_only():
    document = "Patient ZZTESTPATIENT-99999 " + "x" * 500
    applog.log("deidentify: %s chars", len(document))
    with applog.timed("deidentify", chars=len(document)):
        pass
    text = _log_text()
    assert "ZZTESTPATIENT-99999" not in text
    assert "ZZTESTPATIENT" not in text
    assert str(len(document)) in text
