# Graph Report - medgpt  (2026-08-06)

## Corpus Check
- 34 files · ~41,704 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 797 nodes · 1499 edges · 64 communities (42 shown, 22 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 23 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9f507523`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- deidentify.py
- batch.py
- extract_text
- test_app.py
- app.py
- Any
- Any
- rebuild
- redact
- test_mapping.py
- test_deid_pipeline.py
- residual_scan
- mapping.py
- dedupe_entities
- ollama_client.py
- test_review_gate.py
- resolve_placeholder
- expand_name_variants
- Precision Preservation Cases
- reidentify_detailed
- Care Note Prompt Templates
- Package Entry Point
- De-identification Prompts
- Prompts Package
- Test Suite Package
- Test Runner
- Identity-anchored Date Rule
- Clinical Acronym Filter
- Standalone Regex Layer
- test_docx_roundtrip.py
- deidentify
- Optional Layer Degradation
- No-NER Fallback Path
- test_deid_regressions.py
- test_generation.py
- carenotes.py
- Identity Map Not Stored
- NHS Number Spacing Variants
- test_stress_corpus.py
- Medication Block Integrity
- generate_document
- merge_spans
- conftest.py
- analyze
- refine_document
- canonical_person_key
- render_prompt
- load_protected_terms
- get_analyzer
- structured_spans
- _span_is_plausible
- _line_bounds
- Stress corpus
- with_banner
- _collapse_person_identities
- stress_report.py
- test_a_date_entity_never_spans_a_line_break
- test_in_prose_clinical_date_survives_by_default
- test_every_surname_form_maps_to_one_clinician
- test_a_patient_label_outranks_a_kinship_heading
- Exception
- fixture
- Path
- Pattern

## God Nodes (most connected - your core abstractions)
1. `deidentify()` - 57 edges
2. `Document` - 32 edges
3. `residual_scan()` - 23 edges
4. `structured_spans()` - 19 edges
5. `extract_text()` - 18 edges
6. `candidate_residuals()` - 17 edges
7. `run_app()` - 16 edges
8. `write_approved()` - 15 edges
9. `generate_document()` - 15 edges
10. `rebuild()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `Shared-surname Binding Collision` --rationale_for--> `surface_forms()`  [INFERRED]
  README.md → carescribe/core/mapping.py
- `presidio-analyzer` --references--> `_build_analyzer()`  [INFERRED]
  requirements.txt → carescribe/core/deidentify.py
- `spaCy Model Fallback Chain` --rationale_for--> `_build_analyzer()`  [INFERRED]
  requirements.txt → carescribe/core/deidentify.py
- `Batch Review Workflow` --references--> `rebuild()`  [INFERRED]
  README.md → carescribe/core/deidentify.py
- `pdfplumber` --references--> `extract_text()`  [INFERRED]
  requirements.txt → carescribe/core/ingest.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **The Five-layer De-identification Stack** — readme_layer1_structured_regex, readme_layer2_presidio_spacy, readme_layer3_gliner, readme_layer4_variant_expansion, readme_layer5_linebreak_matching [EXTRACTED 1.00]
- **PHI Containment Guarantees** — readme_no_network_calls, readme_mapping_never_on_disk, readme_single_write_path, readme_human_review_gate, readme_cpu_only_local [EXTRACTED 1.00]
- **Approve-time Write Flow** — readme_safety_sweep, carescribe_core_deidentify_residual_scan, carescribe_core_batch_write_approved, readme_dismissal_mechanism [EXTRACTED 1.00]

## Communities (64 total, 22 thin omitted)

### Community 0 - "deidentify.py"
Cohesion: 0.22
Nodes (12): date_span_wanted(), _has_contact_anchor(), _has_identity_anchor(), _is_clinical_measurement(), _looks_like_calendar_date(), Layered, CPU-only de-identification. No network, no GPU, no LLM. Every layer…, True if a real date sits in an appointment or contact clause., True if a date-shaped span is really a dosage or lab value. (+4 more)

### Community 1 - "batch.py"
Cohesion: 0.06
Nodes (54): approved_docx_path(), approved_path(), BatchError, list_folder(), load_documents(), Path, RuntimeError, Batch input and approved-output handling. The single module in CareScribe that… (+46 more)

### Community 2 - "extract_text"
Cohesion: 0.06
Nodes (54): Any, _build_analyzer(), Build a Presidio ``AnalyzerEngine`` over spaCy. Returns (engine, model, error)., _extract_docx(), _extract_pdf(), extract_text(), _extract_txt(), IngestError (+46 more)

### Community 3 - "test_app.py"
Cohesion: 0.14
Nodes (30): AppTest, analysed_batch(), data_editors(), loaded_batch(), _NullBackend, UI checks for the batch review app via Streamlit's AppTest. No server of any…, Generation must never run on text a human has not approved., The stub is gone; the contract it declared is still enforced. (+22 more)

### Community 4 - "app.py"
Cohesion: 0.07
Nodes (60): _as_docx(), current(), document_flags(), documents(), _draft_state(), entity_frame(), flag_dismissals(), ingest_sources() (+52 more)

### Community 7 - "rebuild"
Cohesion: 0.12
Nodes (18): add_manual_entity(), DeidentificationError, DeidResult, RuntimeError, Raised when de-identification can't run at all., Re-derive redacted text and the PHI map from a reviewer-edited table. Called…, Add an identifier the tools missed and immediately re-redact. The new value…, Everything the de-identification stage produces for one document. (+10 more)

### Community 8 - "redact"
Cohesion: 0.12
Nodes (17): find_known_as(), find_spans(), _form_pattern(), Pattern, Pull a patient's preferred name out of a "Known as:" field, if present., Whitespace-tolerant, case-insensitive pattern for one surface form. Tokens are…, Find non-overlapping ``(start, end, placeholder)`` spans for every form. All…, Replace every surface form of every entity with its placeholder. Replacement… (+9 more)

### Community 9 - "test_mapping.py"
Cohesion: 0.13
Nodes (16): assign_placeholders(), Attach a stable placeholder to each unique entity. A type with exactly one…, Swap placeholders back to their original values. Thin wrapper over…, reidentify(), Person Typing From Context, Stable Per-entity Placeholders, parametrize, Mapping-layer checks: type normalisation, surface forms, and re-identification.… (+8 more)

### Community 10 - "test_deid_pipeline.py"
Cohesion: 0.10
Nodes (13): Regression suite for the layered de-identification pipeline. Two guarantees,…, A bare digit run is a lab value; only a labelled one is a record number., The layer that exists specifically to catch an unlabelled name in prose., One real value, one placeholder — the whole point of the mapping., Two runs over the same text must agree, or review is meaningless., Margaret\\nChen" must redact to the SAME placeholder as the header name., test_analyze_returns_nothing_for_empty_text(), test_empty_document_is_rejected() (+5 more)

### Community 11 - "residual_scan"
Cohesion: 0.20
Nodes (10): Re-scan ALREADY-REDACTED text for anything that still looks identifying. Runs…, residual_scan(), Placeholders are the point of the exercise, not leaks., A .txt file read off a Windows disk arrives with CRLF endings. NER tokenises…, test_crlf_and_lf_documents_behave_identically(), test_residual_scan_catches_a_leaked_name(), test_residual_scan_catches_a_leaked_structured_identifier(), test_residual_scan_does_not_flag_placeholders() (+2 more)

### Community 12 - "mapping.py"
Cohesion: 0.21
Nodes (11): expand_facility_variants(), Issue, normalise_type(), In-memory PII <-> placeholder mapping. This module is deliberately pure: it…, Coerce a model-supplied type string onto the canonical list., Return the full organisation name plus short forms. "St. Aidan's General…, All strings that redact to a placeholder, plus collisions worth flagging., Expand entities into every surface form that should be redacted. Entity values… (+3 more)

### Community 13 - "dedupe_entities"
Cohesion: 0.20
Nodes (10): build_map(), dedupe_entities(), normalise_action(), Drop blank and duplicate entities, keeping first-seen order and casing.…, Build the placeholder -> original-value map used for re-identification. If two…, Coerce a table cell to :data:`REDACT` or :data:`KEEP`. Defaults to redact., test_dedupe_carries_the_keep_action(), test_dedupe_drops_dangerously_short_values() (+2 more)

### Community 14 - "ollama_client.py"
Cohesion: 0.07
Nodes (33): default_model(), generate(), is_up(), list_models(), missing_model_message(), OllamaError, RuntimeError, Local Ollama client — pinned to the loopback interface. Generation is the first… (+25 more)

### Community 15 - "test_review_gate.py"
Cohesion: 0.06
Nodes (52): Core logic: Ollama access, ingestion, de-identification, care notes, PHI…, blocking_reason(), build_checklist(), ChecklistItem, describe(), DocFeatures, The adaptive reviewer checklist. A checklist only works if it is short enough…, Why Approve is disabled, in one short line. Empty string means it isn't. (+44 more)

### Community 16 - "resolve_placeholder"
Cohesion: 0.29
Nodes (7): _edit_distance(), Levenshtein distance, short-circuiting once it exceeds ``cap``., Map a possibly-corrupted placeholder onto a known one. Returns the exact token…, resolve_placeholder(), Guessing between [MRN_1] and [MRN_2] would attach the wrong identity., test_ambiguous_placeholder_is_refused_not_guessed(), test_edit_distance_caps_out()

### Community 17 - "expand_name_variants"
Cohesion: 0.17
Nodes (12): expand_name_variants(), _initial_letters(), name_core(), Split a name into its parts with any leading honorific removed. "Mrs Margaret…, Initials for a name, with hyphenated components contributing each part.…, Return every plausible written form of one person's name. Covers: the full…, Dr" as a standalone form would redact every "Dr" in the document., St." must never become a bare "St" that matches clinical text. (+4 more)

### Community 18 - "Precision Preservation Cases"
Cohesion: 0.29
Nodes (7): parametrize, A bare city name used as context, not as an address, is not an identifier. "She…, test_additional_identifier_does_not_survive(), test_clinical_term_survives(), test_dosage_survives(), test_identifier_does_not_survive(), test_place_of_care_survives()

### Community 19 - "reidentify_detailed"
Cohesion: 0.33
Nodes (6): Outcome of a re-identification pass., Swap placeholders back to originals, repairing mangled tokens. Never raises on…, reidentify_detailed(), ReidentifyResult, test_invented_placeholder_is_left_alone(), test_mangled_placeholder_is_repaired()

### Community 20 - "Care Note Prompt Templates"
Cohesion: 0.50
Nodes (3): build_messages(), Care note templates. Every template shares the same hard rule: the input is…, Return ``(system, user)`` for a template label and de-identified document.

### Community 29 - "test_docx_roundtrip.py"
Cohesion: 0.06
Nodes (47): approved_map(), document_has_text_boxes(), The reviewer-approved ``{literal: placeholder}`` map for the Word pass. This is…, True if a .docx holds text this redaction pass cannot reach., apply_redactions(), _delete_prefix(), extract_text(), has_unreachable_text() (+39 more)

### Community 30 - "deidentify"
Cohesion: 0.14
Nodes (27): deidentify(), Run the full local pipeline over one document. CPU-only and offline: no model…, parametrize, Regression suite for the round-2 leaks (A1-A9). The corpus tests in…, Flattening the break made one span of the org and the next line's town., The dangerous direction: this used to fail open, leaking the whole name., Brother: David Chen\\nWei Chen" was one span covering two people., test_a_bare_number_without_a_case_label_is_left_alone() (+19 more)

### Community 33 - "test_deid_regressions.py"
Cohesion: 0.10
Nodes (27): _mrn_values(), parametrize, Regression suite for the five leaks found on a second, non-fixture document.…, A two-part capitalised phrase mid-document is not a letterhead., Layer 1 must carry this on its own — NER catching it is luck, not a guarantee., M.E.C.\\nFollow-up" must not become the name "M.E.C. Follow"., Regardless of REDACT_INPROSE_DATES, which stays False by default., The label shapes document #2 actually used, including the parenthetical. (+19 more)

### Community 34 - "test_generation.py"
Cohesion: 0.10
Nodes (23): finalise(), Re-identify a draft locally and refuse to hand back a leaky document. Returns…, check_placeholder_integrity(), Compare a draft's bracketed tokens against the placeholders it should use. An…, Local re-identification of a generated draft. Returns ``(text, unresolved)``.…, reidentify_document(), Local generation: the privacy contract, placeholder integrity, and the gate. No…, Between [MRN_1] and [MRN_2], refusing is the only safe answer. (+15 more)

### Community 35 - "carenotes.py"
Cohesion: 0.14
Nodes (14): assert_deidentified(), Backend, CareNoteError, generate_care_note(), OllamaBackend, RuntimeError, Care note generation — local, on approved de-identified text only. The contract…, Refuse to send anything carrying a value from the identity mapping. A cheap,… (+6 more)

### Community 38 - "test_stress_corpus.py"
Cohesion: 0.20
Nodes (11): _normalise(), parametrize, Corpus-driven regression net. Every document in ``stress_corpus/`` is run…, Collapse every whitespace run to one space, so line breaks stop mattering., A document listed in the key but missing on disk would silently pass., Whatever the sweep still flags must not be a structured identifier. A surviving…, _redacted(), test_clinical_content_is_preserved() (+3 more)

### Community 40 - "generate_document"
Cohesion: 0.18
Nodes (12): generate_document(), Stream a drafted document from approved de-identified text. ``phi_values`` is…, Spot-check the instruction is honoured, with the model mocked., Captures exactly what generation handed the model., A bug upstream must crash here, not send quietly., `phi_values` exists to assert absence, never to be forwarded., RecordingBackend, test_absent_fields_come_back_as_not_documented() (+4 more)

### Community 41 - "merge_spans"
Cohesion: 0.18
Nodes (11): _collapse_facility_subsets(), _collapse_person_subsets(), merge_spans(), protected_ranges(), Drop a person entity whose name is contained in a longer one. NER returns…, Drop a facility whose name is a short form of a longer one. The letterhead…, Resolve every layer's spans into a de-duplicated entity list. Overlaps are…, Character ranges of every allow-listed term occurrence in ``text``. (+3 more)

### Community 42 - "conftest.py"
Cohesion: 0.24
Nodes (9): deid(), ner_available(), fixture, Shared pytest fixtures. The spaCy model load costs several seconds, so the…, The full pipeline's output for the fixture document., True when a spaCy model loaded — layer 2 tests skip without one., raw_text(), redacted() (+1 more)

### Community 43 - "analyze"
Cohesion: 0.24
Nodes (10): analyze(), flatten_lines(), gliner_spans(), ner_spans(), Layer 2: Presidio/spaCy detections, mapped onto CareScribe entity types.…, Layer 3: GLiNER detections, or an empty list when it isn't installed., Run every enabled layer over ``text`` and return reviewable entities. Each…, One detection, in character offsets over the source text. (+2 more)

### Community 44 - "refine_document"
Cohesion: 0.25
Nodes (9): load_prompt(), Revise an existing draft against a follow-up instruction. Operates on the same…, Read one prompt file from ``carescribe/prompts``., The shared preamble — role, anti-fabrication rules, placeholder rules., refine_document(), system_prompt(), test_refinement_carries_the_running_history(), test_refinement_needs_a_draft_and_an_instruction() (+1 more)

### Community 45 - "canonical_person_key"
Cohesion: 0.22
Nodes (9): canonical_person_key(), keys_are_compatible(), A stable identity key for one person: full given name plus surname. This…, True if two canonical keys can denote the same person. Exact match, or one side…, test_canonical_key_separates_two_people_with_one_surname(), test_canonical_key_unifies_the_forms_of_one_person(), test_a_shared_surname_is_not_a_shared_identity(), test_an_initial_can_stand_in_for_a_given_name() (+1 more)

### Community 46 - "render_prompt"
Cohesion: 0.25
Nodes (8): Build the user prompt for one template with the source text embedded., render_prompt(), parametrize, test_an_unknown_template_is_refused(), test_each_template_renders_a_well_formed_prompt(), test_no_real_identifier_reaches_the_backend(), test_the_custom_template_carries_the_clinicians_own_format(), test_the_custom_template_needs_instructions()

### Community 47 - "load_protected_terms"
Cohesion: 0.29
Nodes (8): _build_protected_pattern(), load_protected_terms(), Path, Pattern, Read the editable allow-list. Blank lines and ``#`` comments are ignored., Re-read the allow-list from disk (the file is meant to be edited by hand)., reload_protected_terms(), test_the_allow_list_is_an_editable_file()

### Community 48 - "get_analyzer"
Cohesion: 0.25
Nodes (8): engine_status(), get_analyzer(), get_gliner(), Return the shared Presidio analyzer, or ``None`` if it can't be built. First…, Return the shared GLiNER model, or ``None`` if it isn't available. Guarded end…, Report which layers are live, for the sidebar. Loads nothing by itself., Load every enabled engine now, so the first document isn't the slow one., warm_up()

### Community 49 - "structured_spans"
Cohesion: 0.25
Nodes (8): _header_footer_bounds(), _is_staff_context(), _plausible_surname(), Character ranges of the document's opening and closing lines., True if an initial+surname sits somewhere that vouches for it being staff.…, True if the trailing token of an initial+surname reads like a real name.…, Layer 1: deterministic regex detections over ``text``., structured_spans()

### Community 50 - "_span_is_plausible"
Cohesion: 0.25
Nodes (8): _is_acronym(), _location_is_address(), _looks_clinical(), True if a LOCATION span is part of a postal address, not a bare place name. "14…, Reject the false positives NER reliably produces on clinical documents., True for a short all-caps token like "ECG" or "LS9" — never a name here., True if the value is a known clinical abbreviation or a drug name., _span_is_plausible()

### Community 51 - "_line_bounds"
Cohesion: 0.33
Nodes (7): classify_person(), _is_labelled_date_field(), _line_bounds(), True if ``start`` sits within three lines of a NEXT OF KIN-style heading., Decide whether a detected name is a clinician, a relative, or the patient.…, True if the date sits in a labelled field ("Admission date: 11 May 2026")., _under_relative_heading()

### Community 52 - "Stress corpus"
Cohesion: 0.40
Nodes (4): Running it, Stress corpus, The answer key, What each document covers

### Community 53 - "with_banner"
Cohesion: 0.50
Nodes (4): Prepend the review banner, without duplicating one already there., with_banner(), test_every_draft_carries_the_review_banner(), test_the_banner_is_not_duplicated_on_refinement()

### Community 54 - "_collapse_person_identities"
Cohesion: 0.50
Nodes (4): _collapse_person_identities(), True for a person row whose role is known (patient / relative / clinician)., Collapse every written form of one person onto a single entity row.…, _specific_person_type()

### Community 55 - "stress_report.py"
Cohesion: 0.67
Nodes (3): main(), normalise(), Per-document pass/fail report for the stress corpus. python…

### Community 56 - "test_a_date_entity_never_spans_a_line_break"
Cohesion: 0.33
Nodes (4): 14 June 2026\\nDate" swallowed the next line's label and mangled the text., The precision guard that keeps clinical context intact., test_a_date_entity_never_spans_a_line_break(), test_place_of_care_in_prose_still_survives()

## Knowledge Gaps
- **5 isolated node(s):** `What each document covers`, `The answer key`, `Running it`, `Longest-match-wins Overlap Resolution`, `Person Typing From Context`
  These have ≤1 connection - possible missing edges or undocumented components.
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `deidentify()` connect `deidentify` to `deidentify.py`, `batch.py`, `No-NER Fallback Path`, `test_deid_regressions.py`, `app.py`, `test_stress_corpus.py`, `rebuild`, `redact`, `conftest.py`, `analyze`, `residual_scan`, `dedupe_entities`, `ollama_client.py`, `test_deid_pipeline.py`, `stress_report.py`, `test_a_date_entity_never_spans_a_line_break`, `test_a_patient_label_outranks_a_kinship_heading`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `Document` connect `app.py` to `batch.py`, `test_generation.py`, `test_app.py`, `test_review_gate.py`, `test_docx_roundtrip.py`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `residual_scan()` connect `residual_scan` to `deidentify.py`, `batch.py`, `extract_text`, `test_stress_corpus.py`, `merge_spans`, `analyze`, `ollama_client.py`, `structured_spans`, `_span_is_plausible`, `stress_report.py`, `test_docx_roundtrip.py`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Document` (e.g. with `apply_redactions()` and `extract_text()`) actually correct?**
  _`Document` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `extract_text()` (e.g. with `pdfplumber` and `python-docx`) actually correct?**
  _`extract_text()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `What each document covers`, `The answer key`, `Running it` to the rest of the system?**
  _5 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `batch.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06140350877192982 - nodes in this community are weakly interconnected._