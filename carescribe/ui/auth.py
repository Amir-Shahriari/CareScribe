"""The sign-in gate, and the account panel in the sidebar.

CareScribe now opens on a login screen. Everything past it is scoped to one
account: the patients you create, the roster you browse, the folders approved
documents are filed into.

Be honest about what this is. It is **workspace separation on a shared desktop
machine, not a security control** -- the patient roster is plaintext on disk and
another person at this computer can read every name in every account without
signing in. The UI strings below say so, deliberately, in the one place a user
might otherwise assume protection they do not have. Do not soften them.
"""

from __future__ import annotations

import streamlit as st

from carescribe.core import applog, patients, users

MIN_PASSWORD_LENGTH = users.MIN_PASSWORD_LENGTH
MAX_USERNAME_LENGTH = users.MAX_USERNAME_LENGTH


# --- pure validation, so the form can say what is wrong before submitting ---

def normalise_username(raw: str) -> str:
    """Collapse internal whitespace and strip the ends. Never raises."""
    return " ".join(str(raw or "").split())


def username_error(raw: str) -> str | None:
    """``None`` if the username is acceptable, else why not."""
    name = normalise_username(raw)
    if not name:
        return "Enter a username."
    if len(name) > MAX_USERNAME_LENGTH:
        return f"Username must be {MAX_USERNAME_LENGTH} characters or fewer."
    # Letters and digits from any script are fine -- a clinician named Zoe or
    # Li must be able to sign up -- plus the punctuation real names carry.
    for char in name:
        if not (char.isalnum() or char in " -_.'"):
            return "Username can only contain letters, numbers, spaces, and - _ . '"
    return None


def password_error(raw: str) -> str | None:
    """``None`` if the password is acceptable, else why not.

    Length is the only rule. Complexity rules push people towards passwords
    they have to write down, and this is not the boundary protecting the data.
    A password is never trimmed -- spaces are legitimate characters.
    """
    if not isinstance(raw, str) or raw == "":
        return "Enter a password."
    if len(raw) < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    return None


def password_confirmation_error(password: str, confirmation: str) -> str | None:
    """``None`` if the two match, else why not."""
    if not confirmation:
        return "Re-enter the password."
    if password != confirmation:
        return "Passwords do not match."
    return None


def signup_errors(username: str, password: str, confirmation: str) -> dict[str, str]:
    """Every problem at once. An empty dict means the form is submittable."""
    found: dict[str, str] = {}
    name_problem = username_error(username)
    if name_problem:
        found["username"] = name_problem
    password_problem = password_error(password)
    if password_problem:
        found["password"] = password_problem
    confirmation_problem = password_confirmation_error(password, confirmation)
    if confirmation_problem:
        found["confirmation"] = confirmation_problem
    return found


# --- session ---------------------------------------------------------------

def current_user_id() -> str:
    return st.session_state.get("user_id", "") or ""


def is_signed_in() -> bool:
    return bool(current_user_id())


def sign_in(user: users.User) -> None:
    """Put the account into session and scope the store to it."""
    st.session_state["user_id"] = user.id
    st.session_state["username"] = user.username
    patients.set_active_user(user.id)


def sign_out(wipe: "callable | None" = None) -> None:
    """Leave the account, and take every trace of the session's work with it.

    ``wipe`` is ``app.wipe_phi`` -- passed in rather than imported, because the
    PHI keys are the app's business and this module must not import it back.
    Signing out has to wipe: the documents in memory belong to whoever was
    signed in, and leaving them for the next person is exactly the leak
    accounts are meant to prevent.
    """
    if wipe is not None:
        wipe()
    st.session_state["user_id"] = ""
    st.session_state["username"] = ""
    st.session_state["patient_id"] = ""
    patients.set_active_user(None)


def apply_scope() -> None:
    """Re-assert the store scope for this rerun.

    ``patients`` keeps the active account in module state, and Streamlit runs
    the script fresh on every interaction, so this is called once at the top of
    ``main()`` before anything reads the roster.
    """
    patients.set_active_user(current_user_id() or None)


# --- screens ---------------------------------------------------------------

def _honesty_caption() -> None:
    st.caption(
        "Accounts keep each person's patients separate on this computer. "
        "They are not a security control: the records are stored unencrypted, "
        "and anyone with access to this machine's files can read them whether "
        "or not they sign in."
    )


def _render_sign_in_form() -> None:
    # Plain widgets rather than st.form. A form would give Enter-to-submit, but
    # it is a container, and a container that is open while the rest of the page
    # renders is a whole class of bug for two fields and a button. Everything
    # here reruns on change anyway.
    username = st.text_input("Username", key="sign_in_username")
    password = st.text_input("Password", type="password", key="sign_in_password")
    if not st.button("Sign in", key="sign_in_go", type="primary"):
        return
    user = users.authenticate(username, password)
    if user is None:
        # One message for both causes. Which of the two it was is not the
        # user's business to learn by probing.
        st.error("That username and password do not match an account.")
        return
    sign_in(user)
    st.rerun()


def _render_sign_up_form(first_account: bool) -> None:
    username = st.text_input("Choose a username", key="sign_up_username")
    password = st.text_input(
        "Choose a password", type="password", key="sign_up_password",
        help=f"At least {MIN_PASSWORD_LENGTH} characters.",
    )
    confirmation = st.text_input(
        "Re-enter the password", type="password", key="sign_up_confirm"
    )
    if not st.button("Create account", key="sign_up_go", type="primary"):
        return

    problems = signup_errors(username, password, confirmation)
    if problems:
        for message in problems.values():
            st.error(message)
        return
    if users.username_taken(username):
        st.error("That username is already taken.")
        return

    try:
        user = users.create_user(username, password)
    except users.UserError as exc:
        st.error(str(exc))
        return

    # The first account inherits whatever roster this machine already had, so
    # a clinician who has been using CareScribe does not lose their patients
    # the day accounts arrive.
    if first_account:
        try:
            moved = patients.migrate_unscoped_into(user.id)
        except patients.PatientError as exc:
            applog.warn("could not migrate the existing roster: %s", exc)
            moved = 0
        if moved:
            st.session_state["_migrated_count"] = moved

    sign_in(user)
    st.rerun()


def render_gate() -> bool:
    """Show the sign-in screen. ``True`` when the app may carry on.

    Called before anything else in ``main()``. When it returns ``False`` the
    caller must return immediately -- nothing behind the gate should render.
    """
    if is_signed_in():
        apply_scope()
        return True

    has_accounts = users.any_users()

    st.markdown("### Sign in to CareScribe")
    _honesty_caption()

    if not has_accounts:
        st.info(
            "No accounts on this computer yet. Create the first one to get "
            "started -- any patients already saved here will be moved into it."
        )
        _render_sign_up_form(first_account=True)
        return False

    sign_in_tab, sign_up_tab = st.tabs(["Sign in", "Create an account"])
    with sign_in_tab:
        _render_sign_in_form()
    with sign_up_tab:
        _render_sign_up_form(first_account=False)
    return False


def render_account_panel(wipe: "callable | None" = None) -> None:
    """Who is signed in, and the way out. Lives in the sidebar.

    Uses the explicit ``st.sidebar.*`` API rather than a bare ``st.*`` inside a
    ``with st.sidebar`` block, matching the rest of ``render_sidebar``. It also
    binds the widgets to the sidebar container directly instead of to whatever
    context the bare proxy happens to be in, which keeps this panel independent
    of anything the page rendered before it.
    """
    if not is_signed_in():
        return
    username = st.session_state.get("username", "") or "this account"
    st.sidebar.caption(f"Signed in as **{username}**")
    st.sidebar.caption("Signing out clears the documents loaded in this session.")
    if st.sidebar.button("Sign out", key="sign_out", use_container_width=True):
        sign_out(wipe)
        st.rerun()


__all__ = [
    "apply_scope",
    "current_user_id",
    "is_signed_in",
    "normalise_username",
    "password_confirmation_error",
    "password_error",
    "render_account_panel",
    "render_gate",
    "sign_in",
    "sign_out",
    "signup_errors",
    "username_error",
]
