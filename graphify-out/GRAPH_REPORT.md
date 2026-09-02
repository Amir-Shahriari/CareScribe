# Graph Report - medgpt  (2026-09-02)

## Corpus Check
- 168 files · ~140,165 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2318 nodes · 4477 edges · 140 communities (117 shown, 23 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 96 edges (avg confidence: 0.63)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bc7a2ff5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- candidate_residuals
- clinical_forms.py
- test_assemble_pipeline.py
- generation_status
- batch.py
- Reference: verified template structure
- template_ingest.py
- test_docx_roundtrip.py
- test_app.py
- schema.py
- test_generation.py
- test_template_ingest.py
- Local clinical LLM fine-tune — design
- structured_spans
- deidentify.py
- test_app_screens.py
- model_setup.py
- test_train_and_grammar.py
- backends.py
- fill_template
- test_desktop_packaging.py
- get_form_spec
- test_cloud_client.py
- Clinic reference library — design
- app.py
- deidentify
- components.py
- test_combined_sources_generate_every_form_type_with_a_stub_backend
- test_deid_regressions.py
- make_sample_docs.py
- assert_deidentified
- extract_text
- Architecture
- test_stress_corpus.py
- combine_sources
- analyze_document
- FormType
- CareScribe — design system
- make_icon.py
- EncounterFacts
- exemplars.py
- mapping.py
- ollama_client.py
- run_app.py
- test_buildinfo.py
- residual_scan
- highlight_review
- core/__init__.py
- BackendError
- review_spans.py
- Model Card for phi35-v1
- Installing CareScribe
- validators.py
- Clinic-uploaded clinical form templates — design
- [0.1.0] - 2026-09-01
- Report templates (SOAP / GP letter / discharge / custom)
- Outpatient Respiratory Clinic Letter (doc03)
- RuntimeError
- Reference: verified against the real codebase
- swarm-pipeline.md
- train/__init__.py
- Ward 7B Nursing Handover (doc04)
- inject
- merge_spans
- test_clinical_form_templates.py
- carescribe/__init__.py
- deid_prompt.py
- prompts/__init__.py
- build_dmg.sh
- build_macos.sh
- rthook_carescribe.py
- tests/__init__.py
- run_all.py
- generate_document
- House-style exemplar retrieval — design
- main
- desktop.py
- with_banner
- Cloud generation transport (`CloudBackend`) — design
- test_reference_library.py
- merge_and_convert.sh
- GLiNER Deliberately Uninstalled
- test_eval.py
- Sample Source Documents README
- Recurring fictional staff roster (e.g. A. Whitfield) across documents
- Lightweight review UX for de-identification — design
- test_deid_pipeline.py
- review_spans
- NoEgress
- test_clinical_forms_generate.py
- test_generator_backend.py
- test_review_gate.py
- select_backend
- refine_document
- test_generation_setup.py
- CareScribe clinical drafting model — model card
- expand_name_variants
- search
- <id> — <title>
- analyze
- LLM backend flexibility + realistic test corpus + full-pipeline validation
- verify_frozen.py
- Per-field retrieval planner — design
- components/__init__.py
- build_dataset.py
- test_batch.py
- Evaluation report
- blocking_reason
- OllamaBackend
- AGENTS.md — rules for automated coding agents in this repo
- Task board
- Global Constraints
- finetune/
- run_eval.py
- load_protected_terms
- reference_library.py
- finetune/__init__.py
- integrate/__init__.py
- test_mapping.py
- parse_fields
- medgpt-finetune
- canonical_person_key
- resolve_placeholder
- query_tokens
- carenotes.py
- _run_form_generation
- eval/__init__.py
- is_model_present
- assemble/__init__.py
- ner_spans
- _run
- wipe_phi
- resolve_model_path
- test_app_clinical_forms.py
- _RecordingBackend
- DeidentificationError

## God Nodes (most connected - your core abstractions)
1. `deidentify()` - 71 edges
2. `EncounterFacts` - 49 edges
3. `get_form_spec()` - 47 edges
4. `FormType` - 43 edges
5. `Document` - 42 edges
6. `residual_scan()` - 28 edges
7. `generate_document()` - 27 edges
8. `sample_encounters()` - 26 edges
9. `generation_status()` - 23 edges
10. `RecordingBackend` - 21 edges

## Surprising Connections (you probably didn't know these)
- `Stable per-entity placeholder scheme` --semantically_similar_to--> `build_prompt()`  [INFERRED] [semantically similar]
  README.md → carescribe/core/clinical_forms.py
- `Section-path field key slug scheme` --rationale_for--> `slugify()`  [EXTRACTED]
  docs/superpowers/specs/2026-08-13-clinical-forms-design.md → carescribe/core/clinical_forms.py
- `presidio-analyzer` --references--> `_build_analyzer()`  [INFERRED]
  requirements.txt → carescribe/core/deidentify.py
- `spaCy Model Fallback Chain` --rationale_for--> `_build_analyzer()`  [INFERRED]
  requirements.txt → carescribe/core/deidentify.py
- `pdfplumber` --references--> `extract_text()`  [INFERRED]
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

## Communities (140 total, 23 thin omitted)

### Community 0 - "candidate_residuals"
Cohesion: 0.14
Nodes (17): candidate_residuals(), Flag, _is_common(), outstanding(), _placeholder_ranges(), Residual-candidate highlighter — where the reviewer's eye should go first. This…, One span worth a second look, with its offsets in the redacted text., Identity for dismissal — per value, so one decision covers repeats. (+9 more)

### Community 1 - "clinical_forms.py"
Cohesion: 0.16
Nodes (22): _biopsychosocial_spec(), build_prompt(), _form_grammar(), FormField, FormSpec, generate_form_document(), _grid_fields(), HeaderField (+14 more)

### Community 2 - "test_assemble_pipeline.py"
Cohesion: 0.18
Nodes (20): build_manifest(), _carescribe_sha(), content_hash(), Provenance for a built dataset. A content hash over the pair list, plus how it…, SHA-256 over the sorted JSON lines — stable regardless of pair order., make_pair(), make_template_pair(), Pair (+12 more)

### Community 3 - "generation_status"
Cohesion: 0.10
Nodes (25): cache_data, _draft_state(), _form_draft_state(), _model_card_path(), Path, Which backend will be used, and the fix if none is available., Shown instead of an empty panel when no model is available yet. An empty…, Option A. The only outbound request the app makes, on an explicit click. (+17 more)

### Community 4 - "batch.py"
Cohesion: 0.14
Nodes (20): _as_docx(), The de-identified draft, refinement, re-identification, and exports., Opt-in, local-only substitution of placeholders back to real values., Render generated text to a .docx in memory — nothing touches disk., render_draft(), render_reidentification(), approved_docx_path(), approved_path() (+12 more)

### Community 5 - "Reference: verified template structure"
Cohesion: 0.10
Nodes (20): carescribe/core/clinical_forms.py (module), Refine prompt (clinical form, marker-preserving), Refine prompt (free-form draft revision), Clinical Form Generation (APS Templates) Implementation Plan, Global Constraints, Reference: verified template structure, Self-Review Notes (for the implementer), Task 10: End-to-end generation glue (`generate_form_document`, `refine_form_document`, `render_preview`) (+12 more)

### Community 6 - "template_ingest.py"
Cohesion: 0.12
Nodes (31): Let a clinic add its own table-based .docx form to the selector. Parsing and…, _render_template_uploader(), ClinicalFormError, RuntimeError, Raised when a clinical form can't be built or filled., slugify(), delete_template(), _find_grids() (+23 more)

### Community 7 - "test_docx_roundtrip.py"
Cohesion: 0.06
Nodes (53): approved_map(), document_has_text_boxes(), The reviewer-approved ``{literal: placeholder}`` map for the Word pass. This is…, Redact the original .docx into the output folder, structure preserved. The same…, True if a .docx holds text this redaction pass cannot reach., write_approved_docx(), apply_redactions(), _delete_prefix() (+45 more)

### Community 8 - "test_app.py"
Cohesion: 0.10
Nodes (39): analysed_batch(), _clean_auto_doc(), data_editors(), loaded_batch(), _NullBackend, AppTest, UI checks for the batch review app via Streamlit's AppTest. No server of any…, After the read-and-confirmed tick, a clean auto-confidence document has nothing… (+31 more)

### Community 9 - "schema.py"
Cohesion: 0.06
Nodes (62): BaseModel, Enum, field_validator, _blank_for(), expand(), Random, Turn vignettes into `EncounterFacts` instances with a seeded RNG. `expand`…, Yield ``n`` `EncounterFacts`, deterministic for a given ``seed``. (+54 more)

### Community 10 - "test_generation.py"
Cohesion: 0.09
Nodes (24): finalise(), Re-identify a draft locally and refuse to hand back a leaky document. Returns…, check_placeholder_integrity(), Compare a draft's bracketed tokens against the placeholders it should use. An…, Local re-identification of a generated draft. Returns ``(text, unresolved)``.…, reidentify_document(), Local generation: the privacy contract, placeholder integrity, and the gate. No…, Between [MRN_1] and [MRN_2], refusing is the only safe answer. (+16 more)

### Community 11 - "test_template_ingest.py"
Cohesion: 0.13
Nodes (21): available_forms(), (form_id, title) pairs — bundled forms first, then clinic-uploaded ones., fill_parsed_template(), Fill an in-memory copy of ``original_docx`` from ``spec``'s anchors. A thin…, _anchors(), _build_synthetic(), _merge_full_width(), fixture (+13 more)

### Community 12 - "Local clinical LLM fine-tune — design"
Cohesion: 0.06
Nodes (30): 10. Workstream E — integration, 11. What needs a human / external resource, 12. Milestones (testable deliverables), 13. Testing strategy, 1. Goal, 2. Constraints inherited from CareScribe, 3. Approach (selected), 4. Base model (+22 more)

### Community 13 - "structured_spans"
Cohesion: 0.17
Nodes (12): _header_footer_bounds(), _plausible_surname(), Character ranges of the document's opening and closing lines., A clock time is identifying only when it belongs to an appointment., True if the trailing token of an initial+surname reads like a real name.…, Layer 1: deterministic regex detections over ``text``., structured_spans(), _time_span_wanted() (+4 more)

### Community 14 - "deidentify.py"
Cohesion: 0.10
Nodes (29): classify_person(), date_span_wanted(), _has_contact_anchor(), _has_identity_anchor(), _is_acronym(), _is_clinical_measurement(), _is_isolated_table_cell(), _is_labelled_date_field() (+21 more)

### Community 15 - "test_app_screens.py"
Cohesion: 0.12
Nodes (28): deid(), ner_available(), fixture, Shared pytest fixtures. The spaCy model load costs several seconds, so the…, The full pipeline's output for the fixture document., True when a spaCy model loaded — layer 2 tests skip without one., raw_text(), redacted() (+20 more)

### Community 16 - "model_setup.py"
Cohesion: 0.15
Nodes (18): clear_partial_download(), download_model(), _free_bytes(), model_destination(), ModelSetupError, Progress, Path, RuntimeError (+10 more)

### Community 17 - "test_train_and_grammar.py"
Cohesion: 0.05
Nodes (54): _body_rules(), compile_grammar(), field_grammar(), _lit(), note_grammar(), _placeholder_rule(), GBNF grammars for constrained local decoding — a structural guarantee on top of…, Compile a GBNF string with llama-cpp-python, or return ``None``. Never raises:… (+46 more)

### Community 18 - "backends.py"
Cohesion: 0.14
Nodes (20): privacy_indicator(), A persistent, honest statement of where data goes. It must change when cloud…, cloud_enabled(), cloud_key_present(), cloud_provider(), CloudBackend, describe_backends(), Generation backends, layered so the app works with nothing installed. Selection… (+12 more)

### Community 19 - "fill_template"
Cohesion: 0.14
Nodes (22): _clear_cell(), _dedupe_row(), _fill_cell(), _fill_cell_after_label(), _fill_header_cell(), fill_template(), Remove every paragraph after the first, and every run in the first, leaving one…, Overwrite a dedicated value cell (label lives in a different cell). (+14 more)

### Community 20 - "test_desktop_packaging.py"
Cohesion: 0.09
Nodes (17): available_ram_gb(), ram_verdict(), Total system RAM in GB, or 0.0 if it cannot be determined., Whether this machine can run the bundled local model. Returns a verdict rather…, _cloud_off(), fixture, The packaging invariants: what the desktop app may and may not do. Packaging is…, No key may be committed, defaulted, or written anywhere. (+9 more)

### Community 21 - "get_form_spec"
Cohesion: 0.17
Nodes (21): get_form_spec(), plan(), _load(), Generic table-row classification: which rows are fields, which are section…, test_biopsychosocial_spec_field_count_and_grid(), test_no_field_key_collides_within_a_spec(), test_session_notes_field_walk_finds_nine_fields(), test_session_notes_signature_row_is_excluded() (+13 more)

### Community 22 - "test_cloud_client.py"
Cohesion: 0.10
Nodes (25): CloudError, _config(), _post(), RuntimeError, Transport for the optional cloud generation backend. Reached only when a…, Yield the payload of each ``data:`` line in an SSE stream., Stream a completion from the configured cloud provider, yielding text. Raises…, A recoverable problem talking to the configured cloud provider. (+17 more)

### Community 23 - "Clinic reference library — design"
Cohesion: 0.17
Nodes (11): `app.py`, Architecture, Clinic reference library — design, Decision, Follow-ups (not blocking), New `core/reference_library.py`, Privacy / safety, Problem (+3 more)

### Community 24 - "app.py"
Cohesion: 0.10
Nodes (42): current(), document_flags(), entity_confirmed(), entity_frame(), flag_dismissals(), CareScribe — local, privacy-preserving de-identification and review. Run with:…, One click to approve every document that comes back clean. Each is re-run…, Re-derive the preview and map from an edited entity list. (+34 more)

### Community 25 - "deidentify"
Cohesion: 0.10
Nodes (35): deidentify(), Run the full local pipeline over one document. CPU-only and offline: no model…, With no spaCy model, layer 1 must still protect the document., Two runs over the same text must agree, or review is meaningless., test_pipeline_is_deterministic(), test_pipeline_runs_without_ner(), parametrize, Regression suite for the round-2 leaks (A1-A9). The corpus tests in… (+27 more)

### Community 26 - "components.py"
Cohesion: 0.10
Nodes (32): _model_card_dialog(), Name the generation model with a readable label; the card opens in a dialog…, _render_generation_model(), render_sidebar(), chip(), detection_layer(), empty_state(), _esc() (+24 more)

### Community 27 - "test_combined_sources_generate_every_form_type_with_a_stub_backend"
Cohesion: 0.32
Nodes (6): skipif, parametrize, Deterministic stand-in for a real generation backend., _StubBackend, test_combined_sources_generate_every_form_type_with_a_stub_backend(), test_ingest_and_deidentify_every_sample_document()

### Community 28 - "test_deid_regressions.py"
Cohesion: 0.08
Nodes (31): _mrn_values(), parametrize, Regression suite for the five leaks found on a second, non-fixture document.…, A two-part capitalised phrase mid-document is not a letterhead., Layer 1 must carry this on its own — NER catching it is luck, not a guarantee., M.E.C.\\nFollow-up" must not become the name "M.E.C. Follow"., Regardless of REDACT_INPROSE_DATES, which stays False by default., 14 June 2026\\nDate" swallowed the next line's label and mangled the text. (+23 more)

### Community 29 - "make_sample_docs.py"
Cohesion: 0.21
Nodes (21): build_case_conference_note(), build_discharge_summary(), build_intake_notes(), build_referral_letter(), build_risk_assessment(), build_session_log(), build_treatment_review_source(), _grid_table() (+13 more)

### Community 30 - "assert_deidentified"
Cohesion: 0.12
Nodes (17): assert_deidentified(), Backend, CloudBackend (unwired seam), Protocol, True only when ``needle`` occurs in ``haystack`` as a whole token run. Both are…, Refuse to send anything carrying a value from the identity mapping. A cheap,…, One method wide: the seam a different provider would be swapped in at.…, _value_present() (+9 more)

### Community 31 - "extract_text"
Cohesion: 0.05
Nodes (55): BaseException, ensure_engine_ready(), Load the model at startup, behind a visible spinner. Deliberately not lazy. If…, The last line of defence: a calm message instead of a stack trace. A clinician…, render_unexpected_error(), exception(), get_logger(), log() (+47 more)

### Community 32 - "Architecture"
Cohesion: 0.13
Nodes (14): 1. Template assets, 2. Form spec extraction, 3. Header fields (practitioner-entered), 4. Multi-document source combination, 5. Generation, 6. Review, 7. Export, 8. UI (`app.py`, Step 5) (+6 more)

### Community 33 - "test_stress_corpus.py"
Cohesion: 0.05
Nodes (48): answer_key.json, Community MH Discharge Letter (doc01), Mohammed Al-Rashid ('Mo'), Cardiology Discharge Summary (doc02), Margaret Elizabeth Chen ('Peggy'), Elspeth Mackenzie-Ford ('Ellie'), GP Referral Letter (doc05), Priya Venkataraman (+40 more)

### Community 34 - "combine_sources"
Cohesion: 0.21
Nodes (13): combine_sources(), Concatenate several documents' de-identified text into one source. ``sources``…, Regression test for Finding 3: raw filename must not leak into model-facing…, Regression test for Finding 1: cap at 26 documents (A-Z)., Regression test for Finding 1: prefixed placeholders must match PLACEHOLDER_RE.…, Regression test for Finding 2: text and map rewrites must be consistent. A…, test_combine_sources_no_filename_in_output(), test_combine_sources_non_standard_placeholder_consistency() (+5 more)

### Community 35 - "analyze_document"
Cohesion: 0.15
Nodes (13): analyze_document(), Run the de-identification layers over one document, in place., test_analyze_document_populates_state(), Stands in for a model so the egress test does not need one installed., Load → de-identify → approve → generate, with egress forbidden., StubBackend, test_the_mapping_is_never_written(), test_the_whole_flow_opens_no_outbound_socket() (+5 more)

### Community 36 - "FormType"
Cohesion: 0.16
Nodes (18): build_messages(), Care note templates. Every template shares the same hard rule: the input is…, Return ``(system, user)`` for a template label and de-identified document., FormType, The output form a training example asks the model to fill., build_messages(), default_instruction(), The prompt construction shared by training and production. Training pairs MUST… (+10 more)

### Community 37 - "CareScribe — design system"
Cohesion: 0.20
Nodes (9): Browser surfaces, CareScribe — design system, Components (`carescribe/ui/components.py`), Direction, Palette, Sidebar order, Space & shape, Type (+1 more)

### Community 38 - "make_icon.py"
Cohesion: 0.29
Nodes (12): Image, _load_font(), main(), Path, Generate CareScribe's placeholder icon. A real icon is a design job; this…, The first usable bold face, or ``None`` if none of them load., A rounded square with "CS" centred on it., macOS only. Silently skipped elsewhere — the .app is built on a Mac. (+4 more)

### Community 39 - "EncounterFacts"
Cohesion: 0.25
Nodes (17): _care_plan(), _field_content(), _handover(), _history_lines(), _med_line(), _objective_lines(), _plan_lines(), _progress_note() (+9 more)

### Community 40 - "exemplars.py"
Cohesion: 0.14
Nodes (25): add_exemplar(), count(), _dir(), _load(), _path(), Path, House-style exemplar retrieval for clinical-form generation. A clinic…, Top-``k`` stored values for ``field_key``, ranked by BM25 against ``query``. (+17 more)

### Community 41 - "mapping.py"
Cohesion: 0.09
Nodes (29): build_map(), expand_facility_variants(), find_known_as(), find_spans(), _form_pattern(), Issue, Pattern, In-memory PII <-> placeholder mapping. This module is deliberately pure: it… (+21 more)

### Community 42 - "ollama_client.py"
Cohesion: 0.11
Nodes (26): Option B. Ollama does the fetching; the request goes to loopback., run_ollama_pull(), generate_care_note(), Draft a care note from ALREADY DE-IDENTIFIED text, returning it whole. The…, pull_ollama_model(), Ask the local Ollama daemon to pull a model, yielding progress. The request…, default_model(), generate() (+18 more)

### Community 43 - "run_app.py"
Cohesion: 0.16
Nodes (17): Popen, close_splash(), _fatal(), free_port(), main(), _no_window_kwargs(), CareScribe desktop launcher — the app's entry point. Starts the Streamlit…, Dismiss the bootloader splash, if this is a frozen build that has one.… (+9 more)

### Community 44 - "test_buildinfo.py"
Cohesion: 0.24
Nodes (10): build_info(), Build information for CareScribe., Return standard HTTP User-Agent string., Return application identity and version., user_agent(), Tests for buildinfo module., Test that user_agent returns correct format., Test that build_info returns correct name and version. (+2 more)

### Community 45 - "residual_scan"
Cohesion: 0.15
Nodes (13): Re-scan ALREADY-REDACTED text for anything that still looks identifying. Runs…, residual_scan(), main(), normalise(), Per-document pass/fail report for the stress corpus. python…, Placeholders are the point of the exercise, not leaks., A .txt file read off a Windows disk arrives with CRLF endings. NER tokenises…, test_crlf_and_lf_documents_behave_identically() (+5 more)

### Community 46 - "highlight_review"
Cohesion: 0.24
Nodes (9): highlight_review(), Click-to-redact highlighted text. Renders already-redacted (or already-flagged)…, Render ``html`` and return the ``data-span-id`` of the last click. Returns…, _frontend_path(), Path, Offline-first: nothing in this file may fetch from a CDN., test_frontend_file_exists(), test_frontend_has_no_external_script_or_link_tags() (+1 more)

### Community 47 - "core/__init__.py"
Cohesion: 0.24
Nodes (13): Core logic: Ollama access, ingestion, de-identification, care notes, PHI…, load_settings(), _path(), Persisted app settings — which generation backend/model/temperature to use.…, Read persisted settings. A missing or unreadable file yields defaults., Persist non-secret settings, creating the app data dir if needed., save_settings(), Settings (+5 more)

### Community 48 - "BackendError"
Cohesion: 0.20
Nodes (8): BackendError, LocalGGUFBackend, True if the runtime and a model file are both present., Raised when a backend cannot be used, with the fix in the message., Shared message for a completion cut off by the token/context budget. A half-…, CPU-only generation from a bundled GGUF via ``llama-cpp-python``. The model is…, _truncation_error(), RuntimeError

### Community 49 - "review_spans.py"
Cohesion: 0.38
Nodes (6): _entity_spans(), Unifies the two things a reviewer might still need to act on in one document's…, One clickable span in a document's redacted text., Placeholder occurrences for low-confidence, not-yet-confirmed entities., _residual_spans(), ReviewSpan

### Community 50 - "Model Card for phi35-v1"
Cohesion: 0.33
Nodes (5): Citations, Framework versions, Model Card for phi35-v1, Quick start, Training procedure

### Community 51 - "Installing CareScribe"
Cohesion: 0.22
Nodes (8): Before you start, First launch, If it will not start, Installing CareScribe, macOS, Updating, Where your files go, Windows

### Community 52 - "validators.py"
Cohesion: 0.10
Nodes (34): build_target(), The ideal filled form for ``facts`` — deterministic, fact-placed only.…, check_faithfulness(), check_format(), _check_marker_format(), check_placeholders(), check_residual(), _field_is_empty() (+26 more)

### Community 53 - "Clinic-uploaded clinical form templates — design"
Cohesion: 0.18
Nodes (10): Architecture, Clinic-uploaded clinical form templates — design, Follow-ups (not blocking), New module `core/template_ingest.py`, Persistence, Problem, Registry integration (`core/clinical_forms.py`), Scope (+2 more)

### Community 54 - "[0.1.0] - 2026-09-01"
Cohesion: 0.50
Nodes (3): [0.1.0] - 2026-09-01, Added, Changelog

### Community 55 - "Report templates (SOAP / GP letter / discharge / custom)"
Cohesion: 0.40
Nodes (5): SOAP care note prompt template, GP clinic letter prompt template, Custom (clinician house format) prompt template, Discharge summary prompt template, Report templates (SOAP / GP letter / discharge / custom)

### Community 56 - "Outpatient Respiratory Clinic Letter (doc03)"
Cohesion: 0.40
Nodes (5): Ngozi Okafor, Outpatient Respiratory Clinic Letter (doc03), Attendee list pattern, Header town + county pattern, Record-number label shapes (three variants)

### Community 58 - "Reference: verified against the real codebase"
Cohesion: 0.15
Nodes (12): Global Constraints, Lightweight Review UX Redesign Implementation Plan, Reference: verified against the real codebase, Self-Review Notes, Task 1: Confidence tiering in the detection pipeline, Task 2: Unified review-span module, Task 3: Click-to-redact custom Streamlit component, Task 4: Simplify `review_checklist.py` to a two-input gate (+4 more)

### Community 61 - "Ward 7B Nursing Handover (doc04)"
Cohesion: 0.50
Nodes (4): Aiden Braithwaite, Ward 7B Nursing Handover (doc04), 'A. Surname' against full name in header, Labelled date fields

### Community 62 - "inject"
Cohesion: 0.15
Nodes (26): _collect(), _date(), _dob(), inject(), _make(), _mrn(), _name(), nhs_number() (+18 more)

### Community 63 - "merge_spans"
Cohesion: 0.14
Nodes (14): _collapse_facility_subsets(), _collapse_person_identities(), _collapse_person_subsets(), merge_spans(), protected_ranges(), Shrink a NER span to its identifying core. Drops leading titles ("Sister Fiona…, Drop a person entity whose name is contained in a longer one. NER returns…, True for a person row whose role is known (patient / relative / clinician). (+6 more)

### Community 64 - "test_clinical_form_templates.py"
Cohesion: 0.50
Nodes (3): parametrize, The three bundled APS templates load and match the structure this feature's…, test_bundled_template_shape()

### Community 73 - "generate_document"
Cohesion: 0.11
Nodes (24): generate_document(), Stream a drafted document from approved de-identified text. ``phi_values`` is…, parametrize, A 2-char mapping value must not refuse a clean draft just because those…, The boundary check must not weaken a real leak: a short value standing alone as…, The complement of the mapping-value check: a leaked identifier that was never…, `acknowledged` carries the residual-sweep findings approval accepted (a town…, `phi_values` exists to assert absence, never to be forwarded. (+16 more)

### Community 74 - "House-style exemplar retrieval — design"
Cohesion: 0.18
Nodes (10): `app.py`, Architecture, `core/clinical_forms.py`, Follow-ups (not blocking), House-style exemplar retrieval — design, New module `core/exemplars.py`, Privacy, Problem (+2 more)

### Community 76 - "main"
Cohesion: 0.13
Nodes (16): documents(), ingest_sources(), main(), _pipeline_step(), _privacy_state(), A missing model must stop loudly, never fall back to fetching one., The 0-based step the reviewer stands on, for components.step_tracker()., Extract text from uploads/paths into session state. (+8 more)

### Community 77 - "desktop.py"
Cohesion: 0.14
Nodes (25): app_data_dir(), bundle_root(), ensure_dirs(), find_local_model(), is_frozen(), _model_search_dirs(), models_dir(), output_dir() (+17 more)

### Community 78 - "with_banner"
Cohesion: 0.40
Nodes (5): Prepend the review banner, without duplicating one already there., with_banner(), test_generated_output_keeps_the_review_banner(), test_every_draft_carries_the_review_banner(), test_the_banner_is_not_duplicated_on_refinement()

### Community 80 - "Cloud generation transport (`CloudBackend`) — design"
Cohesion: 0.20
Nodes (9): Architecture, Cloud generation transport (`CloudBackend`) — design, `core/backends.py`, Follow-ups (not blocking), New module `core/cloud_client.py`, Privacy properties (unchanged, inherited), Problem, Scope (+1 more)

### Community 81 - "test_reference_library.py"
Cohesion: 0.15
Nodes (19): add_file(), is_empty(), ``(filename, paragraph_count)`` per loaded reference file., Store an uploaded reference file. Returns the stored filename., sources(), _library(), fixture, Clinic reference library: paragraph chunking with heading tracking, BM25… (+11 more)

### Community 84 - "test_eval.py"
Cohesion: 0.09
Nodes (34): aggregate(), DraftScore, _headings(), _lexical_overlap(), _order_agreement(), The four target metrics, scored per draft and reducible to a mean. Format,…, Mean of each metric over ``scores`` (style_match over styled drafts only)., Fraction of ``a``'s headings that appear in ``b`` in the same relative order. (+26 more)

### Community 87 - "Lightweight review UX for de-identification — design"
Cohesion: 0.14
Nodes (13): 1. Confidence tiering (drives what gets a click at all), 2. One primary review view, not three, 3. The click-to-redact component, 4. Attestation & audit trail, 5. Crash-risk fixes, Architecture, Current state (for reference), Goals (+5 more)

### Community 88 - "test_deid_pipeline.py"
Cohesion: 0.05
Nodes (36): parametrize, Regression suite for the layered de-identification pipeline. Two guarantees,…, With REDACT_INPROSE_DATES False, a procedure date is clinical, not identity., DOB and admission/discharge dates carry identity, so they go., spaCy labels "ECG" and "NSTEMI" as organisations; the filter must drop them., One real value, one placeholder — the whole point of the mapping., Marking a row Keep must un-redact exactly that value and nothing else., The add action IS the human decision — no second click to confirm it. (+28 more)

### Community 89 - "review_spans"
Cohesion: 0.32
Nodes (12): Every clickable span in ``redacted_text``, in reading order. ``confirmed`` is…, review_spans(), _entity(), action=Keep means the reviewer already decided — nothing to click on the…, test_a_confirmed_entity_produces_no_span(), test_a_kept_entity_produces_no_entity_span(), test_auto_confidence_entities_produce_no_span(), test_dismissed_residual_flags_are_excluded() (+4 more)

### Community 91 - "NoEgress"
Cohesion: 0.14
Nodes (10): NoEgress, Fails the test if anything opens a non-loopback socket. Loopback is allowed:…, Re-identification is pure Python — it must not phone anywhere., test_reidentification_opens_no_socket(), The load that used to hang on a captive portal must not exist., Reset the cache so the guard covers a genuine first load., The reported hang: no model, so something tries to download it., test_a_missing_model_fails_loudly_instead_of_fetching() (+2 more)

### Community 92 - "test_clinical_forms_generate.py"
Cohesion: 0.23
Nodes (9): Human-readable rendering for display only — the marker text in ``draft_state``…, render_preview(), Captures exactly what generation handed the model — mirrors the fixture in…, RecordingBackend, test_generate_form_document_refuses_a_real_identifier(), test_generate_form_document_sends_the_field_marker_prompt(), test_refine_form_document_preserves_markers_instruction(), test_render_preview_defaults_missing_value() (+1 more)

### Community 93 - "test_generator_backend.py"
Cohesion: 0.11
Nodes (19): GeneratorBackend, get_backend(), OllamaBackend, OpenAICompatibleBackend, TemplateBackend, Test that TemplateBackend properly renders facts in proforma style, Test that TemplateBackend properly renders facts in prose style, Test that TemplateBackend is deterministic - same input gives same output (+11 more)

### Community 94 - "test_review_gate.py"
Cohesion: 0.13
Nodes (16): _flag_values(), fixture, parametrize, The reviewer gate: candidate highlighting, the adaptive checklist, and the no-…, The real test: nothing the corpus calls an identifier may appear., A dismissal key holds the span text, so it must be wiped with the rest., Five-digit rule must not fire on "10mg" style clinical numbers., record() (+8 more)

### Community 95 - "select_backend"
Cohesion: 0.13
Nodes (19): Pick a backend. Returns ``(kind, backend, label)``. ``prefer`` lets the UI…, select_backend(), _backend_with_fake_model(), _FakeModel, The happy path must keep working: finish_reason 'stop' yields the text with no…, The streaming path gets finish_reason only on its final, contentless chunk…, The default (no prefer/model/temperature) path is unchanged., Stands in for ``llama_cpp.Llama``: only ``create_chat_completion`` is ever… (+11 more)

### Community 96 - "refine_document"
Cohesion: 0.20
Nodes (11): The shared preamble — role, anti-fabrication rules, placeholder rules., Revise an existing draft against a follow-up instruction. Operates on the same…, refine_document(), system_prompt(), test_generate_document_default_behaviour_is_unchanged(), test_refine_also_rescans_the_source_for_missed_identifiers(), test_refine_document_accepts_a_system_and_refine_prompt_override(), test_refine_document_default_behaviour_is_unchanged() (+3 more)

### Community 97 - "test_generation_setup.py"
Cohesion: 0.06
Nodes (28): _cloud_off(), _fresh_generation_status_cache(), mapping_module(), _nothing_available(), fixture, First-run generation setup: never an empty panel, and the egress line held. The…, A second call within the TTL must not re-probe Ollama., No module may fetch a model as a side effect of being imported. (+20 more)

### Community 98 - "CareScribe clinical drafting model — model card"
Cohesion: 0.40
Nodes (4): CareScribe clinical drafting model — model card, Evaluation, Known limitations, Training data

### Community 99 - "expand_name_variants"
Cohesion: 0.20
Nodes (10): expand_name_variants(), _initial_letters(), Initials for a name, with hyphenated components contributing each part.…, Return every plausible written form of one person's name. Covers: the full…, Dr" as a standalone form would redact every "Dr" in the document., St." must never become a bare "St" that matches clinical text., test_abbreviated_token_is_not_a_standalone_name_form(), test_expand_name_variants_covers_the_forms_the_document_uses() (+2 more)

### Community 100 - "search"
Cohesion: 0.15
Nodes (12): ExemplarError, RuntimeError, Raised when an exemplar cannot be stored — e.g. it still holds an identifier., RuntimeError, Top-``k`` reference passages for ``query`` at ``granularity``. BM25, ``score >…, Raised when a reference file cannot be stored., ReferenceError, ReferenceHit (+4 more)

### Community 101 - "<id> — <title>"
Cohesion: 0.29
Nodes (6): Acceptance criteria, Do NOT touch, Files in scope, Goal, <id> — <title>, Notes

### Community 102 - "analyze"
Cohesion: 0.11
Nodes (19): analyze(), _crosses_paragraph_break(), flatten_lines(), gliner_spans(), Layer 3: GLiNER detections, or an empty list when it isn't installed., Run every enabled layer over ``text`` and return reviewable entities. Each…, One detection, in character offsets over the source text., Return ``text`` with every line break collapsed to one space, plus an offset… (+11 more)

### Community 104 - "LLM backend flexibility + realistic test corpus + full-pipeline validation"
Cohesion: 0.20
Nodes (9): A. Backend/settings flexibility, B. Realistic document corpus, C. Full-pipeline validation loop, Design, Goals, LLM backend flexibility + realistic test corpus + full-pipeline validation, Non-goals, Problem (+1 more)

### Community 105 - "verify_frozen.py"
Cohesion: 0.36
Nodes (9): bundled_app_py(), _default_dist(), find_executable(), free_port(), main(), Path, Post-build smoke check: does the frozen CareScribe binary actually start? A…, Locate the frozen entry-point inside a PyInstaller output directory. (+1 more)

### Community 106 - "Per-field retrieval planner — design"
Cohesion: 0.17
Nodes (11): `app.py`, Architecture, `core/reference_library.py`, `core/retrieval_planner.py` (new), `core/text_search.py`, Decision, Follow-ups (not blocking), Per-field retrieval planner — design (+3 more)

### Community 108 - "build_dataset.py"
Cohesion: 0.12
Nodes (28): build(), _fallback_inject(), _load_datagen_config(), main(), Path, End-to-end: sampled encounters -> validated SFT pairs + manifest. python -m…, Return ``{"pairs": [...], "kept": k, "dropped": d, "reasons": {...}}``.…, Fill ``[[TOKEN]]`` slots with simple fake values. Used only until… (+20 more)

### Community 109 - "test_batch.py"
Cohesion: 0.07
Nodes (37): BatchError, list_folder(), load_documents(), RuntimeError, Return the supported documents in ``folder``, sorted by name. Non-recursive on…, Extract text from uploads or paths. Returns ``(documents, errors)``. One…, Findings from the safety sweep, minus the ones the reviewer has cleared. A…, Write approved de-identified text to the output folder. Re-runs the safety… (+29 more)

### Community 111 - "blocking_reason"
Cohesion: 0.17
Nodes (11): blocking_reason(), The approval gate. Only the **authoritative safety sweep** blocks approval. A…, Why Approve is disabled, in one short line. Empty string means it isn't.…, Low-confidence redactions are already in place; the permissive flags are…, The streamlined gate: a permissive flag the reviewer left untouched does not…, test_advisory_spans_do_not_block_approval(), test_an_advisory_flag_alone_no_longer_blocks_approval(), test_approval_is_blocked_while_the_sweep_has_findings() (+3 more)

### Community 113 - "OllamaBackend"
Cohesion: 0.12
Nodes (14): OllamaBackend, Local generation through the loopback-pinned Ollama daemon., core/model_setup.py (model download, isolated), packaging/build_macos.sh, packaging/build_windows.ps1, packaging/carescribe.iss (Inno Setup script), packaging/make_icon.py, The desktop app (PyInstaller packaging) (+6 more)

### Community 114 - "AGENTS.md — rules for automated coding agents in this repo"
Cohesion: 0.40
Nodes (4): AGENTS.md — rules for automated coding agents in this repo, Do, Never, Task spec shape

### Community 115 - "Task board"
Cohesion: 0.11
Nodes (17): App bug the user hit (2026-09-01) — FIXED in `e9bcc3b`, Fine-tune decisions locked (2026-09-01), Fine-tune hardware facts (2026-09-01), Fine-tune progress — cockpit-driven, COMMITTED on integration branch, Local clinical LLM fine-tune (started 2026-09-01), M3–M5 DONE — model trained, evaluated, integrated (2026-09-01), Pipeline incident 2026-09-01 (fixed), Punch-list — "address all 10 issues" (2026-09-02) (+9 more)

### Community 116 - "Global Constraints"
Cohesion: 0.18
Nodes (10): Global Constraints, LLM Backend Flexibility + Realistic Test Corpus Implementation Plan, Task 1: Settings persistence module, Task 2: `select_backend()` explicit model/temperature overrides + Ollama temperature fix, Task 3: Settings panel UI + wiring generation call sites through it, Task 4: Stress corpus expansion — batch 1 (5 documents), Task 5: Stress corpus expansion — batch 2 (5 documents), Task 6: Sample documents expansion (full-pipeline generation exercise) (+2 more)

### Community 118 - "finetune/"
Cohesion: 0.40
Nodes (4): Environment, finetune/, Layout, Milestones

### Community 119 - "run_eval.py"
Cohesion: 0.14
Nodes (18): DeidentifiedNote, deidentify_note(), leaked_values(), Run the real CareScribe de-identifier over a synthetic note. The fine-tune must…, De-identify one rendered+identified synthetic note., Injected identifier values that de-id did NOT remove from the text. A non-empty…, A regression set built from the repo's own corpus, not synthetic data.…, regressed() (+10 more)

### Community 120 - "load_protected_terms"
Cohesion: 0.29
Nodes (8): _build_protected_pattern(), load_protected_terms(), Path, Pattern, Read the editable allow-list. Blank lines and ``#`` comments are ignored., Re-read the allow-list from disk (the file is meant to be edited by hand)., reload_protected_terms(), test_the_allow_list_is_an_editable_file()

### Community 121 - "reference_library.py"
Cohesion: 0.22
Nodes (14): Add clinic reference files (formulary, pathways, protocols) to a local library.…, _render_reference_uploader(), _all_chunks(), _bounded(), Chunk, _dir(), _files(), _paragraphs() (+6 more)

### Community 126 - "test_mapping.py"
Cohesion: 0.08
Nodes (33): assign_placeholders(), dedupe_entities(), normalise_type(), Coerce a model-supplied type string onto the canonical list., Drop blank and duplicate entities, keeping first-seen order and casing.…, Attach a stable placeholder to each unique entity. A type with exactly one…, Outcome of a re-identification pass., Swap placeholders back to originals, repairing mangled tokens. Never raises on… (+25 more)

### Community 127 - "parse_fields"
Cohesion: 0.44
Nodes (9): parse_fields(), Turn the model's marker-delimited output into ``{field_key: text}``. Any field…, _spec(), test_parse_fields_defaults_missing_field_to_not_documented(), test_parse_fields_first_occurrence_wins_on_duplicate_marker(), test_parse_fields_handles_empty_output(), test_parse_fields_happy_path(), test_parse_fields_ignores_unknown_marker_without_raising() (+1 more)

### Community 131 - "canonical_person_key"
Cohesion: 0.20
Nodes (10): canonical_person_key(), keys_are_compatible(), name_core(), Split a name into its parts with any leading honorific removed. "Mrs Margaret…, A stable identity key for one person: full given name plus surname. This…, True if two canonical keys can denote the same person. Exact match, or one side…, test_canonical_key_separates_two_people_with_one_surname(), test_canonical_key_unifies_the_forms_of_one_person() (+2 more)

### Community 132 - "resolve_placeholder"
Cohesion: 0.29
Nodes (7): _edit_distance(), Levenshtein distance, short-circuiting once it exceeds ``cap``., Map a possibly-corrupted placeholder onto a known one. Returns the exact token…, resolve_placeholder(), Guessing between [MRN_1] and [MRN_2] would attach the wrong identity., test_ambiguous_placeholder_is_refused_not_guessed(), test_edit_distance_caps_out()

### Community 133 - "query_tokens"
Cohesion: 0.20
Nodes (10): Protocol, Per-field retrieval planning for clinical-form generation. Roadmap item E…, Deterministic planner driven by a keyword taxonomy over field labels., RetrievalPlan, RetrievalPlanner, RuleBasedPlanner, query_tokens(), Okapi BM25 over a small in-memory document set — standard library only. Shared… (+2 more)

### Community 134 - "carenotes.py"
Cohesion: 0.16
Nodes (15): assert_no_residual_identifiers(), CareNoteError, load_prompt(), RuntimeError, Care note generation — local, on approved de-identified text only. The contract…, Build the user prompt for one template with the source text embedded., Refuse to send text the residual sweep still flags. :func:`assert_deidentified`…, Raised when care note generation can't proceed. (+7 more)

### Community 135 - "_run_form_generation"
Cohesion: 0.13
Nodes (19): _active_backend(), _invalidate_form_export(), Drop any previously re-identified/exportable content — called whenever the…, Resolve the backend to generate with, honouring saved settings. Centralises…, A concrete "it works", rather than asking the clinician to trust a flag., Render a stream token by token so a slow local model looks alive., First-pass generation. The model receives de-identified text only., Follow-up instructions, on de-identified text only. (+11 more)

### Community 137 - "is_model_present"
Cohesion: 0.50
Nodes (4): is_model_present(), True if a usable model file is already on this computer. This is the marker…, Setup is one-time because the file itself is the state., test_model_presence_is_the_persisted_marker()

### Community 140 - "ner_spans"
Cohesion: 0.11
Nodes (19): cache_resource, load_detection_engine(), Load the NER model once per session, not once per rerun. Streamlit re-runs the…, engine_status(), get_analyzer(), get_gliner(), ner_spans(), Layer 2: Presidio/spaCy detections, mapped onto CareScribe entity types.… (+11 more)

### Community 141 - "_run"
Cohesion: 0.60
Nodes (4): AppTest, _run(), test_saving_settings_persists_and_survives_reload(), test_settings_expander_renders_without_error()

### Community 143 - "wipe_phi"
Cohesion: 0.67
Nodes (4): PHI_KEYS (session-state PHI registry), Drop every document, identifier table, and identity map from memory., wipe_phi(), Bug: form_drafts never registered with PHI_KEYS/wipe_phi

### Community 144 - "resolve_model_path"
Cohesion: 0.50
Nodes (5): available_models(), Where a spaCy model package actually lives, or ``None`` if absent. Resolved…, Every spaCy model importable in this environment., resolve_model_path(), test_model_paths_resolve_explicitly()

### Community 145 - "test_app_clinical_forms.py"
Cohesion: 0.29
Nodes (7): _form_draft_key(), _header_values_complete(), Pure-logic pieces of the clinical-form UI: the session-state key used to key a…, test_form_draft_key_differs_by_form_or_selection(), test_form_draft_key_is_stable_for_the_same_selection(), test_header_values_complete_requires_every_non_reason_field(), test_invalidate_form_export_drops_stale_resolved_values()

### Community 156 - "DeidentificationError"
Cohesion: 0.67
Nodes (3): DeidentificationError, RuntimeError, Raised when de-identification can't run at all.

## Ambiguous Edges - Review These
- `stress_corpus/README.md` → `Psychological Medicine Clinic Letter (doc06)`  [AMBIGUOUS]
  stress_corpus/README.md · relation: references
- `stress_corpus/README.md` → `CMHT Family Review Letter (doc07)`  [AMBIGUOUS]
  stress_corpus/README.md · relation: references
- `stress_corpus/README.md` → `Resource Centre Referral (doc08)`  [AMBIGUOUS]
  stress_corpus/README.md · relation: references
- `stress_corpus/README.md` → `Crisis Team Contact Log (doc09)`  [AMBIGUOUS]
  stress_corpus/README.md · relation: references
- `stress_corpus/README.md` → `Mental Health Act Assessment Record (doc10)`  [AMBIGUOUS]
  stress_corpus/README.md · relation: references

## Knowledge Gaps
- **222 isolated node(s):** `medgpt-finetune`, `merge_and_convert.sh script`, `build_dmg.sh script`, `build_macos.sh script`, `Worker capability ceiling on the fine-tune workstream (2026-09-01)` (+217 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `stress_corpus/README.md` and `Psychological Medicine Clinic Letter (doc06)`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `stress_corpus/README.md` and `CMHT Family Review Letter (doc07)`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `stress_corpus/README.md` and `Resource Centre Referral (doc08)`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `stress_corpus/README.md` and `Crisis Team Contact Log (doc09)`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `stress_corpus/README.md` and `Mental Health Act Assessment Record (doc10)`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `deidentify()` connect `deidentify` to `test_generation_setup.py`, `test_stress_corpus.py`, `analyze_document`, `analyze`, `test_app.py`, `mapping.py`, `test_combined_sources_generate_every_form_type_with_a_stub_backend`, `NoEgress`, `residual_scan`, `deidentify.py`, `test_app_screens.py`, `test_batch.py`, `test_deid_regressions.py`, `run_eval.py`, `app.py`, `test_deid_pipeline.py`, `DeidentificationError`, `extract_text`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `FormType` connect `FormType` to `test_assemble_pipeline.py`, `EncounterFacts`, `schema.py`, `build_dataset.py`, `test_train_and_grammar.py`, `validators.py`, `test_eval.py`, `run_eval.py`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._