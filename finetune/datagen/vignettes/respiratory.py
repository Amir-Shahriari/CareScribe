"""Respiratory encounters."""

from __future__ import annotations

from finetune.datagen.sampling import Choice, Range, Subset
from finetune.datagen.schema import EncounterType

from .base import Vignette, med

VIGNETTES = [
    Vignette(
        id="resp_asthma_followup",
        specialty="respiratory",
        encounter_type=EncounterType.FOLLOW_UP,
        weight=1.1,
        demographics={
            "age_band": Choice(["18-29", "30-39", "40-49"]),
            "sex": Choice(["M", "F"]),
            "occupation": Choice(["teacher", "painter and decorator", "office worker"]),
        },
        presenting_complaint="asthma review, using reliever inhaler most days",
        history=[
            {"label": "control", "detail": Choice(["nocturnal cough 2 nights/week", "wakes once a week"])},
            {"label": "triggers", "detail": Choice(["cold air and exercise", "house dust"])},
            {"label": "technique", "detail": "inhaler technique checked, suboptimal"},
        ],
        pmh=Subset(["allergic rhinitis", "childhood eczema"], 0, 2),
        meds=[
            med("salbutamol", "100mcg", "QDS PRN"),
            med("beclometasone", Choice(["100mcg", "200mcg"]), "BD"),
        ],
        allergies=Subset(["pollen", "house dust mite"], 0, 2),
        examination=[
            {"system": "respiratory", "finding": "auscultation", "value": Choice(["mild expiratory wheeze", "clear"])},
            {"system": "respiratory", "finding": "peak flow", "value": Range(320, 470, "L/min")},
        ],
        investigations=[],
        impression=["partly controlled asthma, likely adherence and technique related"],
        plan=[
            {"action": "step up", "detail": "increase beclometasone to 200mcg BD"},
            {"action": "inhaler technique", "detail": "spacer supplied, technique re-taught"},
            {"action": "asthma action plan", "detail": "updated and given to patient"},
        ],
        follow_up="6 weeks",
        gappable=("allergies", "investigations", "follow_up"),
    ),
    Vignette(
        id="resp_copd_handover",
        specialty="respiratory",
        encounter_type=EncounterType.HANDOVER,
        weight=0.9,
        demographics={
            "age_band": Choice(["60-69", "70-79"]),
            "sex": Choice(["M", "F"]),
            "occupation": "retired",
        },
        presenting_complaint="ward handover: infective exacerbation of COPD, day 2 of admission",
        history=[
            {"label": "status", "detail": "less breathless today, still requires 2L oxygen"},
            {"label": "overnight", "detail": Choice(["settled night", "one episode of desaturation, resolved with physio"])},
        ],
        pmh=["COPD", Choice(["ischaemic heart disease", "osteoporosis"])],
        meds=[
            med("salbutamol", "200mcg", "QDS PRN"),
            med("paracetamol", "1g", "QDS PRN"),
        ],
        allergies=[],
        examination=[
            {"system": "respiratory", "finding": "auscultation", "value": "scattered wheeze, right base crackles"},
            {"system": "obs", "finding": "SpO2", "value": Range(88, 93, "% on 2L")},
        ],
        investigations=[
            {"test": "CRP", "value": Range(40, 120, "mg/L"), "flag": "high"},
            {"test": "chest X-ray", "value": "hyperinflation, no consolidation", "flag": None},
        ],
        impression=["infective exacerbation of COPD, improving"],
        plan=[
            {"action": "continue", "detail": "IV antibiotics day 2 of 5, oral steroids"},
            {"action": "wean oxygen", "detail": "target saturations 88-92%"},
            {"action": "physio", "detail": "twice daily"},
        ],
        follow_up="review on consultant ward round",
        gappable=("history", "investigations"),
    ),
]
