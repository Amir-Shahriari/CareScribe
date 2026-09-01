"""General-practice encounters — the broad, undifferentiated middle."""

from __future__ import annotations

from finetune.datagen.sampling import Choice, Range, Subset
from finetune.datagen.schema import EncounterType

from .base import Vignette, med

VIGNETTES = [
    Vignette(
        id="gp_uri_new",
        specialty="general practice",
        encounter_type=EncounterType.NEW,
        weight=1.4,
        demographics={
            "age_band": Choice(["18-29", "30-39", "40-49"]),
            "sex": Choice(["M", "F"]),
            "occupation": Choice(["teacher", "warehouse operative", "student", "carer"]),
        },
        presenting_complaint=Choice(
            [
                "3 days of sore throat, dry cough and low-grade fever",
                "productive cough and coryza for a week, no breathlessness",
            ]
        ),
        history=[
            {"label": "onset", "detail": Choice(["3 days ago", "5 days ago", "1 week ago"])},
            {"label": "systemic", "detail": "no rigors, eating and drinking normally"},
        ],
        pmh=Subset(["hay fever", "childhood asthma", "eczema"], 0, 2),
        meds=[],
        allergies=Subset(["penicillin"], 0, 1),
        examination=[
            {"system": "ENT", "finding": "pharyngeal erythema", "value": "mild"},
            {"system": "respiratory", "finding": "chest", "value": "clear, no crackles"},
            {"system": "obs", "finding": "temperature", "value": Range(37, 38, "°C")},
        ],
        investigations=[],
        impression=Choice([["viral upper respiratory tract infection"], ["acute bronchitis, likely viral"]]),
        plan=[
            {"action": "self-care advice", "detail": "fluids, paracetamol, rest"},
            {"action": "safety-net", "detail": "return if breathless or fever beyond 5 days"},
        ],
        follow_up=Choice([None, "only if not settling in 1 week"]),
        gappable=("allergies", "investigations", "follow_up"),
    ),
    Vignette(
        id="gp_htn_review",
        specialty="general practice",
        encounter_type=EncounterType.FOLLOW_UP,
        weight=1.2,
        demographics={
            "age_band": Choice(["50-59", "60-69", "70-79"]),
            "sex": Choice(["M", "F"]),
            "occupation": Choice(["retired", "accountant", "bus driver"]),
        },
        presenting_complaint="hypertension review, feels well, no side effects",
        history=[
            {"label": "adherence", "detail": "takes medication daily"},
            {"label": "lifestyle", "detail": Choice(["walks 30 min most days", "largely sedentary"])},
        ],
        pmh=["hypertension", Choice(["type 2 diabetes", "hypercholesterolaemia"])],
        meds=[
            med("amlodipine", Choice(["5mg", "10mg"]), "OD"),
            med("atorvastatin", "20mg", "ON"),
        ],
        allergies=[],
        examination=[
            {"system": "cardiovascular", "finding": "clinic BP", "value": Range(128, 152, "mmHg systolic")},
            {"system": "cardiovascular", "finding": "heart sounds", "value": "normal, no murmurs"},
        ],
        investigations=[
            {"test": "U&E", "value": "within normal limits", "flag": None},
            {"test": "HbA1c", "value": Range(38, 58, "mmol/mol"), "flag": None},
        ],
        impression=["hypertension, borderline control"],
        plan=[
            {"action": "titrate antihypertensive", "detail": "increase amlodipine to 10mg OD"},
            {"action": "home BP monitoring", "detail": "1 week diary"},
        ],
        follow_up="4 weeks with home readings",
        gappable=("investigations", "history"),
    ),
]
