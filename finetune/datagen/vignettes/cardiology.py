"""Cardiology encounters, including a discharge."""

from __future__ import annotations

from finetune.datagen.sampling import Choice, Range, Subset
from finetune.datagen.schema import EncounterType

from .base import Vignette, med

VIGNETTES = [
    Vignette(
        id="cardio_hf_discharge",
        specialty="cardiology",
        encounter_type=EncounterType.DISCHARGE,
        weight=1.0,
        demographics={
            "age_band": Choice(["60-69", "70-79", "80-89"]),
            "sex": Choice(["M", "F"]),
            "occupation": "retired",
        },
        presenting_complaint="admitted with decompensated heart failure, now euvolaemic and for discharge",
        history=[
            {"label": "admission", "detail": "5-day stay, IV diuresis"},
            {"label": "weight", "detail": Range(2, 6, "kg lost during admission")},
            {"label": "function", "detail": "mobilising independently on the ward"},
        ],
        pmh=["heart failure with reduced ejection fraction", Choice(["atrial fibrillation", "ischaemic heart disease"])],
        meds=[
            med("furosemide", "40mg", "OD"),
            med("bisoprolol", Choice(["2.5mg", "5mg"]), "OD"),
            med("ramipril", Choice(["2.5mg", "5mg"]), "OD"),
        ],
        allergies=Subset(["aspirin"], 0, 1),
        examination=[
            {"system": "cardiovascular", "finding": "JVP", "value": "not elevated"},
            {"system": "respiratory", "finding": "chest", "value": "clear"},
            {"system": "general", "finding": "peripheral oedema", "value": "trace only"},
        ],
        investigations=[
            {"test": "echocardiogram", "value": "LVEF 35%", "flag": "abnormal"},
            {"test": "creatinine", "value": Range(90, 150, "µmol/L"), "flag": "high"},
        ],
        impression=["heart failure, compensated on discharge"],
        plan=[
            {"action": "medication", "detail": "continue as above; up-titrate bisoprolol in community"},
            {"action": "daily weights", "detail": "call GP if >2kg gain in 3 days"},
            {"action": "referral", "detail": "community heart failure nurse"},
        ],
        follow_up="cardiology clinic in 6 weeks",
        gappable=("allergies", "history"),
    ),
    Vignette(
        id="cardio_af_newref",
        specialty="cardiology",
        encounter_type=EncounterType.NEW,
        weight=1.0,
        demographics={
            "age_band": Choice(["55-64", "65-74", "75-84"]),
            "sex": Choice(["M", "F"]),
            "occupation": Choice(["retired", "self-employed", "clerical"]),
        },
        presenting_complaint="new-onset palpitations, GP found irregular pulse",
        history=[
            {"label": "symptoms", "detail": Choice(["intermittent palpitations for 2 weeks", "one episode of dizziness"])},
            {"label": "exertion", "detail": "no chest pain, no syncope"},
        ],
        pmh=Subset(["hypertension", "type 2 diabetes"], 0, 2),
        meds=[med("amlodipine", "5mg", "OD")],
        allergies=[],
        examination=[
            {"system": "cardiovascular", "finding": "pulse", "value": "irregularly irregular, ~90 bpm"},
            {"system": "cardiovascular", "finding": "heart sounds", "value": "normal, no murmurs"},
        ],
        investigations=[
            {"test": "ECG", "value": "atrial fibrillation, rate 96", "flag": "abnormal"},
            {"test": "TFT", "value": "normal", "flag": None},
        ],
        impression=["newly diagnosed atrial fibrillation"],
        plan=[
            {"action": "rate control", "detail": "start bisoprolol 2.5mg OD"},
            {"action": "anticoagulation", "detail": "start apixaban 5mg BD after CHA2DS2-VASc discussion"},
            {"action": "imaging", "detail": "request outpatient echocardiogram"},
        ],
        follow_up="6 weeks",
        gappable=("pmh", "investigations"),
    ),
]
