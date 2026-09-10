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
    Vignette(
        id="elderly_delirium_new",
        specialty="elderly care",
        encounter_type=EncounterType.NEW,
        weight=1.1,
        demographics={
            "age_band": Choice(["70-79", "80-89"]),
            "sex": Choice(["M", "F"]),
            "occupation": "retired",
        },
        presenting_complaint="acute confusion over 48 hours, out of character per the family",
        history=[
            {"label": "onset", "detail": Choice(["abrupt, worse in the evenings", "fluctuating through the day"])},
            {"label": "precipitant", "detail": Choice(["reduced oral intake", "recent urinary symptoms", "a new sedating medication"])},
            {"label": "baseline", "detail": Choice(["independent at home before this", "needs help with washing and dressing"])},
        ],
        pmh=["hypertension", Choice(["mild cognitive impairment", "type 2 diabetes"])],
        meds=[
            med("amlodipine", "5mg", "OD"),
            med("paracetamol", "1g", "QDS PRN"),
        ],
        allergies=[],
        examination=[
            {"system": "cognition", "finding": "attention", "value": "inattentive, cannot recite months backwards"},
            {"system": "neurological", "finding": "focal signs", "value": "none"},
            {"system": "obs", "finding": "temperature", "value": "afebrile"},
        ],
        investigations=[
            {"test": "urine dipstick", "value": "leucocytes positive, nitrites negative", "flag": "abnormal"},
            {"test": "eGFR", "value": Range(38, 68, "mL/min/1.73m2"), "flag": "low"},
        ],
        impression=["delirium, precipitant not yet confirmed"],
        plan=[
            {"action": "treat reversible causes", "detail": "hydration and review of sedating medication"},
            {"action": "delirium care", "detail": "orientation, daylight, familiar objects, family presence encouraged"},
            {"action": "avoid sedation", "detail": "no antipsychotic unless there is risk of harm"},
        ],
        follow_up="reassess cognition in 72 hours",
        gappable=("investigations", "history", "follow_up"),
    ),
    Vignette(
        id="elderly_discharge_home",
        specialty="elderly care",
        encounter_type=EncounterType.DISCHARGE,
        weight=1.0,
        demographics={
            "age_band": Choice(["70-79", "80-89"]),
            "sex": Choice(["M", "F"]),
            "occupation": "retired",
        },
        presenting_complaint="discharge home after rehabilitation following a fall",
        history=[
            {"label": "admission", "detail": "admitted after a fall at home, no fracture"},
            {"label": "rehabilitation", "detail": Choice(["mobilising with a frame", "mobilising with a stick, supervised on stairs"])},
            {"label": "support", "detail": Choice(["package of care restarting", "family providing daily support", "lives with a spouse"])},
        ],
        pmh=["osteoarthritis", Choice(["hypertension", "atrial fibrillation"])],
        meds=[
            med("paracetamol", "1g", "QDS PRN"),
            med("apixaban", "2.5mg", "BD"),
        ],
        allergies=Subset(["codeine"], 0, 1),
        examination=[
            {"system": "musculoskeletal", "finding": "gait", "value": "slow and cautious, no ataxia"},
            {"system": "cardiovascular", "finding": "lying and standing BP", "value": "no significant postural drop"},
            {"system": "general", "finding": "skin", "value": "intact, no pressure damage"},
        ],
        investigations=[],
        impression=["fall without fracture, rehabilitation goals met"],
        plan=[
            {"action": "home equipment", "detail": "rails and a raised toilet seat fitted before discharge"},
            {"action": "falls prevention", "detail": "strength and balance programme arranged"},
            {"action": "medication review", "detail": "sedating medication avoided, analgesia continued"},
        ],
        follow_up="community therapy review within 2 weeks",
        gappable=("allergies", "investigations", "follow_up"),
    ),
    Vignette(
        id="elderly_continence_followup",
        specialty="elderly care",
        encounter_type=EncounterType.FOLLOW_UP,
        weight=0.9,
        demographics={
            "age_band": Choice(["70-79", "80-89"]),
            "sex": "F",
            "occupation": "retired",
        },
        presenting_complaint="review of urinary incontinence after eight weeks of conservative measures",
        history=[
            {"label": "pattern", "detail": Choice(["urgency with occasional leakage", "leakage on coughing and standing"])},
            {"label": "response", "detail": Choice(["fewer episodes than before", "no real change so far"])},
            {"label": "impact", "detail": Choice(["avoiding outings", "using pads daily", "manages with planning"])},
        ],
        pmh=["osteoarthritis", Choice(["hypertension", "type 2 diabetes"])],
        meds=[med("amlodipine", "5mg", "OD")],
        allergies=[],
        examination=[
            {"system": "abdominal", "finding": "palpable bladder", "value": "not palpable"},
            {"system": "general", "finding": "peripheral oedema", "value": Choice(["none", "mild ankle oedema"])},
            {"system": "general", "finding": "skin", "value": "no excoriation in the perineal area"},
        ],
        investigations=[
            {"test": "post-void residual", "value": "not elevated", "flag": None},
        ],
        impression=["mixed urinary incontinence, partial response to conservative measures"],
        plan=[
            {"action": "continue pelvic floor training", "detail": "supervised programme extended"},
            {"action": "bladder diary", "detail": "three days before the next review"},
            {"action": "review fluid timing", "detail": "reduce evening caffeine"},
        ],
        follow_up="8 weeks",
        gappable=("investigations", "history", "follow_up"),
    ),
    Vignette(
        id="elderly_frailty_crisis",
        specialty="elderly care",
        encounter_type=EncounterType.CRISIS,
        weight=0.8,
        demographics={
            "age_band": Choice(["80-89", "90-99"]),
            "sex": Choice(["M", "F"]),
            "occupation": "retired",
        },
        presenting_complaint="urgent home visit after a sudden loss of function and two falls in a day",
        history=[
            {"label": "change", "detail": Choice(["off legs since this morning", "unable to transfer since yesterday"])},
            {"label": "carer concern", "detail": "the usual carer cannot manage the transfers safely"},
            {"label": "wishes", "detail": Choice(["wishes to stay at home if possible", "family asking about admission"])},
        ],
        pmh=["frailty", Choice(["heart failure with reduced ejection fraction", "chronic kidney disease"])],
        meds=[
            med("furosemide", "20mg", "OD"),
            med("paracetamol", "1g", "QDS PRN"),
        ],
        allergies=[],
        examination=[
            {"system": "general", "finding": "hydration", "value": Choice(["dry mucous membranes", "well hydrated"])},
            {"system": "obs", "finding": "temperature", "value": "afebrile"},
            {"system": "musculoskeletal", "finding": "hips", "value": "no shortening or rotation, no bony tenderness"},
        ],
        investigations=[],
        impression=["acute functional decline on a background of frailty, no fracture identified"],
        plan=[
            {"action": "urgent community response", "detail": "same-day therapy and nursing input at home"},
            {"action": "increase care", "detail": "additional visits arranged for transfers"},
            {"action": "escalation discussion", "detail": "treatment preferences revisited with the patient and family"},
        ],
        follow_up="review tomorrow by the community team",
        gappable=("investigations", "history"),
    ),
]
