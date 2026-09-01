"""Elderly-care / geriatric medicine encounters."""

from __future__ import annotations

from finetune.datagen.sampling import Choice, Range, Subset
from finetune.datagen.schema import EncounterType

from .base import Vignette, med

VIGNETTES = [
    Vignette(
        id="elderly_falls_new",
        specialty="elderly care",
        encounter_type=EncounterType.NEW,
        weight=1.1,
        demographics={
            "age_band": Choice(["75-84", "85-94"]),
            "sex": Choice(["M", "F"]),
            "occupation": "retired",
        },
        presenting_complaint="two falls at home in the past month, no loss of consciousness",
        history=[
            {"label": "falls", "detail": Choice(["both indoors, tripped on rug", "one on the stairs, one in the garden"])},
            {"label": "function", "detail": "uses a stick outdoors, independent with personal care"},
            {"label": "postural symptoms", "detail": "light-headed on standing"},
        ],
        pmh=["hypertension", "osteoarthritis", Choice(["mild cognitive impairment", "type 2 diabetes"])],
        meds=[
            med("amlodipine", "10mg", "OD"),
            med("atorvastatin", "40mg", "ON"),
        ],
        allergies=Subset(["codeine"], 0, 1),
        examination=[
            {"system": "cardiovascular", "finding": "lying/standing BP", "value": Range(15, 35, "mmHg drop")},
            {"system": "neurological", "finding": "gait", "value": "cautious, wide-based"},
            {"system": "musculoskeletal", "finding": "lower limb power", "value": "4+/5 symmetrical"},
        ],
        investigations=[
            {"test": "bone profile", "value": "normal", "flag": None},
            {"test": "vitamin D", "value": Range(20, 45, "nmol/L"), "flag": "low"},
        ],
        impression=["recurrent falls, multifactorial — orthostatic hypotension and deconditioning"],
        plan=[
            {"action": "medication review", "detail": "reduce amlodipine to 5mg OD"},
            {"action": "referral", "detail": "community falls team and physiotherapy"},
            {"action": "bone health", "detail": "start vitamin D replacement"},
        ],
        follow_up="6 weeks in the falls clinic",
        gappable=("allergies", "investigations", "history"),
    ),
    Vignette(
        id="elderly_dementia_review",
        specialty="elderly care",
        encounter_type=EncounterType.FOLLOW_UP,
        weight=1.0,
        demographics={
            "age_band": Choice(["75-84", "85-94"]),
            "sex": Choice(["M", "F"]),
            "occupation": "retired",
        },
        presenting_complaint="memory clinic review of Alzheimer's disease, 6 months on treatment",
        history=[
            {"label": "cognition", "detail": Choice(["stable per family", "mild further decline in word-finding"])},
            {"label": "behaviour", "detail": Choice(["no agitation", "occasional evening restlessness"])},
            {"label": "carer", "detail": "spouse coping, attends carer support group"},
        ],
        pmh=["Alzheimer's disease", "hypertension"],
        meds=[med("donepezil", Choice(["5mg", "10mg"]), "ON")],
        allergies=[],
        examination=[
            {"system": "cognition", "finding": "MoCA", "value": Range(16, 24, "/30")},
            {"system": "general", "finding": "weight", "value": "stable"},
        ],
        investigations=[],
        impression=["Alzheimer's disease, slow expected progression, tolerating donepezil"],
        plan=[
            {"action": "continue donepezil", "detail": "at current dose"},
            {"action": "carer support", "detail": "reiterate respite options"},
            {"action": "advance care planning", "detail": "revisit at next review"},
        ],
        follow_up="6 months",
        gappable=("investigations", "follow_up"),
    ),
]
