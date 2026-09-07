"""Form validation for the sign-in and sign-up screens.

Pure functions: no Streamlit session, no account store. They exist so a form
can say what is wrong before it is submitted, in one consistent voice.
"""

from __future__ import annotations

import pytest

from carescribe.ui import auth


# --- normalise_username ----------------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("  Ann Smith ", "Ann Smith"),
    ("Ann   Smith", "Ann Smith"),
    ("Ann\tSmith", "Ann Smith"),
    ("", ""),
    ("   ", ""),
])
def test_normalise_username(raw, expected):
    assert auth.normalise_username(raw) == expected


# --- username_error --------------------------------------------------------

@pytest.mark.parametrize("name", [
    "ann", "Ann Smith", "o'brien", "jean-luc", "dr.who", "user_1", "Zoe", "Zoë", "李",
])
def test_acceptable_usernames(name):
    assert auth.username_error(name) is None


@pytest.mark.parametrize("name", ["", "   ", "a/b", "a\\b", "<script>", "ann@example"])
def test_rejected_usernames(name):
    assert auth.username_error(name) is not None


def test_username_length_boundary():
    assert auth.username_error("a" * auth.MAX_USERNAME_LENGTH) is None
    assert auth.username_error("a" * (auth.MAX_USERNAME_LENGTH + 1)) is not None


def test_username_length_is_measured_after_normalising():
    padded = "  " + ("a" * auth.MAX_USERNAME_LENGTH) + "  "
    assert auth.username_error(padded) is None


# --- password_error --------------------------------------------------------

def test_password_length_boundary():
    assert auth.password_error("a" * auth.MIN_PASSWORD_LENGTH) is None
    assert auth.password_error("a" * (auth.MIN_PASSWORD_LENGTH - 1)) is not None


def test_empty_password_is_rejected():
    assert auth.password_error("") is not None


def test_a_password_is_never_trimmed():
    """Leading and trailing spaces are legitimate password characters."""
    assert auth.password_error("  pass  ") is None      # 8 characters
    assert auth.password_error(" " * auth.MIN_PASSWORD_LENGTH) is None


def test_no_complexity_rules():
    assert auth.password_error("aaaaaaaa") is None


# --- confirmation ----------------------------------------------------------

def test_confirmation_must_be_present_and_match():
    assert auth.password_confirmation_error("correct horse", "") is not None
    assert auth.password_confirmation_error("correct horse", "other") is not None
    assert auth.password_confirmation_error("correct horse", "correct horse") is None


# --- signup_errors ---------------------------------------------------------

def test_a_valid_trio_has_no_problems():
    assert auth.signup_errors("ann", "correct horse", "correct horse") == {}


def test_an_all_invalid_trio_reports_every_field():
    problems = auth.signup_errors("", "short", "")
    assert set(problems) == {"username", "password", "confirmation"}


def test_fields_that_are_fine_are_absent_not_none():
    problems = auth.signup_errors("ann", "short", "short")
    assert "username" not in problems
    assert problems["password"]


def test_every_message_is_a_sentence():
    problems = auth.signup_errors("a/b", "short", "mismatch")
    for message in problems.values():
        assert message.endswith((".", "'"))
        assert message[0].isupper()
