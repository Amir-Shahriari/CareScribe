"""
End-to-end evaluation of the patient records pipeline, one stage of the user
experience at a time.

The flow a clinician actually drives:

    create a patient  ->  for each source document:
        upload (ingest)  ->  de-identify  ->  review  ->  approve (file it)
    ...  ->  rename the patient  ->  work a second patient  ->  delete one

Every ``sample_documents/*.docx`` (15, deliberately varied: referral and
discharge letters, session logs, a pathology report, a medication chart, a
psychiatry letter, a psychometric report, a WorkCover certificate, imaging and
physiotherapy reports) is filed under one patient. The bar the store must clear
at every stage: **nothing identifying beyond the roster display name reaches
disk** — not a document's contents, not a placeholder-to-value mapping, not a
residual identifier, and the patient folder is an opaque id, never the name.

Everything here is fabricated — the sample documents are synthetic and describe
one fictional patient.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from carescribe.core import batch, deidentify, ingest, patients

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_documents"
DOCX_FILES = sorted(SAMPLE_DIR.glob("*.docx"))

# The fictional patient's hard identifiers, gathered from the source documents.
# None of these may appear anywhere under the store after filing.
KNOWN_IDENTIFIERS = (
    "Jordan Elliot Whitfield", "Whitfield", "12/04/1985",
    "2934 5671 0",                      # Medicare number
    "45 Kestrel Ave",                   # home address
    "0412 887 234", "0433 990 214",     # mobiles
    "jordan.whitfield85@example.com",   # email
    "Priya Whitfield",                  # relative
    "RFMP-88213", "MCDH-410287",        # facility record numbers
    "25-0788-441907",                   # pathology lab reference
    "CPC-4471",                         # psychiatry clinic file number
    "RAD-2025-77120",                   # imaging accession number
    "WC-2025-118342",                   # WorkCover claim number
    "2481726A", "2559071T", "2705513Y", "2810664R",  # provider numbers
)

pytestmark = pytest.mark.skipif(
    len(DOCX_FILES) < 15, reason="expected 15 sample_documents/*.docx"
)


@dataclass
class FiledCase:
    root: Path
    primary: patients.Patient
    secondary: patients.Patient
    redacted_by_doc: dict[str, str] = field(default_factory=dict)
    phi_by_doc: dict[str, dict[str, str]] = field(default_factory=dict)


def _approve_document(path: Path, patient_id: str) -> tuple[str, dict]:
    """Run one document through ingest -> de-identify -> file all three artefacts.

    Returns the redacted text and the de-identification result's phi_map so the
    caller can assert against it. Raises exactly what the real approve path would
    (``batch.BatchError``) if a write is refused.
    """
    name = path.name
    raw = ingest.extract_text(str(path))
    assert raw.strip(), f"{name}: ingest produced nothing"

    result = deidentify.deidentify(raw)
    redacted = result.redacted_text
    assert redacted.strip(), f"{name}: de-identification produced nothing"

    # The review stage is reachable only if the safety sweep is already clean —
    # prove it here so an approve failure below is a real regression, not a
    # document the pipeline could never file.
    assert deidentify.residual_scan(redacted) == [], name

    out = patients.patient_output_dir(patient_id)

    txt = batch.write_approved(name, redacted, output_dir=out)
    assert txt == out / f"{Path(name).stem}.deid.txt"

    replacements = batch.approved_map(result.entities, result.known_as)
    docx = batch.write_approved_docx(
        name, path.read_bytes(), replacements, output_dir=out
    )
    assert docx == out / f"{Path(name).stem}.deid.docx"

    review = batch.write_review_record(
        name,
        entities=result.entities,
        flags_shown=0,
        flags_redacted=0,
        flags_dismissed=0,
        attested=True,
        output_dir=out,
    )
    assert review == out / f"{Path(name).stem}.review.json"

    return redacted, dict(result.phi_map)


@pytest.fixture(scope="module")
def filed() -> FiledCase:
    """Drive the whole pipeline once: two patients, 15 documents filed under one."""
    import shutil
    import tempfile

    mp = pytest.MonkeyPatch()
    workdir = Path(tempfile.mkdtemp(prefix="carescribe-pipeline-"))
    root = workdir / "patients"
    mp.setenv("CARESCRIBE_PATIENTS_DIR", str(root))
    try:
        primary = patients.create_patient("Jordan Whitfield")
        secondary = patients.create_patient("Dana Okoro")

        case = FiledCase(root=root, primary=primary, secondary=secondary)

        for path in DOCX_FILES:
            redacted, phi_map = _approve_document(path, primary.id)
            case.redacted_by_doc[path.name] = redacted
            case.phi_by_doc[path.name] = phi_map

        # The second patient gets one document, to prove isolation.
        _approve_document(DOCX_FILES[0], secondary.id)

        yield case
    finally:
        mp.undo()
        shutil.rmtree(workdir, ignore_errors=True)


# --------------------------------------------------------------------------
# Stage: create a patient
# --------------------------------------------------------------------------

def test_the_patient_folder_is_an_opaque_id_never_the_name(filed: FiledCase):
    assert filed.primary.id.startswith("p_")
    assert filed.primary.display_name == "Jordan Whitfield"
    for path in filed.root.rglob("*"):
        rel = path.relative_to(filed.root)
        assert "Jordan" not in str(rel) and "Whitfield" not in str(rel), rel


def test_only_the_roster_json_carries_the_name(filed: FiledCase):
    """"Whitfield" is the roster display name — it must live nowhere else on disk."""
    carriers = []
    for path in sorted(filed.root.rglob("*")):
        if not path.is_file():
            continue
        try:
            body = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            body = path.read_bytes().decode("latin-1", "ignore")
        if "Whitfield" in body:
            carriers.append(path.relative_to(filed.root))
    assert len(carriers) == 1, carriers
    assert carriers[0] == Path(filed.primary.id) / "patient.json"


# --------------------------------------------------------------------------
# Stage: upload -> de-identify -> approve, once per document
# --------------------------------------------------------------------------

def test_every_document_is_filed_as_three_artefacts(filed: FiledCase):
    out = patients.patient_output_dir(filed.primary.id)
    assert len(sorted(out.glob("*.deid.txt"))) == 15
    assert len(sorted(out.glob("*.deid.docx"))) == 15
    assert len(sorted(out.glob("*.review.json"))) == 15


def test_filed_documents_lists_all_45_newest_first(filed: FiledCase):
    docs = patients.filed_documents(filed.primary.id)
    assert len(docs) == 45
    kinds = {d.kind for d in docs}
    assert kinds == {"text", "word", "audit"}
    stamps = [d.modified_at for d in docs]
    assert stamps == sorted(stamps, reverse=True)


@pytest.mark.parametrize("path", DOCX_FILES, ids=lambda p: p.name)
def test_each_redacted_text_is_free_of_known_identifiers(filed: FiledCase, path: Path):
    redacted = filed.redacted_by_doc[path.name]
    raw = ingest.extract_text(str(path))
    for ident in KNOWN_IDENTIFIERS:
        if ident in raw:
            assert ident not in redacted, (path.name, ident)


# --------------------------------------------------------------------------
# Stage: the store as a whole — nothing identifying beyond the roster name
# --------------------------------------------------------------------------

def _store_text_blob(root: Path) -> str:
    parts = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.name == "patient.json":
            continue
        if p.suffix == ".docx":
            parts.append(ingest.extract_text(str(p)))
        else:
            parts.append(p.read_text(encoding="utf-8"))
    return "\n".join(parts)


@pytest.mark.parametrize("path", DOCX_FILES, ids=lambda p: p.name)
def test_no_mapping_value_reaches_a_documents_own_filed_artefacts(
    filed: FiledCase, path: Path
):
    """Every literal this document mapped to a placeholder is gone from every
    artefact filed for it — text, audit sidecar, and redacted Word file.

    Checked per-document, not against a union: a bare prose date can be
    identifying in one source and ordinary text in another, and the store's
    guarantee is that a document's *own* detected identifiers never land in the
    files it produces."""
    stem = path.stem
    out = patients.patient_output_dir(filed.primary.id)
    filed_text = "\n".join((
        (out / f"{stem}.deid.txt").read_text(encoding="utf-8"),
        (out / f"{stem}.review.json").read_text(encoding="utf-8"),
        ingest.extract_text(str(out / f"{stem}.deid.docx")),
    ))
    values = {v for v in filed.phi_by_doc[path.name].values() if v and v.strip()}
    leaked = sorted(v for v in values if v in filed_text)
    assert leaked == [], (path.name, leaked)


def test_no_known_identifier_reaches_the_store(filed: FiledCase):
    blob = _store_text_blob(filed.root)
    leaked = sorted(i for i in KNOWN_IDENTIFIERS if i in blob)
    assert leaked == [], leaked


def test_residual_scan_over_the_whole_store_is_clean(filed: FiledCase):
    blob = _store_text_blob(filed.root)
    assert deidentify.residual_scan(blob) == []


def test_every_audit_sidecar_declares_no_phi(filed: FiledCase):
    sidecars = sorted(filed.root.rglob("*.review.json"))
    assert len(sidecars) == 16  # 15 for the primary, 1 for the secondary
    for path in sidecars:
        record = json.loads(path.read_text(encoding="utf-8"))
        assert record["contains_phi"] is False, path
        assert "placeholders_by_type" in record
        assert record["reviewer_attested"] is True


def test_the_redacted_docx_still_opens_and_carries_placeholders(filed: FiledCase):
    out = patients.patient_output_dir(filed.primary.id)
    for path in sorted(out.glob("*.deid.docx")):
        text = ingest.extract_text(str(path))
        assert text.strip(), path.name
        assert "[" in text and "]" in text, (path.name, "no placeholder survived")


# --------------------------------------------------------------------------
# Stage: rename the patient
# --------------------------------------------------------------------------

def test_rename_keeps_every_filed_document(filed: FiledCase):
    before = {d.name for d in patients.filed_documents(filed.primary.id)}
    renamed = patients.rename_patient(filed.primary.id, "Jordan E. Whitfield")
    try:
        assert renamed.display_name == "Jordan E. Whitfield"
        assert renamed.id == filed.primary.id
        after = {d.name for d in patients.filed_documents(filed.primary.id)}
        assert after == before
        assert len(after) == 45
    finally:
        patients.rename_patient(filed.primary.id, "Jordan Whitfield")


# --------------------------------------------------------------------------
# Stage: a second patient, kept isolated
# --------------------------------------------------------------------------

def test_the_second_patient_does_not_see_the_first_patients_documents(filed: FiledCase):
    primary = patients.filed_documents(filed.primary.id)
    secondary = patients.filed_documents(filed.secondary.id)
    assert len(primary) == 45
    assert len(secondary) == 3
    assert patients.patient_output_dir(filed.primary.id) != patients.patient_output_dir(
        filed.secondary.id
    )
    # The secondary patient only ever got document 01, in all three forms.
    assert {d.name for d in secondary} == {
        "01_gp_referral_letter.deid.txt",
        "01_gp_referral_letter.deid.docx",
        "01_gp_referral_letter.review.json",
    }


# --------------------------------------------------------------------------
# Stage: delete one patient
# --------------------------------------------------------------------------

def test_delete_removes_only_the_target_patient(filed: FiledCase):
    # Work on a throwaway third patient so the module fixture stays intact.
    victim = patients.create_patient("Temp Person")
    _approve_document(DOCX_FILES[1], victim.id)
    assert (filed.root / victim.id).is_dir()

    patients.delete_patient(victim.id)

    assert not (filed.root / victim.id).exists()
    survivors = {p.id for p in patients.list_patients()}
    assert survivors == {filed.primary.id, filed.secondary.id}
    assert len(patients.filed_documents(filed.primary.id)) == 45
    with pytest.raises(patients.PatientError):
        patients.get_patient(victim.id)
