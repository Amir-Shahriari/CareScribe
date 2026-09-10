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
    Vignette(
        id="gp_back_pain_new",
        specialty="general practice",
        encounter_type=EncounterType.NEW,
        weight=1.2,
        demographics={
            "age_band": Choice(["30-39", "40-49", "50-59"]),
            "sex": Choice(["M", "F"]),
            "occupation": Choice(["warehouse operative", "nurse", "driver", "office worker"]),
        },
        presenting_complaint=Choice(
            [
                "4 days of lower back pain after lifting at work, no leg symptoms",
                "2 weeks of aching lumbar pain, worse on standing, easing when sitting",
            ]
        ),
        history=[
            {"label": "onset", "detail": Choice(["lifting a heavy box", "no clear trigger", "a long drive"])},
            {"label": "red flags", "detail": "no bladder or bowel disturbance, no saddle anaesthesia, no night pain"},
            {"label": "function", "detail": Choice(["still working with difficulty", "off work since onset"])},
        ],
        pmh=Subset(["previous back strain", "obesity", "hypertension"], 0, 2),
        meds=[med("paracetamol", "1g", "QDS PRN")],
        allergies=Subset(["ibuprofen"], 0, 1),
        examination=[
            {"system": "musculoskeletal", "finding": "lumbar movement", "value": "restricted flexion, paraspinal tenderness"},
            {"system": "neurological", "finding": "straight leg raise", "value": "negative bilaterally"},
            {"system": "neurological", "finding": "power and sensation", "value": "normal in both legs"},
        ],
        investigations=[],
        impression=["mechanical lower back pain, no red flags"],
        plan=[
            {"action": "analgesia", "detail": "regular paracetamol, topical NSAID if tolerated"},
            {"action": "activity advice", "detail": "keep moving, avoid bed rest"},
            {"action": "safety-net", "detail": "return urgently if bladder or bowel symptoms or leg weakness"},
        ],
        follow_up=Choice([None, "2 weeks if not improving"]),
        gappable=("allergies", "investigations", "follow_up"),
    ),
    Vignette(
        id="gp_t2dm_review",
        specialty="general practice",
        encounter_type=EncounterType.FOLLOW_UP,
        weight=1.1,
        demographics={
            "age_band": Choice(["50-59", "60-69", "70-79"]),
            "sex": Choice(["M", "F"]),
            "occupation": Choice(["retired", "shop manager", "cleaner"]),
        },
        presenting_complaint="annual type 2 diabetes review, no new symptoms",
        history=[
            {"label": "adherence", "detail": Choice(["takes metformin as prescribed", "occasional missed doses"])},
            {"label": "hypoglycaemia", "detail": "no hypoglycaemic episodes reported"},
            {"label": "lifestyle", "detail": Choice(["diet unchanged", "has reduced sugary drinks", "walks daily"])},
        ],
        pmh=["type 2 diabetes", Choice(["hypertension", "hypercholesterolaemia"])],
        meds=[
            med("metformin", Choice(["500mg", "1g"]), "BD"),
            med("atorvastatin", Choice(["20mg", "40mg"]), "ON"),
        ],
        allergies=[],
        examination=[
            {"system": "obs", "finding": "BMI", "value": Range(26, 34, "kg/m2")},
            {"system": "cardiovascular", "finding": "clinic BP", "value": Range(124, 148, "mmHg systolic")},
            {"system": "peripheral", "finding": "foot check", "value": "pulses present, monofilament sensation intact"},
        ],
        investigations=[
            {"test": "HbA1c", "value": Range(48, 72, "mmol/mol"), "flag": None},
            {"test": "eGFR", "value": Range(62, 92, "mL/min/1.73m2"), "flag": None},
            {"test": "urine ACR", "value": "not elevated", "flag": None},
        ],
        impression=["type 2 diabetes, suboptimal glycaemic control"],
        plan=[
            {"action": "reinforce lifestyle measures", "detail": "diet and activity advice given"},
            {"action": "continue metformin", "detail": "no dose change today"},
            {"action": "retinal screening", "detail": "confirm invitation attended"},
        ],
        follow_up="6 months",
        gappable=("investigations", "history", "follow_up"),
    ),
    Vignette(
        id="gp_uti_new",
        specialty="general practice",
        encounter_type=EncounterType.NEW,
        weight=1.0,
        demographics={
            "age_band": Choice(["18-29", "30-39", "40-49"]),
            "sex": "F",
            "occupation": Choice(["teacher", "student", "administrator"]),
        },
        presenting_complaint="2 days of dysuria and urinary frequency",
        history=[
            {"label": "onset", "detail": Choice(["2 days ago", "since yesterday"])},
            {"label": "systemic", "detail": "no fever, no loin pain, no vomiting"},
            {"label": "obstetric", "detail": "not pregnant"},
        ],
        pmh=Subset(["previous urinary tract infection"], 0, 1),
        meds=[],
        allergies=Subset(["penicillin", "trimethoprim"], 0, 1),
        examination=[
            {"system": "abdominal", "finding": "suprapubic tenderness", "value": Choice(["mild", "none"])},
            {"system": "abdominal", "finding": "renal angle tenderness", "value": "absent"},
            {"system": "obs", "finding": "temperature", "value": "afebrile"},
        ],
        investigations=[
            {"test": "urine dipstick", "value": "nitrites and leucocytes positive", "flag": "abnormal"},
        ],
        impression=["uncomplicated lower urinary tract infection"],
        plan=[
            {"action": "antibiotic", "detail": "short course per local guideline"},
            {"action": "fluids and analgesia", "detail": "advice given"},
            {"action": "safety-net", "detail": "return if fever, loin pain or no better in 48 hours"},
        ],
        follow_up=Choice([None, "only if symptoms persist"]),
        gappable=("allergies", "pmh", "follow_up"),
    ),
    Vignette(
        id="gp_polypharmacy_review",
        specialty="general practice",
        encounter_type=EncounterType.FOLLOW_UP,
        weight=0.9,
        demographics={
            "age_band": Choice(["70-79", "80-89"]),
            "sex": Choice(["M", "F"]),
            "occupation": "retired",
        },
        presenting_complaint="structured medication review, reports occasional light-headedness on standing",
        history=[
            {"label": "symptoms", "detail": Choice(["light-headed on standing", "mild ankle swelling", "no new symptoms otherwise"])},
            {"label": "adherence", "detail": Choice(["uses a dosette box", "manages own medication"])},
            {"label": "falls", "detail": "no falls in the last six months"},
        ],
        pmh=["hypertension", "atrial fibrillation", Choice(["heart failure", "osteoarthritis"])],
        meds=[
            med("ramipril", Choice(["5mg", "10mg"]), "OD"),
            med("bisoprolol", Choice(["2.5mg", "5mg"]), "OD"),
            med("apixaban", "5mg", "BD"),
            med("furosemide", "20mg", "OD"),
        ],
        allergies=[],
        examination=[
            {"system": "cardiovascular", "finding": "lying BP", "value": Range(126, 146, "mmHg systolic")},
            {"system": "cardiovascular", "finding": "standing BP", "value": Range(104, 126, "mmHg systolic")},
            {"system": "cardiovascular", "finding": "pulse", "value": Range(58, 82, "bpm, irregular")},
        ],
        investigations=[
            {"test": "U&E", "value": "stable, no new derangement", "flag": None},
        ],
        impression=["polypharmacy with postural symptoms, likely antihypertensive burden"],
        plan=[
            {"action": "reduce furosemide", "detail": "stop and monitor ankle swelling"},
            {"action": "postural advice", "detail": "rise slowly, maintain fluid intake"},
            {"action": "repeat bloods", "detail": "U&E in two weeks after change"},
        ],
        follow_up="4 weeks",
        gappable=("investigations", "history"),
    ),
]
