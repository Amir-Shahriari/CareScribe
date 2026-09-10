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
    Vignette(
        id="resp_copd_exacerbation_new",
        specialty="respiratory",
        encounter_type=EncounterType.NEW,
        weight=1.1,
        demographics={
            "age_band": Choice(["60-69", "70-79", "80-89"]),
            "sex": Choice(["M", "F"]),
            "occupation": Choice(["retired", "former welder", "former cleaner"]),
        },
        presenting_complaint="4 days of increased breathlessness and sputum volume",
        history=[
            {"label": "sputum", "detail": Choice(["now green", "thicker and darker than usual"])},
            {"label": "exercise tolerance", "detail": Choice(["down to 20 metres", "housebound since onset"])},
            {"label": "smoking", "detail": Choice(["ex-smoker, stopped years ago", "still smoking, wants to stop"])},
        ],
        pmh=["chronic obstructive pulmonary disease", Choice(["hypertension", "ischaemic heart disease"])],
        meds=[
            med("salbutamol", "200mcg", "QDS PRN"),
            med("beclometasone", Choice(["200mcg", "400mcg"]), "BD"),
        ],
        allergies=Subset(["penicillin"], 0, 1),
        examination=[
            {"system": "respiratory", "finding": "chest", "value": "widespread wheeze, prolonged expiratory phase"},
            {"system": "obs", "finding": "oxygen saturation", "value": Range(88, 94, "% on air")},
            {"system": "obs", "finding": "respiratory rate", "value": Range(20, 28, "per minute")},
        ],
        investigations=[
            {"test": "chest radiograph", "value": "no consolidation", "flag": None},
        ],
        impression=["infective exacerbation of chronic obstructive pulmonary disease"],
        plan=[
            {"action": "rescue pack", "detail": "oral steroid and antibiotic course commenced"},
            {"action": "inhaler technique", "detail": "checked and corrected in clinic"},
            {"action": "safety-net", "detail": "seek urgent review if saturations fall further or confusion develops"},
        ],
        follow_up="review in 1 week",
        gappable=("allergies", "investigations", "follow_up"),
    ),
    Vignette(
        id="resp_pneumonia_discharge",
        specialty="respiratory",
        encounter_type=EncounterType.DISCHARGE,
        weight=1.0,
        demographics={
            "age_band": Choice(["50-59", "60-69", "70-79"]),
            "sex": Choice(["M", "F"]),
            "occupation": Choice(["retired", "warehouse operative", "teacher"]),
        },
        presenting_complaint="admitted with community-acquired pneumonia, now well enough for discharge",
        history=[
            {"label": "admission", "detail": Range(3, 7, "day inpatient stay")},
            {"label": "response", "detail": "afebrile for 48 hours, oxygen requirement weaned off"},
            {"label": "function", "detail": Choice(["independently mobile on the ward", "mobilising with a frame as before"])},
        ],
        pmh=Subset(["type 2 diabetes", "hypertension", "chronic kidney disease"], 0, 2),
        meds=[med("paracetamol", "1g", "QDS PRN")],
        allergies=Subset(["penicillin"], 0, 1),
        examination=[
            {"system": "respiratory", "finding": "chest", "value": "reduced air entry at the base, improving"},
            {"system": "obs", "finding": "oxygen saturation", "value": Range(94, 98, "% on air")},
            {"system": "obs", "finding": "temperature", "value": "afebrile"},
        ],
        investigations=[
            {"test": "chest radiograph", "value": "consolidation resolving", "flag": "abnormal"},
            {"test": "C-reactive protein", "value": "falling", "flag": None},
        ],
        impression=["community-acquired pneumonia, resolving"],
        plan=[
            {"action": "complete antibiotic course", "detail": "finish the remaining oral days at home"},
            {"action": "repeat imaging", "detail": "chest radiograph at 6 weeks to confirm resolution"},
            {"action": "safety-net", "detail": "return if fever recurs or breathlessness worsens"},
        ],
        follow_up="GP review in 2 weeks",
        gappable=("allergies", "pmh", "investigations"),
    ),
]
