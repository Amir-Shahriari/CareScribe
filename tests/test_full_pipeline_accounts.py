"""The whole pipeline, end to end, through accounts.

``tests/test_patient_pipeline.py`` drives ingest -> de-identify -> review ->
approve for all fifteen sample documents under one patient, with no accounts in
the picture. This does the same work through the layer added on top: two
clinicians with their own sign-ins, each filing real documents under their own
patients, and then the app itself is rendered to prove the frontend shows each
account what it should and nothing it should not.

Two bars have to be cleared at once, and both are asserted against real output:

* **The de-identification guarantee still holds.** Adding accounts moved every
  patient folder one level deeper. Nothing identifying beyond the roster
  display name and the username may reach disk -- not a document's contents,
  not a placeholder-to-value mapping, not a residual identifier.
* **Accounts separate what they claim to separate.** One account's roster,
  filed documents, and browser view must not surface in another's, at the store
  level or on screen.

Everything here is fabricated -- the sample documents are synthetic and
describe one fictional patient.
"""

from __future__ import annotations

import json
import warnings
from dataclasses import dataclass, field
from pathlib import Path

warnings.filterwarnings("ignore")

import pytest  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

from carescribe.core import batch, deidentify, ingest, patients, users  # noqa: E402

APP = str(Path(__file__).resolve().parent.parent / "carescribe" / "app.py")
SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_documents"
DOCX_FILES = sorted(SAMPLE_DIR.glob("*.docx"))

# Enough documents to exercise letters, a numeric result table and a form,
# without paying for all fifteen twice over -- the full sweep is
# test_patient_pipeline.py's job.
PIPELINE_DOCS = DOCX_FILES[:4]

# The fictional patient's hard identifiers. None may appear anywhere under
# either store after filing.
KNOWN_IDENTIFIERS = (
    "Jordan Elliot Whitfield", "Whitfield", "12/04/1985",
    "2934 5671 0",
)

# Usernames chosen to be findable in a path if the store ever put them there.
ALICE_USERNAME = "alice.clinician"
BLAKE_USERNAME = "blake.clinician"
PASSWORD = "correct horse battery"


@dataclass
class Filed:
    workdir: Path
    users_root: Path
    patients_root: Path
    alice: users.User
    blake: users.User
    alice_patient: patients.Patient
    blake_patient: patients.Patient
    redacted_by_doc: dict[str, str] = field(default_factory=dict)
    phi_by_doc: dict[str, dict[str, str]] = field(default_factory=dict)


def _approve_document(path: Path, patient_id: str) -> tuple[str, dict]:
    """ingest -> de-identify -> safety sweep -> file all three artefacts.

    The same sequence the approve button drives, so a failure here is a real
    regression rather than a document the pipeline could never file.
    """
    name = path.name
    raw = ingest.extract_text(str(path))
    assert raw.strip(), f"{name}: ingest produced nothing"

    result = deidentify.deidentify(raw)
    redacted = result.redacted_text
    assert redacted.strip(), f"{name}: de-identification produced nothing"
    assert deidentify.residual_scan(redacted) == [], name

    out = patients.patient_output_dir(patient_id)
    batch.write_approved(name, redacted, output_dir=out)
    batch.write_approved_docx(
        name, path.read_bytes(),
        batch.approved_map(result.entities, result.known_as),
        output_dir=out,
    )
    batch.write_review_record(
        name, entities=result.entities, flags_shown=0, flags_redacted=0,
        flags_dismissed=0, attested=True, output_dir=out,
    )
    return redacted, dict(result.phi_map)


@pytest.fixture(scope="module")
def filed() -> Filed:
    """Two accounts sign up, each files documents under their own patient."""
    import shutil
    import tempfile

    mp = pytest.MonkeyPatch()
    workdir = Path(tempfile.mkdtemp(prefix="carescribe-accounts-"))
    users_root = workdir / "users"
    patients_root = workdir / "patients"
    mp.setenv("CARESCRIBE_USERS_DIR", str(users_root))
    mp.setenv("CARESCRIBE_PATIENTS_DIR", str(patients_root))
    patients.set_active_user(None)
    try:
        alice = users.create_user(ALICE_USERNAME, PASSWORD)
        blake = users.create_user(BLAKE_USERNAME, PASSWORD)

        patients.set_active_user(alice.id)
        alice_patient = patients.create_patient("Jordan Whitfield")
        case = Filed(
            workdir=workdir, users_root=users_root, patients_root=patients_root,
            alice=alice, blake=blake,
            alice_patient=alice_patient, blake_patient=None,  # set below
        )
        for path in PIPELINE_DOCS:
            redacted, phi_map = _approve_document(path, alice_patient.id)
            case.redacted_by_doc[path.name] = redacted
            case.phi_by_doc[path.name] = phi_map

        patients.set_active_user(blake.id)
        blake_patient = patients.create_patient("Dana Okoro")
        _approve_document(DOCX_FILES[0], blake_patient.id)
        case.blake_patient = blake_patient

        patients.set_active_user(None)
        yield case
    finally:
        patients.set_active_user(None)
        mp.undo()
        shutil.rmtree(workdir, ignore_errors=True)


def _every_file(root: Path) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file()]


def run_app(**session) -> AppTest:
    app = AppTest.from_file(APP, default_timeout=120)
    for key, value in session.items():
        app.session_state[key] = value
    app.run()
    assert not app.exception, [e.value for e in app.exception]
    return app


def screen_text(app: AppTest) -> str:
    parts = [m.value for m in app.markdown]
    parts += [c.value for c in app.caption]
    parts += [e.value for e in app.error]
    parts += [i.value for i in app.info]
    return " ".join(str(p) for p in parts)


# --------------------------------------------------------------------------
# The pipeline still files what it should
# --------------------------------------------------------------------------

def test_every_document_is_filed_as_three_artefacts(filed: Filed):
    patients.set_active_user(filed.alice.id)
    docs = patients.filed_documents(filed.alice_patient.id)
    assert len(docs) == len(PIPELINE_DOCS) * 3
    assert {d.kind for d in docs} == {"text", "word", "audit"}


def test_filed_documents_come_back_newest_first(filed: Filed):
    patients.set_active_user(filed.alice.id)
    stamps = [d.modified_at for d in patients.filed_documents(filed.alice_patient.id)]
    assert stamps == sorted(stamps, reverse=True)


def test_each_redacted_text_is_free_of_known_identifiers(filed: Filed):
    for name, redacted in filed.redacted_by_doc.items():
        for identifier in KNOWN_IDENTIFIERS:
            assert identifier not in redacted, f"{name} leaked {identifier!r}"


def test_the_residual_sweep_over_the_whole_store_is_clean(filed: Filed):
    for path in _every_file(filed.patients_root):
        if path.suffix != ".txt":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        assert deidentify.residual_scan(text) == [], path.name


# --------------------------------------------------------------------------
# The guarantee, now that the store is one level deeper
# --------------------------------------------------------------------------

def test_no_known_identifier_reaches_either_store(filed: Filed):
    """Every file except the two rosters is free of the patient's identifiers.

    The rosters are the documented exception: ``patient.json`` holds the display
    name a clinician typed ("Jordan Whitfield", which contains the surname), and
    ``user.json`` holds the username. Those two are excluded here and pinned
    precisely by the next test instead.
    """
    exceptions = {patients.ROSTER_FILENAME, users.RECORD_FILENAME}
    for root in (filed.patients_root, filed.users_root):
        for path in _every_file(root):
            if path.name in exceptions:
                continue
            blob = path.read_bytes()
            for identifier in KNOWN_IDENTIFIERS:
                assert identifier.encode("utf-8") not in blob, f"{path} leaked {identifier!r}"


def test_the_roster_carries_the_display_name_and_nothing_more(filed: Filed):
    """The carve-out is exactly one field wide.

    A roster entry may hold the name the clinician typed. It may not hold the
    patient's full legal name from the document, their date of birth, or their
    Medicare number -- those are identifiers the pipeline redacts, and a roster
    that quietly accumulated them would widen the guarantee without anyone
    deciding to.
    """
    for path in filed.patients_root.rglob(patients.ROSTER_FILENAME):
        record = json.loads(path.read_text(encoding="utf-8"))
        assert set(record) == {"id", "display_name", "created_at", "updated_at"}
        blob = json.dumps(record)
        for identifier in ("Jordan Elliot Whitfield", "12/04/1985", "2934 5671 0"):
            assert identifier not in blob, f"{path} carries {identifier!r}"


def test_no_mapping_value_reaches_the_filed_artefacts(filed: Filed):
    """The placeholder-to-value map is in memory only. Prove it never landed."""
    patients.set_active_user(filed.alice.id)
    out_dir = patients.patient_output_dir(filed.alice_patient.id)
    for name, phi_map in filed.phi_by_doc.items():
        stem = Path(name).stem
        for value in phi_map.values():
            if not isinstance(value, str) or len(value.strip()) < 4:
                continue
            for artefact in out_dir.glob(f"{stem}.*"):
                blob = artefact.read_bytes()
                assert value.encode("utf-8") not in blob, (
                    f"{artefact.name} carries the real value {value!r}"
                )


def test_no_path_anywhere_contains_a_name_or_a_username(filed: Filed):
    """Both id layers are opaque. Neither a patient name nor a username is a path."""
    secrets = ["Jordan", "Whitfield", "Dana", "Okoro",
               ALICE_USERNAME, BLAKE_USERNAME, "alice", "blake"]
    for root in (filed.patients_root, filed.users_root):
        for path in root.rglob("*"):
            relative = str(path.relative_to(root))
            for secret in secrets:
                assert secret.lower() not in relative.lower(), f"{relative} carries {secret!r}"


def test_the_only_identifying_text_on_disk_is_the_roster_and_the_usernames(filed: Filed):
    """Names appear in patient.json and usernames in user.json -- nowhere else."""
    for path in _every_file(filed.patients_root):
        blob = path.read_bytes()
        if b"Jordan Whitfield" in blob or b"Dana Okoro" in blob:
            assert path.name == patients.ROSTER_FILENAME, f"{path} carries a patient name"
    for path in _every_file(filed.users_root):
        blob = path.read_bytes()
        if ALICE_USERNAME.encode() in blob or BLAKE_USERNAME.encode() in blob:
            assert path.name == users.RECORD_FILENAME, f"{path} carries a username"


def test_no_password_reaches_disk(filed: Filed):
    for path in _every_file(filed.users_root):
        assert PASSWORD.encode("utf-8") not in path.read_bytes(), path


def test_every_audit_sidecar_declares_no_phi(filed: Filed):
    patients.set_active_user(filed.alice.id)
    out_dir = patients.patient_output_dir(filed.alice_patient.id)
    records = sorted(out_dir.glob("*.review.json"))
    assert records, "no review records were filed"
    for path in records:
        record = json.loads(path.read_text(encoding="utf-8"))
        blob = json.dumps(record)
        for identifier in KNOWN_IDENTIFIERS:
            assert identifier not in blob, f"{path.name} leaked {identifier!r}"


# --------------------------------------------------------------------------
# Accounts separate what they claim to
# --------------------------------------------------------------------------

def test_each_account_sees_only_its_own_roster(filed: Filed):
    patients.set_active_user(filed.alice.id)
    assert [p.display_name for p in patients.list_patients()] == ["Jordan Whitfield"]
    patients.set_active_user(filed.blake.id)
    assert [p.display_name for p in patients.list_patients()] == ["Dana Okoro"]


def test_one_account_cannot_reach_the_others_patient_by_id(filed: Filed):
    patients.set_active_user(filed.blake.id)
    with pytest.raises(patients.PatientError):
        patients.get_patient(filed.alice_patient.id)
    assert patients.filed_documents(filed.alice_patient.id) == []


def test_the_two_accounts_file_into_different_directories(filed: Filed):
    patients.set_active_user(filed.alice.id)
    alice_dir = patients.patient_output_dir(filed.alice_patient.id)
    patients.set_active_user(filed.blake.id)
    blake_dir = patients.patient_output_dir(filed.blake_patient.id)
    assert alice_dir != blake_dir
    assert filed.alice.id in str(alice_dir)
    assert filed.blake.id in str(blake_dir)


def test_deleting_one_accounts_patient_leaves_the_other_intact(filed: Filed):
    """Runs last of the store tests: it mutates Blake's roster."""
    patients.set_active_user(filed.blake.id)
    patients.delete_patient(filed.blake_patient.id)
    assert patients.list_patients() == []

    patients.set_active_user(filed.alice.id)
    assert [p.display_name for p in patients.list_patients()] == ["Jordan Whitfield"]
    assert len(patients.filed_documents(filed.alice_patient.id)) == len(PIPELINE_DOCS) * 3
    # Put it back for anything that runs after.
    patients.set_active_user(filed.blake.id)
    filed.blake_patient = patients.create_patient("Dana Okoro")


# --------------------------------------------------------------------------
# ... and the frontend shows it
# --------------------------------------------------------------------------

def test_the_app_shows_the_signed_in_accounts_patient(filed: Filed):
    app = run_app(user_id=filed.alice.id, username=filed.alice.username)
    body = screen_text(app)
    assert "Jordan Whitfield" in body
    assert f"{len(PIPELINE_DOCS) * 3} documents" in body


def test_the_app_does_not_show_another_accounts_patient(filed: Filed):
    app = run_app(user_id=filed.blake.id, username=filed.blake.username)
    assert "Jordan Whitfield" not in screen_text(app)


def test_the_browser_opens_a_patient_and_lists_the_filed_artefacts(filed: Filed):
    app = run_app(user_id=filed.alice.id, username=filed.alice.username,
                  browse_patient_id=filed.alice_patient.id)
    body = screen_text(app)
    stem = Path(PIPELINE_DOCS[0].name).stem
    assert f"{stem}.deid.txt" in body
    assert f"{stem}.deid.docx" in body
    # Grouped under clinician-facing labels, not the raw stored kind.
    assert "Word document" in body
    assert "Review record" in body


def test_the_browser_offers_a_download_per_artefact(filed: Filed):
    """One download per filed artefact, and none for anyone else's.

    ``AppTest`` does not surface a key on a download-button node, so this
    counts them and pins the count to the artefacts actually on disk -- an
    account leaking another's documents into the browser would push it up.
    """
    app = run_app(user_id=filed.alice.id, username=filed.alice.username,
                  browse_patient_id=filed.alice_patient.id)
    buttons = app.get("download_button")
    assert len(buttons) == len(PIPELINE_DOCS) * 3
    assert {b.label for b in buttons} == {"Download"}

    # Blake, with the same patient opened by id, is offered nothing.
    other = run_app(user_id=filed.blake.id, username=filed.blake.username,
                    browse_patient_id=filed.alice_patient.id)
    assert other.get("download_button") == []


def test_the_browser_search_filters_the_roster(filed: Filed):
    app = run_app(user_id=filed.alice.id, username=filed.alice.username,
                  patient_query="nobody-by-this-name")
    body = screen_text(app)
    assert "Jordan Whitfield" not in body
    assert "No patient matches" in body


def test_signing_out_from_a_working_session_clears_it(filed: Filed):
    from tests.fixtures import DISCHARGE_SUMMARY

    docs = {"a.txt": batch.Document(name="a.txt", raw_text=DISCHARGE_SUMMARY)}
    app = run_app(user_id=filed.alice.id, username=filed.alice.username,
                  docs=docs, order=list(docs), selected="a.txt",
                  patient_id=filed.alice_patient.id,
                  browse_patient_id=filed.alice_patient.id)
    app.sidebar.button(key="sign_out").click().run()

    assert app.session_state["user_id"] == ""
    assert app.session_state["docs"] == {}
    assert app.session_state["patient_id"] == ""
    assert "Sign in to CareScribe" in screen_text(app)
    # The filed documents are untouched on disk -- signing out is not a delete.
    patients.set_active_user(filed.alice.id)
    assert len(patients.filed_documents(filed.alice_patient.id)) == len(PIPELINE_DOCS) * 3


def test_a_wrong_password_does_not_sign_anyone_in(filed: Filed):
    assert users.authenticate(ALICE_USERNAME, "not the password") is None
    assert users.authenticate(ALICE_USERNAME, PASSWORD) is not None
