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
    Vignette(
        id="cardio_chest_pain_new",
        specialty="cardiology",
        encounter_type=EncounterType.NEW,
        weight=1.1,
        demographics={
            "age_band": Choice(["50-59", "60-69", "70-79"]),
            "sex": Choice(["M", "F"]),
            "occupation": Choice(["retired", "engineer", "shop manager", "driver"]),
        },
        presenting_complaint="referred with exertional chest tightness over the past two months",
        history=[
            {"label": "character", "detail": Choice(["central tightness on hills", "heaviness after climbing stairs"])},
            {"label": "relief", "detail": "settles within a few minutes of rest"},
            {"label": "risk factors", "detail": Choice(["ex-smoker", "family history of early coronary disease", "no smoking history"])},
        ],
        pmh=Subset(["hypertension", "hypercholesterolaemia", "type 2 diabetes"], 0, 3),
        meds=[
            med("atorvastatin", Choice(["20mg", "40mg"]), "ON"),
            med("amlodipine", "5mg", "OD"),
        ],
        allergies=[],
        examination=[
            {"system": "cardiovascular", "finding": "heart sounds", "value": "normal, no murmurs"},
            {"system": "cardiovascular", "finding": "clinic BP", "value": Range(128, 156, "mmHg systolic")},
            {"system": "general", "finding": "peripheral oedema", "value": "none"},
        ],
        investigations=[
            {"test": "resting ECG", "value": "sinus rhythm, no ischaemic change", "flag": None},
            {"test": "total cholesterol", "value": Range(4, 7, "mmol/L"), "flag": None},
        ],
        impression=["stable angina, likely obstructive coronary disease"],
        plan=[
            {"action": "CT coronary angiography", "detail": "requested as first-line imaging"},
            {"action": "antianginal", "detail": "commence a rate-limiting agent"},
            {"action": "safety-net", "detail": "attend emergency care if pain occurs at rest or lasts beyond 15 minutes"},
        ],
        follow_up="clinic review after imaging",
        gappable=("pmh", "allergies", "follow_up"),
    ),
    Vignette(
        id="cardio_post_mi_followup",
        specialty="cardiology",
        encounter_type=EncounterType.FOLLOW_UP,
        weight=1.0,
        demographics={
            "age_band": Choice(["50-59", "60-69", "70-79"]),
            "sex": Choice(["M", "F"]),
            "occupation": Choice(["retired", "electrician", "teacher"]),
        },
        presenting_complaint="six-week review after myocardial infarction and stenting",
        history=[
            {"label": "symptoms", "detail": Choice(["no further chest pain", "occasional twinges, not exertional"])},
            {"label": "rehabilitation", "detail": Choice(["attending cardiac rehab", "declined cardiac rehab", "on the waiting list"])},
            {"label": "adherence", "detail": "taking all discharge medication"},
        ],
        pmh=["myocardial infarction", Choice(["hypertension", "hypercholesterolaemia"])],
        meds=[
            med("bisoprolol", Choice(["2.5mg", "5mg"]), "OD"),
            med("ramipril", Choice(["2.5mg", "5mg"]), "OD"),
            med("atorvastatin", "80mg", "ON"),
        ],
        allergies=Subset(["aspirin"], 0, 1),
        examination=[
            {"system": "cardiovascular", "finding": "clinic BP", "value": Range(112, 138, "mmHg systolic")},
            {"system": "cardiovascular", "finding": "pulse", "value": Range(54, 76, "bpm, regular")},
            {"system": "general", "finding": "wound site", "value": "radial site healed, no haematoma"},
        ],
        investigations=[
            {"test": "echocardiogram", "value": "LVEF 48%", "flag": "abnormal"},
        ],
        impression=["post-infarct recovery on track, mildly impaired left ventricular function"],
        plan=[
            {"action": "up-titrate beta blocker", "detail": "as blood pressure allows"},
            {"action": "continue secondary prevention", "detail": "no changes to statin or ACE inhibitor"},
            {"action": "reinforce cardiac rehabilitation", "detail": "benefits discussed again"},
        ],
        follow_up="6 months",
        gappable=("allergies", "investigations", "history"),
    ),
]
