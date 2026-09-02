"""Community mental health / psychology encounters."""

from __future__ import annotations

from finetune.datagen.sampling import Choice, Subset
from finetune.datagen.schema import EncounterType

from .base import Vignette, med

VIGNETTES = [
    Vignette(
        id="cmht_depression_followup",
        specialty="community mental health",
        encounter_type=EncounterType.FOLLOW_UP,
        weight=1.3,
        demographics={
            "age_band": Choice(["18-29", "30-39", "40-49", "50-59"]),
            "sex": Choice(["M", "F"]),
            "occupation": Choice(["unemployed", "part-time retail", "administrator", "carer"]),
        },
        presenting_complaint="review of moderate depressive episode, 6 weeks into treatment",
        history=[
            {"label": "mood", "detail": Choice(["slightly improved", "unchanged", "brighter, more engaged"])},
            {"label": "sleep", "detail": Choice(["still early-morning waking", "improving"])},
            {"label": "risk", "detail": "no active suicidal ideation, no plans or intent"},
        ],
        pmh=Subset(["previous depressive episode", "generalised anxiety disorder"], 0, 2),
        meds=[med("sertraline", Choice(["50mg", "100mg"]), "OD")],
        allergies=[],
        examination=[
            {"system": "mental state", "finding": "affect", "value": "reactive, mildly low"},
            {"system": "mental state", "finding": "thought", "value": "no psychotic features"},
            {"system": "mental state", "finding": "cognition", "value": "grossly intact"},
        ],
        investigations=[],
        impression=["moderate depressive episode, partial response to SSRI"],
        plan=[
            {"action": "increase sertraline", "detail": "to 100mg OD, review tolerability"},
            {"action": "psychological therapy", "detail": "continue weekly CBT"},
            {"action": "safety plan", "detail": "reviewed and updated with patient"},
        ],
        follow_up="3 weeks",
        gappable=("pmh", "follow_up"),
    ),
    Vignette(
        id="cmht_crisis_contact",
        specialty="community mental health",
        encounter_type=EncounterType.CRISIS,
        weight=0.8,
        demographics={
            "age_band": Choice(["18-29", "30-39"]),
            "sex": Choice(["M", "F"]),
            "occupation": Choice(["student", "unemployed", "hospitality"]),
        },
        presenting_complaint="urgent review after presenting to crisis line with rising distress",
        history=[
            {"label": "trigger", "detail": Choice(["relationship breakdown", "job loss", "anniversary of bereavement"])},
            {"label": "risk", "detail": "fleeting thoughts of self-harm, no act, future-oriented, agrees to safety plan"},
            {"label": "supports", "detail": "staying with a friend tonight"},
        ],
        pmh=["emotionally unstable personality traits"],
        meds=[med("mirtazapine", "30mg", "ON")],
        allergies=[],
        examination=[
            {"system": "mental state", "finding": "affect", "value": "distressed, tearful, settles during contact"},
            {"system": "mental state", "finding": "risk", "value": "dynamic, currently low-moderate"},
        ],
        investigations=[],
        impression=["acute-on-chronic distress, no indication for admission"],
        plan=[
            {"action": "home treatment team", "detail": "daily contact for 72 hours"},
            {"action": "safety plan", "detail": "written copy given, crisis numbers confirmed"},
            {"action": "review medication", "detail": "no change today"},
        ],
        follow_up="telephone contact tomorrow morning",
        gappable=("investigations",),
    ),
]
