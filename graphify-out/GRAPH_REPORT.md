# Graph Report - medgpt  (2026-08-21)

## Corpus Check
- 72 files · ~82,644 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1364 nodes · 2503 edges · 111 communities (72 shown, 39 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 40 edges (avg confidence: 0.77)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e9312e13`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- clinical_forms.py
- test_deid_regressions.py
- test_review_gate.py
- Generation backend selection order (Ollama > built-in GGUF > Cloud)
- Reference: verified template structure
- CareNoteError
- test_docx_roundtrip.py
- test_app.py
- load_protected_terms
- test_generation.py
- extract_text
- desktop.py
- test_generation_setup.py
- mapping.py
- test_mapping.py
- ollama_client.py
- deidentify.py
- backends.py
- deidentify
- carenotes.py
- _span_is_plausible
- candidate_residuals
- residual_scan
- rebuild
- review_spans
- generation_status
- conftest.py
- analyze
- merge_spans
- RecordingBackend
- structured_spans
- Architecture
- test_stress_corpus.py
- combine_sources
- assert_deidentified
- get_analyzer
- test_desktop_packaging.py
- make_icon.py
- expand_name_variants
- test_the_whole_deid_path_works_with_no_model_at_all
- RuntimeError
- README.md
- generate_document
- batch.py
- fixture
- test_highlight_review_component.py
- run_app.py
- canonical_person_key
- resolve_placeholder
- ram_verdict
- OllamaBackend
- test_a_date_entity_never_spans_a_line_break
- test_no_clinical_acronym_became_an_entity
- Path
- Report templates (SOAP / GP letter / discharge / custom)
- Outpatient Respiratory Clinic Letter (doc03)
- _build_analyzer
- Reference: verified against the real codebase
- test_ner_layer_finds_a_name_mid_paragraph
- carenotes_prompt.py
- Ward 7B Nursing Handover (doc04)
- test_two_layers_agreeing_is_auto_confidence
- test_generation_status_is_cached
- test_clinical_form_templates.py
- carescribe/__init__.py
- deid_prompt.py
- prompts/__init__.py
- build_dmg.sh
- build_macos.sh
- rthook_carescribe.py
- tests/__init__.py
- run_all.py
- Any
- Any
- test_nothing_downloads_on_import_or_launch
- Exception
- Jordan Whitfield (fictional test client)
- parametrize
- assign_placeholders
- Pattern
- GLiNER Deliberately Uninstalled
- normalise_type
- Sample Source Documents README
- Recurring fictional staff roster (e.g. A. Whitfield) across documents
- Lightweight review UX for de-identification — design
- test_deid_pipeline.py
- normalise_action
- test_a_patient_label_outranks_a_kinship_heading
- NoEgress
- parametrize
- _fresh_generation_status_cache
- applog.py
- test_in_prose_clinical_date_survives_by_default
- test_identity_anchored_dates_are_still_redacted
- Path
- RuntimeError
- test_structured_layer_stands_alone
- redact
- reidentify
- test_mrn_needs_a_label
- test_pipeline_runs_without_ner
- components/__init__.py
- test_pipeline_is_deterministic
- test_a_single_layer_ner_only_hit_needs_review
- test_nhs_number_gone_in_every_spacing
- test_line_broken_name_collapses_to_one_placeholder
- test_medication_block_is_untouched
- parametrize

## God Nodes (most connected - your core abstractions)
1. `deidentify()` - 66 edges
2. `get_form_spec()` - 30 edges
3. `residual_scan()` - 24 edges
4. `generation_status()` - 23 edges
5. `generate_document()` - 22 edges
6. `load_documents()` - 20 edges
7. `write_approved()` - 19 edges
8. `structured_spans()` - 19 edges
9. `extract_text()` - 18 edges
10. `candidate_residuals()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `Stable per-entity placeholder scheme` --semantically_similar_to--> `build_prompt()`  [INFERRED] [semantically similar]
  README.md → carescribe/core/clinical_forms.py
- `presidio-analyzer` --references--> `_build_analyzer()`  [INFERRED]
  requirements.txt → carescribe/core/deidentify.py
- `spaCy Model Fallback Chain` --rationale_for--> `_build_analyzer()`  [INFERRED]
  requirements.txt → carescribe/core/deidentify.py
- `pdfplumber` --references--> `extract_text()`  [INFERRED]
  requirements.txt → carescribe/core/ingest.py
- `python-docx` --references--> `extract_text()`  [INFERRED]
  requirements.txt → carescribe/core/ingest.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **README report-templates table implemented by prompt files** — readme_report_templates, carescribe_prompts_care_notes_soap_template, carescribe_prompts_clinic_letter_template, carescribe_prompts_discharge_summary_template, carescribe_prompts_custom_template [INFERRED 0.85]
- **Privacy-invariant enforcement chain (assert, sweep, write, integrity)** — carescribe_core_carenotes_assert_deidentified, carescribe_core_deidentify_residual_scan, carescribe_core_batch_write_approved, carescribe_core_mapping_check_placeholder_integrity [EXTRACTED 1.00]
- **Clinical form generation pipeline (combine -> prompt -> generate -> parse -> fill)** — carescribe_core_clinical_forms_combine_sources, carescribe_core_clinical_forms_build_prompt, carescribe_core_clinical_forms_generate_form_document, carescribe_core_clinical_forms_parse_fields, carescribe_core_clinical_forms_fill_template [EXTRACTED 1.00]
- **Sample docs that combine into one fictional client's clinical-forms test flow** — sample_documents_readme_01_gp_referral_letter, sample_documents_readme_02_biopsychosocial_intake_notes, sample_documents_readme_03_session_log_progress_notes, sample_documents_readme_04_treatment_review_source, sample_documents_readme_jordan_whitfield [EXTRACTED 1.00]
- **Fictional patients sharing the same reused NHS number across documents** — stress_corpus_doc01_mohammed_al_rashid, stress_corpus_doc02_margaret_elizabeth_chen, stress_corpus_doc05_elspeth_mackenzie_ford, stress_corpus_doc06_priya_venkataraman, stress_corpus_doc09_tomasz_wisniewski, stress_corpus_shared_nhs_number [INFERRED 0.85]
- **Documents sharing the recurring fictional staff roster (e.g. A. Whitfield, R. Patel)** — stress_corpus_doc01_community_mh_letter, stress_corpus_doc02_cardiology_discharge, stress_corpus_doc04_ward_handover, stress_corpus_doc07_cmht_family_review, stress_corpus_doc10_mha_assessment, stress_corpus_recurring_staff_roster [INFERRED 0.75]

## Communities (111 total, 39 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.05
Nodes (80): _as_docx(), current(), document_flags(), documents(), _draft_state(), entity_confirmed(), entity_frame(), flag_dismissals() (+72 more)

### Community 1 - "clinical_forms.py"
Cohesion: 0.06
Nodes (74): available_forms(), _biopsychosocial_spec(), build_prompt(), _clear_cell(), ClinicalFormError, _dedupe_row(), _fill_cell(), _fill_cell_after_label() (+66 more)

### Community 2 - "test_deid_regressions.py"
Cohesion: 0.10
Nodes (27): _mrn_values(), parametrize, Regression suite for the five leaks found on a second, non-fixture document.…, A two-part capitalised phrase mid-document is not a letterhead., Layer 1 must carry this on its own — NER catching it is luck, not a guarantee., M.E.C.\\nFollow-up" must not become the name "M.E.C. Follow"., Regardless of REDACT_INPROSE_DATES, which stays False by default., The label shapes document #2 actually used, including the parenthetical. (+19 more)

### Community 3 - "test_review_gate.py"
Cohesion: 0.11
Nodes (20): blocking_reason(), The approval gate. Approval unlocks once nothing is outstanding: the blocking…, Why Approve is disabled, in one short line. Empty string means it isn't., fixture, _flag_values(), The reviewer gate: candidate highlighting, the adaptive checklist, and the no-…, The real test: nothing the corpus calls an identifier may appear., A dismissal key holds the span text, so it must be wiped with the rest. (+12 more)

### Community 4 - "Generation backend selection order (Ollama > built-in GGUF > Cloud)"
Cohesion: 0.18
Nodes (11): core/model_setup.py (model download, isolated), packaging/build_macos.sh, packaging/build_windows.ps1, packaging/carescribe.iss (Inno Setup script), packaging/make_icon.py, The desktop app (PyInstaller packaging), Generation backend selection order (Ollama > built-in GGUF > Cloud), run_app.py entry point (+3 more)

### Community 5 - "Reference: verified template structure"
Cohesion: 0.10
Nodes (20): carescribe/core/clinical_forms.py (module), Refine prompt (clinical form, marker-preserving), Refine prompt (free-form draft revision), Clinical Form Generation (APS Templates) Implementation Plan, Global Constraints, Reference: verified template structure, Self-Review Notes (for the implementer), Task 10: End-to-end generation glue (`generate_form_document`, `refine_form_document`, `render_preview`) (+12 more)

### Community 6 - "CareNoteError"
Cohesion: 0.20
Nodes (10): CareNoteError, load_prompt(), RuntimeError, Build the user prompt for one template with the source text embedded., Raised when care note generation can't proceed., Read one prompt file from ``carescribe/prompts``., render_prompt(), test_an_unknown_template_is_refused() (+2 more)

### Community 7 - "test_docx_roundtrip.py"
Cohesion: 0.06
Nodes (53): approved_map(), document_has_text_boxes(), The reviewer-approved ``{literal: placeholder}`` map for the Word pass. This is…, Redact the original .docx into the output folder, structure preserved. The same…, True if a .docx holds text this redaction pass cannot reach., write_approved_docx(), apply_redactions(), _delete_prefix() (+45 more)

### Community 8 - "test_app.py"
Cohesion: 0.09
Nodes (47): AppTest, Document, One document's state for the whole review pass. Everything here except…, build_intake_notes(), build_referral_letter(), build_session_log(), build_treatment_review_source(), _grid_table() (+39 more)

### Community 9 - "load_protected_terms"
Cohesion: 0.29
Nodes (7): _build_protected_pattern(), load_protected_terms(), Pattern, Read the editable allow-list. Blank lines and ``#`` comments are ignored., Re-read the allow-list from disk (the file is meant to be edited by hand)., reload_protected_terms(), test_the_allow_list_is_an_editable_file()

### Community 10 - "test_generation.py"
Cohesion: 0.10
Nodes (23): finalise(), Re-identify a draft locally and refuse to hand back a leaky document. Returns…, check_placeholder_integrity(), Compare a draft's bracketed tokens against the placeholders it should use. An…, Local re-identification of a generated draft. Returns ``(text, unresolved)``.…, reidentify_document(), Local generation: the privacy contract, placeholder integrity, and the gate. No…, Between [MRN_1] and [MRN_2], refusing is the only safe answer. (+15 more)

### Community 11 - "extract_text"
Cohesion: 0.09
Nodes (33): Any, _extract_docx(), _extract_pdf(), extract_text(), _extract_txt(), IngestError, RuntimeError, Text extraction for uploaded documents (PDF / DOCX / TXT). Nothing here writes… (+25 more)

### Community 12 - "desktop.py"
Cohesion: 0.14
Nodes (24): app_data_dir(), bundle_root(), ensure_dirs(), find_local_model(), is_frozen(), models_dir(), output_dir(), Path (+16 more)

### Community 13 - "test_generation_setup.py"
Cohesion: 0.09
Nodes (13): mapping_module(), First-run generation setup: never an empty panel, and the egress line held. The…, The one outbound path must not be reachable from the de-id flow., `state` held the draft dict, then the backend dict overwrote it. The draft dict…, The canonical shape of a document's generated-draft state., Renamed from `state` so the collision cannot recur., test_a_missing_model_in_a_frozen_build_says_so(), test_a_truncated_download_is_rejected() (+5 more)

### Community 14 - "mapping.py"
Cohesion: 0.12
Nodes (20): expand_facility_variants(), find_known_as(), find_spans(), _form_pattern(), Issue, Pattern, In-memory PII <-> placeholder mapping. This module is deliberately pure: it…, Return the full organisation name plus short forms. "St. Aidan's General… (+12 more)

### Community 15 - "test_mapping.py"
Cohesion: 0.20
Nodes (10): dedupe_entities(), Drop blank and duplicate entities, keeping first-seen order and casing.…, Mapping-layer checks: type normalisation, surface forms, and re-identification.…, If ANY occurrence of a value was low-confidence, the whole entity is., test_dedupe_carries_the_keep_action(), test_dedupe_drops_dangerously_short_values(), test_dedupe_entities_defaults_missing_confidence_to_review(), test_dedupe_entities_keeps_confidence() (+2 more)

### Community 16 - "ollama_client.py"
Cohesion: 0.06
Nodes (47): Option A. The only outbound request the app makes, on an explicit click., run_model_download(), clear_partial_download(), download_model(), _free_bytes(), is_model_present(), model_destination(), ModelSetupError (+39 more)

### Community 17 - "deidentify.py"
Cohesion: 0.20
Nodes (12): date_span_wanted(), _has_contact_anchor(), _has_identity_anchor(), _is_clinical_measurement(), _looks_like_calendar_date(), Layered, CPU-only de-identification. No network, no GPU, no LLM. Every layer…, True if a real date sits in an appointment or contact clause., True if a date-shaped span is really a dosage or lab value. (+4 more)

### Community 18 - "backends.py"
Cohesion: 0.18
Nodes (16): privacy_indicator(), A persistent, honest statement of where data goes. It must change when cloud…, cloud_enabled(), cloud_key_present(), cloud_provider(), describe_backends(), Generation backends, layered so the app works with nothing installed. Selection…, The configured provider name, or "" when cloud generation is off. (+8 more)

### Community 19 - "deidentify"
Cohesion: 0.14
Nodes (27): deidentify(), Run the full local pipeline over one document. CPU-only and offline: no model…, parametrize, Regression suite for the round-2 leaks (A1-A9). The corpus tests in…, Flattening the break made one span of the org and the next line's town., The dangerous direction: this used to fail open, leaking the whole name., Brother: David Chen\\nWei Chen" was one span covering two people., test_a_bare_number_without_a_case_label_is_left_alone() (+19 more)

### Community 20 - "carenotes.py"
Cohesion: 0.16
Nodes (12): Backend, generate_care_note(), Care note generation — local, on approved de-identified text only. The contract…, Prepend the review banner, without duplicating one already there., Draft a care note from ALREADY DE-IDENTIFIED text, returning it whole. The…, One method wide: the seam a different provider would be swapped in at., template_names(), with_banner() (+4 more)

### Community 21 - "_span_is_plausible"
Cohesion: 0.15
Nodes (15): classify_person(), _is_acronym(), _is_labelled_date_field(), _line_bounds(), _location_is_address(), _looks_clinical(), True for a short all-caps token like "ECG" or "LS9" — never a name here., True if the value is a known clinical abbreviation or a drug name. (+7 more)

### Community 22 - "candidate_residuals"
Cohesion: 0.13
Nodes (18): candidate_residuals(), Flag, _is_common(), outstanding(), _placeholder_ranges(), Residual-candidate highlighter — where the reviewer's eye should go first. This…, One span worth a second look, with its offsets in the redacted text., Identity for dismissal — per value, so one decision covers repeats. (+10 more)

### Community 23 - "residual_scan"
Cohesion: 0.20
Nodes (10): Re-scan ALREADY-REDACTED text for anything that still looks identifying. Runs…, residual_scan(), Placeholders are the point of the exercise, not leaks., A .txt file read off a Windows disk arrives with CRLF endings. NER tokenises…, test_crlf_and_lf_documents_behave_identically(), test_residual_scan_catches_a_leaked_name(), test_residual_scan_catches_a_leaked_structured_identifier(), test_residual_scan_does_not_flag_placeholders() (+2 more)

### Community 24 - "rebuild"
Cohesion: 0.11
Nodes (20): add_manual_entity(), DeidentificationError, DeidResult, Re-derive redacted text and the PHI map from a reviewer-edited table. Called…, Add an identifier the tools missed and immediately re-redact. The new value…, Raised when de-identification can't run at all., Everything the de-identification stage produces for one document., rebuild() (+12 more)

### Community 25 - "review_spans"
Cohesion: 0.20
Nodes (18): _entity_spans(), Unifies the two things a reviewer might still need to act on in one document's…, Every clickable span in ``redacted_text``, in reading order. ``confirmed`` is…, One clickable span in a document's redacted text., Placeholder occurrences for low-confidence, not-yet-confirmed entities., _residual_spans(), review_spans(), ReviewSpan (+10 more)

### Community 26 - "generation_status"
Cohesion: 0.15
Nodes (14): cache_data, generation_status(), _llama_runtime_available(), missing_reason(), Is generation usable right now, and if not, what should the user do? Kept…, One plain sentence on why generation is not available yet., Which generation backends are usable at this moment., Which backend would actually be used, matching the backend ladder. (+6 more)

### Community 27 - "conftest.py"
Cohesion: 0.15
Nodes (14): deid(), ner_available(), fixture, Shared pytest fixtures. The spaCy model load costs several seconds, so the…, The full pipeline's output for the fixture document., True when a spaCy model loaded — layer 2 tests skip without one., raw_text(), redacted() (+6 more)

### Community 28 - "analyze"
Cohesion: 0.22
Nodes (11): analyze(), flatten_lines(), gliner_spans(), ner_spans(), Layer 2: Presidio/spaCy detections, mapped onto CareScribe entity types.…, Layer 3: GLiNER detections, or an empty list when it isn't installed., Run every enabled layer over ``text`` and return reviewable entities. Each…, One detection, in character offsets over the source text. (+3 more)

### Community 29 - "merge_spans"
Cohesion: 0.14
Nodes (14): _collapse_facility_subsets(), _collapse_person_identities(), _collapse_person_subsets(), merge_spans(), protected_ranges(), Shrink a NER span to its identifying core. Drops leading titles ("Sister Fiona…, Drop a person entity whose name is contained in a longer one. NER returns…, True for a person row whose role is known (patient / relative / clinician). (+6 more)

### Community 30 - "RecordingBackend"
Cohesion: 0.19
Nodes (13): Revise an existing draft against a follow-up instruction. Operates on the same…, The shared preamble — role, anti-fabrication rules, placeholder rules., refine_document(), system_prompt(), Captures exactly what generation handed the model., RecordingBackend, test_generate_document_default_behaviour_is_unchanged(), test_refine_document_accepts_a_system_and_refine_prompt_override() (+5 more)

### Community 31 - "structured_spans"
Cohesion: 0.14
Nodes (14): _header_footer_bounds(), _is_staff_context(), _plausible_surname(), Character ranges of the document's opening and closing lines., True if an initial+surname sits somewhere that vouches for it being staff.…, True if the trailing token of an initial+surname reads like a real name.…, Layer 1: deterministic regex detections over ``text``., REDACT_INPROSE_DATES flag (+6 more)

### Community 32 - "Architecture"
Cohesion: 0.13
Nodes (14): 1. Template assets, 2. Form spec extraction, 3. Header fields (practitioner-entered), 4. Multi-document source combination, 5. Generation, 6. Review, 7. Export, 8. UI (`app.py`, Step 5) (+6 more)

### Community 33 - "test_stress_corpus.py"
Cohesion: 0.15
Nodes (16): parametrize, test_each_flag_carries_its_kind_and_reason(), test_the_sidecar_contains_no_identifier_value(), _entities(), _normalise(), Corpus-driven regression net. Every document in ``stress_corpus/`` is run…, Confidence tiering must never make the reviewer's job LESS safe. An "auto"…, Whatever the sweep still flags must not be a structured identifier. A surviving… (+8 more)

### Community 34 - "combine_sources"
Cohesion: 0.21
Nodes (13): combine_sources(), Concatenate several documents' de-identified text into one source. ``sources``…, Regression test for Finding 3: raw filename must not leak into model-facing…, Regression test for Finding 1: cap at 26 documents (A-Z)., Regression test for Finding 1: prefixed placeholders must match PLACEHOLDER_RE.…, Regression test for Finding 2: text and map rewrites must be consistent. A…, test_combine_sources_no_filename_in_output(), test_combine_sources_non_standard_placeholder_consistency() (+5 more)

### Community 35 - "assert_deidentified"
Cohesion: 0.20
Nodes (12): assert_deidentified(), CloudBackend (unwired seam), Refuse to send anything carrying a value from the identity mapping. A cheap,…, System prompt (anti-fabrication rules), Optional cloud generation path (off by default), Two required env vars (CARESCRIBE_CLOUD_PROVIDER / CARESCRIBE_CLOUD_API_KEY), CareScribe practitioner one-page guide, CareScribe (the application) (+4 more)

### Community 36 - "get_analyzer"
Cohesion: 0.20
Nodes (11): cache_resource, load_detection_engine(), Load the NER model once per session, not once per rerun. Streamlit re-runs the…, engine_status(), get_analyzer(), get_gliner(), Return the shared Presidio analyzer, or ``None`` if it can't be built. First…, Return the shared GLiNER model, or ``None`` if it isn't available. Guarded end… (+3 more)

### Community 37 - "test_desktop_packaging.py"
Cohesion: 0.12
Nodes (13): CloudBackend, A remote provider, reachable only when explicitly configured. Receives approved…, _cloud_off(), fixture, The packaging invariants: what the desktop app may and may not do. Packaging is…, A key left by another tool must not silently turn on off-device work., It must not quietly fall back to a local backend and look like it worked., No key may be committed, defaulted, or written anywhere. (+5 more)

### Community 38 - "make_icon.py"
Cohesion: 0.29
Nodes (12): Image, _load_font(), main(), Path, Generate CareScribe's placeholder icon. A real icon is a design job; this…, The first usable bold face, or ``None`` if none of them load., A rounded square with "CS" centred on it., macOS only. Silently skipped elsewhere — the .app is built on a Mac. (+4 more)

### Community 39 - "expand_name_variants"
Cohesion: 0.17
Nodes (12): expand_name_variants(), _initial_letters(), name_core(), Split a name into its parts with any leading honorific removed. "Mrs Margaret…, Initials for a name, with hyphenated components contributing each part.…, Return every plausible written form of one person's name. Covers: the full…, Dr" as a standalone form would redact every "Dr" in the document., St." must never become a bare "St" that matches clinical text. (+4 more)

### Community 40 - "test_the_whole_deid_path_works_with_no_model_at_all"
Cohesion: 0.40
Nodes (5): _nothing_available(), A fresh PC must still de-identify, review and approve., A fresh PC: no Ollama, no model file, no cloud., test_cloud_alone_counts_as_ready(), test_the_whole_deid_path_works_with_no_model_at_all()

### Community 42 - "README.md"
Cohesion: 0.06
Nodes (37): answer_key.json, Community MH Discharge Letter (doc01), Mohammed Al-Rashid ('Mo'), Cardiology Discharge Summary (doc02), Margaret Elizabeth Chen ('Peggy'), Elspeth Mackenzie-Ford ('Ellie'), GP Referral Letter (doc05), Priya Venkataraman (+29 more)

### Community 43 - "generate_document"
Cohesion: 0.15
Nodes (13): generate_document(), Stream a drafted document from approved de-identified text. ``phi_values`` is…, parametrize, Spot-check the instruction is honoured, with the model mocked., A bug upstream must crash here, not send quietly., `phi_values` exists to assert absence, never to be forwarded., test_absent_fields_come_back_as_not_documented(), test_each_template_renders_a_well_formed_prompt() (+5 more)

### Community 44 - "batch.py"
Cohesion: 0.05
Nodes (63): analyze_document(), approved_docx_path(), approved_path(), BatchError, _default_output_dir(), list_folder(), load_documents(), Batch input and approved-output handling. The single module in CareScribe that… (+55 more)

### Community 46 - "test_highlight_review_component.py"
Cohesion: 0.27
Nodes (8): highlight_review(), Click-to-redact highlighted text. Renders already-redacted (or already-flagged)…, Render ``html`` and return the ``data-span-id`` of the last click. Returns…, _frontend_path(), Offline-first: nothing in this file may fetch from a CDN., test_frontend_file_exists(), test_frontend_has_no_external_script_or_link_tags(), test_wrapper_is_callable_and_importable()

### Community 47 - "run_app.py"
Cohesion: 0.16
Nodes (17): Popen, close_splash(), _fatal(), free_port(), main(), _no_window_kwargs(), CareScribe desktop launcher — the app's entry point. Starts the Streamlit…, Dismiss the bootloader splash, if this is a frozen build that has one.… (+9 more)

### Community 48 - "canonical_person_key"
Cohesion: 0.22
Nodes (9): canonical_person_key(), keys_are_compatible(), A stable identity key for one person: full given name plus surname. This…, True if two canonical keys can denote the same person. Exact match, or one side…, test_canonical_key_separates_two_people_with_one_surname(), test_canonical_key_unifies_the_forms_of_one_person(), test_a_shared_surname_is_not_a_shared_identity(), test_an_initial_can_stand_in_for_a_given_name() (+1 more)

### Community 49 - "resolve_placeholder"
Cohesion: 0.29
Nodes (7): _edit_distance(), Levenshtein distance, short-circuiting once it exceeds ``cap``., Map a possibly-corrupted placeholder onto a known one. Returns the exact token…, resolve_placeholder(), Guessing between [MRN_1] and [MRN_2] would attach the wrong identity., test_ambiguous_placeholder_is_refused_not_guessed(), test_edit_distance_caps_out()

### Community 50 - "ram_verdict"
Cohesion: 0.33
Nodes (6): available_ram_gb(), ram_verdict(), Total system RAM in GB, or 0.0 if it cannot be determined., Whether this machine can run the bundled local model. Returns a verdict rather…, test_a_capable_laptop_gets_no_warning(), test_a_weak_laptop_gets_a_warning_not_a_crash()

### Community 51 - "OllamaBackend"
Cohesion: 0.17
Nodes (10): BackendError, LocalGGUFBackend, RuntimeError, Raised when a backend cannot be used, with the fix in the message., CPU-only generation from a bundled GGUF via ``llama-cpp-python``. The model is…, True if the runtime and a model file are both present., OllamaBackend, Local generation through the loopback-pinned Ollama daemon. (+2 more)

### Community 52 - "test_a_date_entity_never_spans_a_line_break"
Cohesion: 0.33
Nodes (4): 14 June 2026\\nDate" swallowed the next line's label and mangled the text., The precision guard that keeps clinical context intact., test_a_date_entity_never_spans_a_line_break(), test_place_of_care_in_prose_still_survives()

### Community 55 - "Report templates (SOAP / GP letter / discharge / custom)"
Cohesion: 0.40
Nodes (5): SOAP care note prompt template, GP clinic letter prompt template, Custom (clinician house format) prompt template, Discharge summary prompt template, Report templates (SOAP / GP letter / discharge / custom)

### Community 56 - "Outpatient Respiratory Clinic Letter (doc03)"
Cohesion: 0.40
Nodes (5): Ngozi Okafor, Outpatient Respiratory Clinic Letter (doc03), Attendee list pattern, Header town + county pattern, Record-number label shapes (three variants)

### Community 57 - "_build_analyzer"
Cohesion: 0.29
Nodes (8): available_models(), _build_analyzer(), is_frozen_build(), Where a spaCy model package actually lives, or ``None`` if absent. Resolved…, Every spaCy model importable in this environment., Build a Presidio ``AnalyzerEngine`` over spaCy. Returns (engine, model, error)., resolve_model_path(), test_model_paths_resolve_explicitly()

### Community 58 - "Reference: verified against the real codebase"
Cohesion: 0.15
Nodes (12): Global Constraints, Lightweight Review UX Redesign Implementation Plan, Reference: verified against the real codebase, Self-Review Notes, Task 1: Confidence tiering in the detection pipeline, Task 2: Unified review-span module, Task 3: Click-to-redact custom Streamlit component, Task 4: Simplify `review_checklist.py` to a two-input gate (+4 more)

### Community 60 - "carenotes_prompt.py"
Cohesion: 0.50
Nodes (3): build_messages(), Care note templates. Every template shares the same hard rule: the input is…, Return ``(system, user)`` for a template label and de-identified document.

### Community 61 - "Ward 7B Nursing Handover (doc04)"
Cohesion: 0.50
Nodes (4): Aiden Braithwaite, Ward 7B Nursing Handover (doc04), 'A. Surname' against full name in header, Labelled date fields

### Community 64 - "test_clinical_form_templates.py"
Cohesion: 0.50
Nodes (3): parametrize, The three bundled APS templates load and match the structure this feature's…, test_bundled_template_shape()

### Community 78 - "Jordan Whitfield (fictional test client)"
Cohesion: 0.31
Nodes (9): 01_gp_referral_letter.docx, 02_biopsychosocial_intake_notes.docx, 03_session_log_progress_notes.docx, 04_treatment_review_source.docx, Biopsychosocial Assessment form, Client Session Notes form, Client Treatment Review form, Clinical-Forms Pipeline (upload -> de-identify -> approve -> combine sources -> generate form) (+1 more)

### Community 80 - "parametrize"
Cohesion: 0.29
Nodes (7): parametrize, A bare city name used as context, not as an address, is not an identifier. "She…, test_additional_identifier_does_not_survive(), test_clinical_term_survives(), test_dosage_survives(), test_identifier_does_not_survive(), test_place_of_care_survives()

### Community 81 - "assign_placeholders"
Cohesion: 0.29
Nodes (7): assign_placeholders(), Attach a stable placeholder to each unique entity. A type with exactly one…, assign_placeholders is analyze()'s last step — a silent drop here is permanent., test_assign_placeholders_keeps_confidence(), test_existing_placeholder_is_preserved(), test_multiple_values_get_numbered_placeholders(), test_single_value_gets_a_bare_placeholder()

### Community 84 - "normalise_type"
Cohesion: 0.40
Nodes (5): normalise_type(), Coerce a model-supplied type string onto the canonical list., parametrize, test_normalise_type(), test_reidentify_never_crashes()

### Community 87 - "Lightweight review UX for de-identification — design"
Cohesion: 0.14
Nodes (13): 1. Confidence tiering (drives what gets a click at all), 2. One primary review view, not three, 3. The click-to-redact component, 4. Attestation & audit trail, 5. Crash-risk fixes, Architecture, Current state (for reference), Goals (+5 more)

### Community 88 - "test_deid_pipeline.py"
Cohesion: 0.10
Nodes (13): Regression suite for the layered de-identification pipeline. Two guarantees,…, Layer 3 is optional: absent or present, it returns a list and never raises., One real value, one placeholder — the whole point of the mapping., An NHS number is Layer 1 (regex) — pattern-certain, no review needed., The map is a return value the caller holds; nothing module-level keeps it., Dr Patel", "Dr Raj Patel" and a bare "Patel" are one person, one placeholder., test_a_structured_regex_hit_is_auto_confidence(), test_analyze_returns_nothing_for_empty_text() (+5 more)

### Community 89 - "normalise_action"
Cohesion: 0.40
Nodes (5): build_map(), normalise_action(), Build the placeholder -> original-value map used for re-identification. If two…, Coerce a table cell to :data:`REDACT` or :data:`KEEP`. Defaults to redact., test_kept_rows_are_absent_from_the_map()

### Community 91 - "NoEgress"
Cohesion: 0.14
Nodes (10): NoEgress, Fails the test if anything opens a non-loopback socket. Loopback is allowed:…, Re-identification is pure Python — it must not phone anywhere., test_reidentification_opens_no_socket(), The load that used to hang on a captive portal must not exist., Reset the cache so the guard covers a genuine first load., The reported hang: no model, so something tries to download it., test_a_missing_model_fails_loudly_instead_of_fetching() (+2 more)

### Community 93 - "_fresh_generation_status_cache"
Cohesion: 0.50
Nodes (4): _cloud_off(), _fresh_generation_status_cache(), fixture, generation_status() is now @st.cache_data(ttl=5) — a process-global cache keyed…

### Community 94 - "applog.py"
Cohesion: 0.13
Nodes (19): BaseException, ensure_engine_ready(), Load the model at startup, behind a visible spinner. Deliberately not lazy. If…, The last line of defence: a calm message instead of a stack trace. A clinician…, render_unexpected_error(), exception(), get_logger(), log() (+11 more)

### Community 102 - "redact"
Cohesion: 0.33
Nodes (6): Replace every surface form of every entity with its placeholder. Replacement…, redact(), Form tokens are joined with \\s+, so a name split across lines still matches., test_longest_match_wins_on_overlap(), test_matcher_does_not_fire_inside_a_longer_word(), test_matcher_tolerates_a_line_break()

### Community 104 - "reidentify"
Cohesion: 0.18
Nodes (11): Outcome of a re-identification pass., Swap placeholders back to originals, repairing mangled tokens. Never raises on…, Swap placeholders back to their original values. Thin wrapper over…, reidentify(), reidentify_detailed(), ReidentifyResult, test_empty_map_is_a_no_op(), test_invented_placeholder_is_left_alone() (+3 more)

## Ambiguous Edges - Review These
- `README.md` → `Psychological Medicine Clinic Letter (doc06)`  [AMBIGUOUS]
  stress_corpus/README.md · relation: references
- `README.md` → `CMHT Family Review Letter (doc07)`  [AMBIGUOUS]
  stress_corpus/README.md · relation: references
- `README.md` → `Resource Centre Referral (doc08)`  [AMBIGUOUS]
  stress_corpus/README.md · relation: references
- `README.md` → `Crisis Team Contact Log (doc09)`  [AMBIGUOUS]
  stress_corpus/README.md · relation: references
- `README.md` → `Mental Health Act Assessment Record (doc10)`  [AMBIGUOUS]
  stress_corpus/README.md · relation: references

## Knowledge Gaps
- **90 isolated node(s):** `Global Constraints`, `Task 1: Confidence tiering in the detection pipeline`, `Task 2: Unified review-span module`, `Task 3: Click-to-redact custom Streamlit component`, `Task 4: Simplify `review_checklist.py` to a two-input gate` (+85 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **39 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `README.md` and `Psychological Medicine Clinic Letter (doc06)`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `README.md` and `CMHT Family Review Letter (doc07)`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `README.md` and `Resource Centre Referral (doc08)`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `README.md` and `Crisis Team Contact Log (doc09)`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `README.md` and `Mental Health Act Assessment Record (doc10)`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `deidentify()` connect `deidentify` to `test_deid_regressions.py`, `test_app.py`, `test_generation_setup.py`, `mapping.py`, `deidentify.py`, `residual_scan`, `rebuild`, `conftest.py`, `analyze`, `test_stress_corpus.py`, `README.md`, `batch.py`, `test_a_date_entity_never_spans_a_line_break`, `test_deid_pipeline.py`, `normalise_action`, `test_a_patient_label_outranks_a_kinship_heading`, `NoEgress`, `applog.py`, `redact`, `test_pipeline_runs_without_ner`, `test_pipeline_is_deterministic`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `Clinical Form Generation (APS Templates) Implementation Plan` connect `Reference: verified template structure` to `assert_deidentified`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._