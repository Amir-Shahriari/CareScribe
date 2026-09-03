# Graph Report - medgpt  (2026-09-04)

## Corpus Check
- 186 files · ~151,318 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2622 nodes · 5005 edges · 158 communities (136 shown, 22 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 98 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6908f556`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- candidate_residuals
- field_grammar
- build_dataset.py
- generation_status
- EncounterType
- Reference: verified template structure
- template_ingest.py
- test_docx_roundtrip.py
- test_app.py
- schema.py
- test_generation.py
- test_template_ingest.py
- Local clinical LLM fine-tune — design
- test_patients.py
- devDependencies
- test_app_screens.py
- model_setup.py
- test_train_and_grammar.py
- test_reasoning_strip.py
- get_form_spec
- test_desktop_packaging.py
- test_clinical_forms_generate.py
- test_cloud_client.py
- Clinic reference library — design
- Document
- deidentify
- components.py
- compilerOptions
- test_deid_regressions.py
- deidentify.py
- assert_deidentified
- extract_text
- Architecture
- test_stress_corpus.py
- combine_sources
- test_batch.py
- FormType
- CareScribe — design system
- make_icon.py
- expand_name_variants
- test_exemplars.py
- app.py
- ollama_client.py
- run_app.py
- test_buildinfo.py
- docx_redact.py
- highlight_review
- available_forms
- blocking_reason
- mapping.py
- Model Card for phi35-v1
- Installing CareScribe
- EncounterFacts
- Clinic-uploaded clinical form templates — design
- Changelog
- Report templates (SOAP / GP letter / discharge / custom)
- Outpatient Respiratory Clinic Letter (doc03)
- App.tsx
- Reference: verified against the real codebase
- swarm-pipeline.md
- train/__init__.py
- Ward 7B Nursing Handover (doc04)
- inject
- make_sample_docs.py
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
- clinical_forms.py
- desktop.py
- normalise_type
- Cloud generation transport (`CloudBackend`) — design
- test_reference_library.py
- merge_and_convert.sh
- GLiNER Deliberately Uninstalled
- run_eval.py
- Sample Source Documents README
- Recurring fictional staff roster (e.g. A. Whitfield) across documents
- Lightweight review UX for de-identification — design
- test_deid_pipeline.py
- review_spans
- exemplars.py
- NoEgress
- Patient records store — design
- test_generator_backend.py
- test_review_gate.py
- test_backend_overrides.py
- load_documents
- test_generation_setup.py
- CareScribe clinical drafting model — model card
- load_settings
- BM25
- <id> — <title>
- analyze
- backends.py
- LLM backend flexibility + realistic test corpus + full-pipeline validation
- verify_frozen.py
- Per-field retrieval planner — design
- components/__init__.py
- test_build_dataset.py
- batch.py
- Evaluation report
- compilerOptions
- patients.py
- Generation backend selection order (Ollama > built-in GGUF > Cloud)
- AGENTS.md — rules for automated coding agents in this repo
- Task board
- Global Constraints
- assign_placeholders
- finetune/
- resolve_placeholder
- load_protected_terms
- reference_library.py
- _build_analyzer
- get_analyzer
- finetune/__init__.py
- integrate/__init__.py
- test_mapping.py
- parse_fields
- medgpt-finetune
- test_letterhead_address_leak.py
- render_patient_bar
- plan
- carenotes.py
- render_clinical_form_panel
- eval/__init__.py
- is_model_present
- CareScribe site
- assemble/__init__.py
- residual_scan
- _run
- tsconfig.json
- review_spans.py
- render_refinement
- safe_stem
- BackendError
- reidentify
- applog.py
- normalise_action
- test_the_whole_deid_path_works_with_no_model_at_all
- test_clinical_forms.py
- test_app_clinical_forms.py
- theme.py
- wipe_phi
- patients_root
- _store

## God Nodes (most connected - your core abstractions)
1. `deidentify()` - 84 edges
2. `EncounterFacts` - 49 edges
3. `get_form_spec()` - 47 edges
4. `FormType` - 43 edges
5. `Document` - 42 edges
6. `residual_scan()` - 34 edges
7. `generate_document()` - 30 edges
8. `create_patient()` - 28 edges
9. `write_approved()` - 26 edges
10. `extract_text()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `Stable per-entity placeholder scheme` --semantically_similar_to--> `build_prompt()`  [INFERRED] [semantically similar]
  README.md → carescribe/core/clinical_forms.py
- `pdfplumber` --references--> `extract_text()`  [INFERRED]
  requirements.txt → carescribe/core/ingest.py
- `python-docx` --references--> `extract_text()`  [INFERRED]
  requirements.txt → carescribe/core/ingest.py
- `Section-path field key slug scheme` --rationale_for--> `slugify()`  [EXTRACTED]
  docs/superpowers/specs/2026-08-13-clinical-forms-design.md → carescribe/core/clinical_forms.py
- `presidio-analyzer` --references--> `_build_analyzer()`  [INFERRED]
  requirements.txt → carescribe/core/deidentify.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **README report-templates table implemented by prompt files** — readme_report_templates, carescribe_prompts_care_notes_soap_template, carescribe_prompts_clinic_letter_template, carescribe_prompts_discharge_summary_template, carescribe_prompts_custom_template [INFERRED 0.85]
- **Privacy-invariant enforcement chain (assert, sweep, write, integrity)** — carescribe_core_carenotes_assert_deidentified, carescribe_core_deidentify_residual_scan, carescribe_core_batch_write_approved, carescribe_core_mapping_check_placeholder_integrity [EXTRACTED 1.00]
- **Clinical form generation pipeline (combine -> prompt -> generate -> parse -> fill)** — carescribe_core_clinical_forms_combine_sources, carescribe_core_clinical_forms_build_prompt, carescribe_core_clinical_forms_generate_form_document, carescribe_core_clinical_forms_parse_fields, carescribe_core_clinical_forms_fill_template [EXTRACTED 1.00]
- **Sample docs that combine into one fictional client's clinical-forms test flow** — sample_documents_readme_01_gp_referral_letter, sample_documents_readme_02_biopsychosocial_intake_notes, sample_documents_readme_03_session_log_progress_notes, sample_documents_readme_04_treatment_review_source, sample_documents_readme_jordan_whitfield [EXTRACTED 1.00]
- **Fictional patients sharing the same reused NHS number across documents** — stress_corpus_doc01_mohammed_al_rashid, stress_corpus_doc02_margaret_elizabeth_chen, stress_corpus_doc05_elspeth_mackenzie_ford, stress_corpus_doc06_priya_venkataraman, stress_corpus_doc09_tomasz_wisniewski, stress_corpus_shared_nhs_number [INFERRED 0.85]
- **Documents sharing the recurring fictional staff roster (e.g. A. Whitfield, R. Patel)** — stress_corpus_doc01_community_mh_letter, stress_corpus_doc02_cardiology_discharge, stress_corpus_doc04_ward_handover, stress_corpus_doc07_cmht_family_review, stress_corpus_doc10_mha_assessment, stress_corpus_recurring_staff_roster [INFERRED 0.75]

## Communities (158 total, 22 thin omitted)

### Community 0 - "candidate_residuals"
Cohesion: 0.14
Nodes (17): candidate_residuals(), Flag, _is_common(), outstanding(), _placeholder_ranges(), Residual-candidate highlighter — where the reviewer's eye should go first. This…, One span worth a second look, with its offsets in the redacted text., Identity for dismissal — per value, so one decision covers repeats. (+9 more)

### Community 1 - "field_grammar"
Cohesion: 0.14
Nodes (21): _body_rules(), compile_grammar(), field_grammar(), _lit(), note_grammar(), _placeholder_rule(), GBNF grammars for constrained local decoding — a structural guarantee on top of…, Compile a GBNF string with llama-cpp-python, or return ``None``. Never raises:… (+13 more)

### Community 2 - "build_dataset.py"
Cohesion: 0.10
Nodes (40): build(), _fallback_inject(), _load_datagen_config(), main(), Path, End-to-end: sampled encounters -> validated SFT pairs + manifest. python -m…, Return ``{"pairs": [...], "kept": k, "dropped": d, "reasons": {...}}``.…, Fill ``[[TOKEN]]`` slots with simple fake values. Used only until… (+32 more)

### Community 3 - "generation_status"
Cohesion: 0.11
Nodes (19): cache_data, generation_status(), _llama_runtime_available(), missing_reason(), Is generation usable right now, and if not, what should the user do? Kept…, One plain sentence on why generation is not available yet., Which generation backends are usable at this moment., Which backend would actually be used, matching the backend ladder. (+11 more)

### Community 4 - "EncounterType"
Cohesion: 0.13
Nodes (25): Choice, Any, Random, Range, Small seeded-sampling primitives shared by the vignette sampler. A vignette is…, Pick one of ``options`` uniformly., Pick one of ``options`` by matching ``weights``., An integer in ``[low, high]``, optionally rendered with ``unit``. (+17 more)

### Community 5 - "Reference: verified template structure"
Cohesion: 0.10
Nodes (20): carescribe/core/clinical_forms.py (module), Refine prompt (clinical form, marker-preserving), Refine prompt (free-form draft revision), Clinical Form Generation (APS Templates) Implementation Plan, Global Constraints, Reference: verified template structure, Self-Review Notes (for the implementer), Task 10: End-to-end generation glue (`generate_form_document`, `refine_form_document`, `render_preview`) (+12 more)

### Community 6 - "template_ingest.py"
Cohesion: 0.15
Nodes (26): slugify(), delete_template(), _find_grids(), _infer_header(), _is_blank_row(), load_user_spec(), _match_header(), _parse_document() (+18 more)

### Community 7 - "test_docx_roundtrip.py"
Cohesion: 0.08
Nodes (32): approved_map(), document_has_text_boxes(), The reviewer-approved ``{literal: placeholder}`` map for the Word pass. This is…, True if a .docx holds text this redaction pass cannot reach., extract_text(), has_unreachable_text(), True if the document holds text this module cannot reach. Text boxes,…, Flatten a docx to text (body + tables + headers/footers) for a residual scan. (+24 more)

### Community 8 - "test_app.py"
Cohesion: 0.10
Nodes (40): analysed_batch(), _clean_auto_doc(), data_editors(), loaded_batch(), _NullBackend, AppTest, UI checks for the batch review app via Streamlit's AppTest. No server of any…, After the read-and-confirmed tick, a clean auto-confidence document has nothing… (+32 more)

### Community 9 - "schema.py"
Cohesion: 0.09
Nodes (35): BaseModel, field_validator, _blank_for(), expand(), Random, Turn vignettes into `EncounterFacts` instances with a seeded RNG. `expand`…, Yield ``n`` `EncounterFacts`, deterministic for a given ``seed``., Build one `EncounterFacts` from a vignette. With ``gap_probability`` > 0, each… (+27 more)

### Community 10 - "test_generation.py"
Cohesion: 0.07
Nodes (37): finalise(), Build the user prompt for one template with the source text embedded., Re-identify a draft locally and refuse to hand back a leaky document. Returns…, render_prompt(), check_placeholder_integrity(), Compare a draft's bracketed tokens against the placeholders it should use. An…, Local re-identification of a generated draft. Returns ``(text, unresolved)``.…, reidentify_document() (+29 more)

### Community 11 - "test_template_ingest.py"
Cohesion: 0.15
Nodes (18): fill_parsed_template(), Fill an in-memory copy of ``original_docx`` from ``spec``'s anchors. A thin…, _anchors(), _build_synthetic(), _merge_full_width(), fixture, parametrize, A clinic can add its own table-based .docx form. The generic parser must infer… (+10 more)

### Community 12 - "Local clinical LLM fine-tune — design"
Cohesion: 0.06
Nodes (30): 10. Workstream E — integration, 11. What needs a human / external resource, 12. Milestones (testable deliverables), 13. Testing strategy, 1. Goal, 2. Constraints inherited from CareScribe, 3. Approach (selected), 4. Base model (+22 more)

### Community 13 - "test_patients.py"
Cohesion: 0.16
Nodes (22): create_patient(), list_patients(), patient_output_dir(), Where this patient's approved de-identified artefacts are filed., Create a patient folder and roster entry. Returns the new record., Every readable patient, sorted by name (case-insensitive) then id. A folder…, parametrize, The per-patient records store. `patients.py` owns no detection logic — it is… (+14 more)

### Community 14 - "devDependencies"
Cohesion: 0.06
Nodes (35): lucide-react, oxlint, react, react-dom, dependencies, lucide-react, react, react-dom (+27 more)

### Community 15 - "test_app_screens.py"
Cohesion: 0.18
Nodes (20): Synthetic test data for the de-identification regression suite. EVERYTHING HERE…, Fully Fabricated Test Data, Synthetic Discharge Summary Fixture, Line-break-split Name Case, Precision Cases In Fixture, Recall Cases In Fixture, _analysed(), _approved() (+12 more)

### Community 16 - "model_setup.py"
Cohesion: 0.16
Nodes (18): clear_partial_download(), download_model(), _free_bytes(), model_destination(), ModelSetupError, Progress, pull_ollama_model(), Path (+10 more)

### Community 17 - "test_train_and_grammar.py"
Cohesion: 0.09
Nodes (32): build_grammar(), A GBNF grammar string for one form + this document's placeholder set. Delegates…, train/ config + modelcard + dpo rejection, and integrate/grammar., test_build_preference_rows_shapes_dpo_data(), test_grammar_pins_headings_and_constrains_brackets(), test_grammar_with_no_placeholders_forbids_brackets_entirely(), test_load_pairs_round_trips_jsonl(), test_make_rejected_applies_exactly_one_corruption() (+24 more)

### Community 18 - "test_reasoning_strip.py"
Cohesion: 0.12
Nodes (25): Remove a model's reasoning monologue from a finished draft. Idempotent. Text…, strip_reasoning(), _drain(), Generation must hand the clinician the finished document, not the model's…, A backend that prefixes its answer with a planning monologue., ReasoningBackend, test_a_bare_closing_tag_takes_everything_before_it(), test_a_wellformed_think_block_is_removed() (+17 more)

### Community 19 - "get_form_spec"
Cohesion: 0.15
Nodes (24): _clear_cell(), ClinicalFormError, _dedupe_row(), _fill_cell(), _fill_header_cell(), fill_template(), get_form_spec(), RuntimeError (+16 more)

### Community 20 - "test_desktop_packaging.py"
Cohesion: 0.08
Nodes (19): available_ram_gb(), ram_verdict(), Total system RAM in GB, or 0.0 if it cannot be determined., Whether this machine can run the bundled local model. Returns a verdict rather…, _cloud_off(), fixture, The packaging invariants: what the desktop app may and may not do. Packaging is…, No key may be committed, defaulted, or written anywhere. (+11 more)

### Community 21 - "test_clinical_forms_generate.py"
Cohesion: 0.23
Nodes (9): Human-readable rendering for display only — the marker text in ``draft_state``…, render_preview(), Captures exactly what generation handed the model — mirrors the fixture in…, RecordingBackend, test_generate_form_document_refuses_a_real_identifier(), test_generate_form_document_sends_the_field_marker_prompt(), test_refine_form_document_preserves_markers_instruction(), test_render_preview_defaults_missing_value() (+1 more)

### Community 22 - "test_cloud_client.py"
Cohesion: 0.10
Nodes (25): CloudError, _config(), _post(), RuntimeError, Transport for the optional cloud generation backend. Reached only when a…, Yield the payload of each ``data:`` line in an SSE stream., Stream a completion from the configured cloud provider, yielding text. Raises…, A recoverable problem talking to the configured cloud provider. (+17 more)

### Community 23 - "Clinic reference library — design"
Cohesion: 0.17
Nodes (11): `app.py`, Architecture, Clinic reference library — design, Decision, Follow-ups (not blocking), New `core/reference_library.py`, Privacy / safety, Problem (+3 more)

### Community 24 - "Document"
Cohesion: 0.11
Nodes (34): active_output_dir(), active_patient_id(), document_flags(), entity_confirmed(), entity_frame(), flag_dismissals(), _model_card_path(), Path (+26 more)

### Community 25 - "deidentify"
Cohesion: 0.09
Nodes (37): deidentify(), Run the full local pipeline over one document. CPU-only and offline: no model…, parametrize, Regression: public crisis-line names are not identifiers and must not be…, The allow-list entry is the helpline name only — a real name beside it still…, test_a_crisis_line_name_survives_deidentification(), test_a_person_named_near_a_crisis_line_is_still_redacted(), test_crisis_line_name_and_number_both_survive_in_context() (+29 more)

### Community 26 - "components.py"
Cohesion: 0.12
Nodes (26): chip(), detection_layer(), _esc(), hero(), icon(), model_label(), privacy_line(), HTML-string UI helpers for CareScribe. Every function returns a string to hand… (+18 more)

### Community 27 - "compilerOptions"
Cohesion: 0.08
Nodes (23): DOM, src, vite/client, compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx (+15 more)

### Community 28 - "test_deid_regressions.py"
Cohesion: 0.06
Nodes (41): _header_footer_bounds(), _plausible_surname(), Character ranges of the document's opening and closing lines., True if the trailing token of an initial+surname reads like a real name.…, Layer 1: deterministic regex detections over ``text``., structured_spans(), Layer 1 alone must still catch every purely structured identifier., A bare digit run is a lab value; only a labelled one is a record number. (+33 more)

### Community 29 - "deidentify.py"
Cohesion: 0.07
Nodes (46): available_models(), classify_person(), _collapse_facility_subsets(), _collapse_person_subsets(), date_span_wanted(), _has_contact_anchor(), _has_identity_anchor(), _is_acronym() (+38 more)

### Community 30 - "assert_deidentified"
Cohesion: 0.16
Nodes (14): assert_deidentified(), CloudBackend (unwired seam), True only when ``needle`` occurs in ``haystack`` as a whole token run. Both are…, Refuse to send anything carrying a value from the identity mapping. A cheap,…, _value_present(), System prompt (anti-fabrication rules), Optional cloud generation path (off by default), Two required env vars (CARESCRIBE_CLOUD_PROVIDER / CARESCRIBE_CLOUD_API_KEY) (+6 more)

### Community 31 - "extract_text"
Cohesion: 0.07
Nodes (44): _extract_docx(), _extract_pdf(), extract_text(), _extract_txt(), IngestError, normalise_line_endings(), Any, RuntimeError (+36 more)

### Community 32 - "Architecture"
Cohesion: 0.13
Nodes (14): 1. Template assets, 2. Form spec extraction, 3. Header fields (practitioner-entered), 4. Multi-document source combination, 5. Generation, 6. Review, 7. Export, 8. UI (`app.py`, Step 5) (+6 more)

### Community 33 - "test_stress_corpus.py"
Cohesion: 0.05
Nodes (48): answer_key.json, Community MH Discharge Letter (doc01), Mohammed Al-Rashid ('Mo'), Cardiology Discharge Summary (doc02), Margaret Elizabeth Chen ('Peggy'), Elspeth Mackenzie-Ford ('Ellie'), GP Referral Letter (doc05), Priya Venkataraman (+40 more)

### Community 34 - "combine_sources"
Cohesion: 0.21
Nodes (13): combine_sources(), Concatenate several documents' de-identified text into one source. ``sources``…, Regression test for Finding 3: raw filename must not leak into model-facing…, Regression test for Finding 1: cap at 26 documents (A-Z)., Regression test for Finding 1: prefixed placeholders must match PLACEHOLDER_RE.…, Regression test for Finding 2: text and map rewrites must be consistent. A…, test_combine_sources_no_filename_in_output(), test_combine_sources_non_standard_placeholder_consistency() (+5 more)

### Community 35 - "test_batch.py"
Cohesion: 0.10
Nodes (28): BatchError, list_folder(), RuntimeError, Return the supported documents in ``folder``, sorted by name. Non-recursive on…, Findings from the safety sweep, minus the ones the reviewer has cleared. A…, Write approved de-identified text to the output folder. Re-runs the safety…, Raised for input-folder and output-write problems., sweep() (+20 more)

### Community 36 - "FormType"
Cohesion: 0.12
Nodes (21): build_messages(), Care note templates. Every template shares the same hard rule: the input is…, Return ``(system, user)`` for a template label and de-identified document., Enum, FormType, The output form a training example asks the model to fill., GBNF grammars for constrained decoding — the belt-and-braces guarantee on top…, build_messages() (+13 more)

### Community 37 - "CareScribe — design system"
Cohesion: 0.20
Nodes (9): Browser surfaces, CareScribe — design system, Components (`carescribe/ui/components.py`), Direction, Palette, Sidebar order, Space & shape, Type (+1 more)

### Community 38 - "make_icon.py"
Cohesion: 0.29
Nodes (12): Image, _load_font(), main(), Path, Generate CareScribe's placeholder icon. A real icon is a design job; this…, The first usable bold face, or ``None`` if none of them load., A rounded square with "CS" centred on it., macOS only. Silently skipped elsewhere — the .app is built on a Mac. (+4 more)

### Community 39 - "expand_name_variants"
Cohesion: 0.07
Nodes (30): _collapse_person_identities(), True for a person row whose role is known (patient / relative / clinician)., Collapse every written form of one person onto a single entity row.…, REDACT_INPROSE_DATES flag, _specific_person_type(), canonical_person_key(), expand_name_variants(), expand_org_variants (Layer 4 — variant expansion) (+22 more)

### Community 40 - "test_exemplars.py"
Cohesion: 0.14
Nodes (18): add_exemplar(), count(), Append one de-identified draft as a house-style exemplar. Refuses…, fixture, House-style exemplar store + BM25 retrieval, and its hook into the clinical-…, _RecordingBackend, _store(), test_add_refuses_a_value_that_still_holds_an_identifier() (+10 more)

### Community 41 - "app.py"
Cohesion: 0.15
Nodes (21): current(), documents(), ingest_sources(), main(), _model_card_dialog(), _pipeline_step(), privacy_indicator(), _privacy_state() (+13 more)

### Community 42 - "ollama_client.py"
Cohesion: 0.15
Nodes (20): default_model(), generate(), is_up(), list_models(), missing_model_message(), OllamaError, RuntimeError, Local Ollama client — pinned to the loopback interface. Generation is the first… (+12 more)

### Community 43 - "run_app.py"
Cohesion: 0.16
Nodes (17): Popen, close_splash(), _fatal(), free_port(), main(), _no_window_kwargs(), CareScribe desktop launcher — the app's entry point. Starts the Streamlit…, Dismiss the bootloader splash, if this is a frozen build that has one.… (+9 more)

### Community 44 - "test_buildinfo.py"
Cohesion: 0.24
Nodes (10): build_info(), Build information for CareScribe., Return standard HTTP User-Agent string., Return application identity and version., user_agent(), Tests for buildinfo module., Test that user_agent returns correct format., Test that build_info returns correct name and version. (+2 more)

### Community 45 - "docx_redact.py"
Cohesion: 0.19
Nodes (15): apply_redactions(), _delete_prefix(), _iter_groups(), _iter_paragraphs(), _norm(), Structure-preserving .docx redaction. apply_redactions(path_in, path_out,…, Redact a literal split across a paragraph boundary (wrapped name)., Delete the leading text of a paragraph matching normalized_prefix (ws-… (+7 more)

### Community 46 - "highlight_review"
Cohesion: 0.24
Nodes (9): highlight_review(), Click-to-redact highlighted text. Renders already-redacted (or already-flagged)…, Render ``html`` and return the ``data-span-id`` of the last click. Returns…, _frontend_path(), Path, Offline-first: nothing in this file may fetch from a CDN., test_frontend_file_exists(), test_frontend_has_no_external_script_or_link_tags() (+1 more)

### Community 47 - "available_forms"
Cohesion: 0.20
Nodes (10): available_forms(), (form_id, title) pairs — bundled forms first, then clinic-uploaded ones., skipif, test_no_field_key_collides_within_a_spec(), parametrize, Deterministic stand-in for a real generation backend., _StubBackend, test_combined_sources_generate_every_form_type_with_a_stub_backend() (+2 more)

### Community 48 - "blocking_reason"
Cohesion: 0.17
Nodes (11): blocking_reason(), The approval gate. Only the **authoritative safety sweep** blocks approval. A…, Why Approve is disabled, in one short line. Empty string means it isn't.…, Low-confidence redactions are already in place; the permissive flags are…, The streamlined gate: a permissive flag the reviewer left untouched does not…, test_advisory_spans_do_not_block_approval(), test_an_advisory_flag_alone_no_longer_blocks_approval(), test_approval_is_blocked_while_the_sweep_has_findings() (+3 more)

### Community 49 - "mapping.py"
Cohesion: 0.12
Nodes (20): expand_facility_variants(), find_known_as(), find_spans(), _form_pattern(), Issue, Pattern, In-memory PII <-> placeholder mapping. This module is deliberately pure: it…, Return the full organisation name plus short forms. "St. Aidan's General… (+12 more)

### Community 50 - "Model Card for phi35-v1"
Cohesion: 0.33
Nodes (5): Citations, Framework versions, Model Card for phi35-v1, Quick start, Training procedure

### Community 51 - "Installing CareScribe"
Cohesion: 0.22
Nodes (8): Before you start, First launch, If it will not start, Installing CareScribe, macOS, Updating, Where your files go, Windows

### Community 52 - "EncounterFacts"
Cohesion: 0.08
Nodes (49): build_target(), _care_plan(), _field_content(), _handover(), _history_lines(), _med_line(), _objective_lines(), _plan_lines() (+41 more)

### Community 53 - "Clinic-uploaded clinical form templates — design"
Cohesion: 0.18
Nodes (10): Architecture, Clinic-uploaded clinical form templates — design, Follow-ups (not blocking), New module `core/template_ingest.py`, Persistence, Problem, Registry integration (`core/clinical_forms.py`), Scope (+2 more)

### Community 54 - "Changelog"
Cohesion: 0.29
Nodes (6): [0.1.0] - 2026-09-01, Added, Added, Changelog, Fixed, [Unreleased]

### Community 55 - "Report templates (SOAP / GP letter / discharge / custom)"
Cohesion: 0.40
Nodes (5): SOAP care note prompt template, GP clinic letter prompt template, Custom (clinician house format) prompt template, Discharge summary prompt template, Report templates (SOAP / GP letter / discharge / custom)

### Community 56 - "Outpatient Respiratory Clinic Letter (doc03)"
Cohesion: 0.40
Nodes (5): Ngozi Okafor, Outpatient Respiratory Clinic Letter (doc03), Attendee list pattern, Header town + county pattern, Record-number label shapes (three variants)

### Community 57 - "App.tsx"
Cohesion: 0.09
Nodes (12): oxc, react, typescript, warn, plugins, rules, react/only-export-components, react/rules-of-hooks (+4 more)

### Community 58 - "Reference: verified against the real codebase"
Cohesion: 0.15
Nodes (12): Global Constraints, Lightweight Review UX Redesign Implementation Plan, Reference: verified against the real codebase, Self-Review Notes, Task 1: Confidence tiering in the detection pipeline, Task 2: Unified review-span module, Task 3: Click-to-redact custom Streamlit component, Task 4: Simplify `review_checklist.py` to a two-input gate (+4 more)

### Community 61 - "Ward 7B Nursing Handover (doc04)"
Cohesion: 0.50
Nodes (4): Aiden Braithwaite, Ward 7B Nursing Handover (doc04), 'A. Surname' against full name in header, Labelled date fields

### Community 62 - "inject"
Cohesion: 0.15
Nodes (26): _collect(), _date(), _dob(), inject(), _make(), _mrn(), _name(), nhs_number() (+18 more)

### Community 63 - "make_sample_docs.py"
Cohesion: 0.21
Nodes (21): build_case_conference_note(), build_discharge_summary(), build_intake_notes(), build_referral_letter(), build_risk_assessment(), build_session_log(), build_treatment_review_source(), _grid_table() (+13 more)

### Community 64 - "test_clinical_form_templates.py"
Cohesion: 0.50
Nodes (3): parametrize, The three bundled APS templates load and match the structure this feature's…, test_bundled_template_shape()

### Community 73 - "generate_document"
Cohesion: 0.08
Nodes (38): assert_no_residual_identifiers(), CareNoteError, generate_document(), load_prompt(), RuntimeError, The shared preamble — role, anti-fabrication rules, placeholder rules., Refuse to send text the residual sweep still flags. :func:`assert_deidentified`…, Stream a drafted document from approved de-identified text. ``phi_values`` is… (+30 more)

### Community 74 - "House-style exemplar retrieval — design"
Cohesion: 0.18
Nodes (10): `app.py`, Architecture, `core/clinical_forms.py`, Follow-ups (not blocking), House-style exemplar retrieval — design, New module `core/exemplars.py`, Privacy, Problem (+2 more)

### Community 76 - "clinical_forms.py"
Cohesion: 0.17
Nodes (21): _biopsychosocial_spec(), build_prompt(), _fill_cell_after_label(), _form_grammar(), FormField, FormSpec, generate_form_document(), _grid_fields() (+13 more)

### Community 77 - "desktop.py"
Cohesion: 0.14
Nodes (27): app_data_dir(), bundle_root(), ensure_dirs(), find_local_model(), is_frozen(), _model_search_dirs(), models_dir(), output_dir() (+19 more)

### Community 78 - "normalise_type"
Cohesion: 0.40
Nodes (5): normalise_type(), Coerce a model-supplied type string onto the canonical list., parametrize, test_normalise_type(), test_reidentify_never_crashes()

### Community 80 - "Cloud generation transport (`CloudBackend`) — design"
Cohesion: 0.20
Nodes (9): Architecture, Cloud generation transport (`CloudBackend`) — design, `core/backends.py`, Follow-ups (not blocking), New module `core/cloud_client.py`, Privacy properties (unchanged, inherited), Problem, Scope (+1 more)

### Community 81 - "test_reference_library.py"
Cohesion: 0.15
Nodes (22): add_file(), is_empty(), ``(filename, paragraph_count)`` per loaded reference file., Top-``k`` reference passages for ``query`` at ``granularity``. BM25, ``score >…, Store an uploaded reference file. Returns the stored filename., ReferenceHit, search(), sources() (+14 more)

### Community 84 - "run_eval.py"
Cohesion: 0.08
Nodes (47): aggregate(), DraftScore, _headings(), _lexical_overlap(), _order_agreement(), The four target metrics, scored per draft and reducible to a mean. Format,…, Mean of each metric over ``scores`` (style_match over styled drafts only)., Fraction of ``a``'s headings that appear in ``b`` in the same relative order. (+39 more)

### Community 87 - "Lightweight review UX for de-identification — design"
Cohesion: 0.14
Nodes (13): 1. Confidence tiering (drives what gets a click at all), 2. One primary review view, not three, 3. The click-to-redact component, 4. Attestation & audit trail, 5. Crash-risk fixes, Architecture, Current state (for reference), Goals (+5 more)

### Community 88 - "test_deid_pipeline.py"
Cohesion: 0.04
Nodes (57): add_manual_entity(), DeidentificationError, DeidResult, RuntimeError, Re-derive redacted text and the PHI map from a reviewer-edited table. Called…, Add an identifier the tools missed and immediately re-redact. The new value…, Raised when de-identification can't run at all., Everything the de-identification stage produces for one document. (+49 more)

### Community 89 - "review_spans"
Cohesion: 0.32
Nodes (12): Every clickable span in ``redacted_text``, in reading order. ``confirmed`` is…, review_spans(), _entity(), action=Keep means the reviewer already decided — nothing to click on the…, test_a_confirmed_entity_produces_no_span(), test_a_kept_entity_produces_no_entity_span(), test_auto_confidence_entities_produce_no_span(), test_dismissed_residual_flags_are_excluded() (+4 more)

### Community 90 - "exemplars.py"
Cohesion: 0.16
Nodes (16): _dir(), _load(), _path(), Path, House-style exemplar retrieval for clinical-form generation. A clinic…, Top-``k`` stored values for ``field_key``, ranked by BM25 against ``query``., ``{field_key: [examples]}`` for every key that has at least one exemplar., retrieve() (+8 more)

### Community 91 - "NoEgress"
Cohesion: 0.12
Nodes (11): NoEgress, Fails the test if anything opens a non-loopback socket. Loopback is allowed:…, Stands in for a model so the egress test does not need one installed., StubBackend, The load that used to hang on a captive portal must not exist., Reset the cache so the guard covers a genuine first load., The reported hang: no model, so something tries to download it., test_a_missing_model_fails_loudly_instead_of_fetching() (+3 more)

### Community 92 - "Patient records store — design"
Cohesion: 0.11
Nodes (17): 10. Rejected alternatives, 1. Goal, 2. Constraints inherited from CareScribe, 3. The one deliberate change to the privacy posture, 4. Storage layout, 5.1 `carescribe/core/desktop.py`, 5.2 `carescribe/core/patients.py` (new), 5.3 `carescribe/core/batch.py` (+9 more)

### Community 93 - "test_generator_backend.py"
Cohesion: 0.11
Nodes (19): GeneratorBackend, get_backend(), OllamaBackend, OpenAICompatibleBackend, TemplateBackend, Test that TemplateBackend properly renders facts in proforma style, Test that TemplateBackend properly renders facts in prose style, Test that TemplateBackend is deterministic - same input gives same output (+11 more)

### Community 94 - "test_review_gate.py"
Cohesion: 0.13
Nodes (15): _flag_values(), fixture, parametrize, The reviewer gate: candidate highlighting, the adaptive checklist, and the no-…, The real test: nothing the corpus calls an identifier may appear., A dismissal key holds the span text, so it must be wiped with the rest., Five-digit rule must not fire on "10mg" style clinical numbers., record() (+7 more)

### Community 95 - "test_backend_overrides.py"
Cohesion: 0.10
Nodes (26): Pick a backend. Returns ``(kind, backend, label)``. ``prefer`` lets the UI…, select_backend(), OllamaBackend, Local generation through the loopback-pinned Ollama daemon., _backend_with_fake_model(), _FakeModel, _raising_stream(), The happy path must keep working: finish_reason 'stop' yields the text with no… (+18 more)

### Community 96 - "load_documents"
Cohesion: 0.14
Nodes (17): analyze_document(), load_documents(), Extract text from uploads or paths. Returns ``(documents, errors)``. One…, Run the de-identification layers over one document, in place., FakeUpload, Stands in for a Streamlit UploadedFile., test_analyze_document_populates_state(), test_duplicate_filenames_are_reported() (+9 more)

### Community 97 - "test_generation_setup.py"
Cohesion: 0.08
Nodes (18): _cloud_off(), _fresh_generation_status_cache(), mapping_module(), fixture, First-run generation setup: never an empty panel, and the egress line held. The…, The one outbound path must not be reachable from the de-id flow., A captive portal returns HTML with a plausible size., generation_status() is now @st.cache_data(ttl=5) — a process-global cache keyed… (+10 more)

### Community 98 - "CareScribe clinical drafting model — model card"
Cohesion: 0.40
Nodes (4): CareScribe clinical drafting model — model card, Evaluation, Known limitations, Training data

### Community 99 - "load_settings"
Cohesion: 0.25
Nodes (15): load_settings(), _path(), Persisted app settings — which generation backend/model/temperature to use.…, Read persisted settings. A missing or unreadable file yields defaults., Persist non-secret settings, creating the app data dir if needed., save_settings(), Settings, test_load_settings_coerces_stringy_temperature() (+7 more)

### Community 100 - "BM25"
Cohesion: 0.18
Nodes (9): ExemplarError, RuntimeError, Raised when an exemplar cannot be stored — e.g. it still holds an identifier., RuntimeError, Raised when a reference file cannot be stored., ReferenceError, BM25, Okapi BM25. ``documents`` is a list of token lists. (+1 more)

### Community 101 - "<id> — <title>"
Cohesion: 0.29
Nodes (6): Acceptance criteria, Do NOT touch, Files in scope, Goal, <id> — <title>, Notes

### Community 102 - "analyze"
Cohesion: 0.09
Nodes (24): analyze(), _crosses_paragraph_break(), flatten_lines(), gliner_spans(), ner_spans(), Layer 2: Presidio/spaCy detections, mapped onto CareScribe entity types.…, Layer 3: GLiNER detections, or an empty list when it isn't installed., Run every enabled layer over ``text`` and return reviewable entities. Each… (+16 more)

### Community 103 - "backends.py"
Cohesion: 0.14
Nodes (18): cloud_enabled(), cloud_key_present(), cloud_provider(), CloudBackend, describe_backends(), Generation backends, layered so the app works with nothing installed. Selection…, The configured provider name, or "" when cloud generation is off., Cloud generation exists only with BOTH an explicit provider and a key. Two… (+10 more)

### Community 104 - "LLM backend flexibility + realistic test corpus + full-pipeline validation"
Cohesion: 0.20
Nodes (9): A. Backend/settings flexibility, B. Realistic document corpus, C. Full-pipeline validation loop, Design, Goals, LLM backend flexibility + realistic test corpus + full-pipeline validation, Non-goals, Problem (+1 more)

### Community 105 - "verify_frozen.py"
Cohesion: 0.36
Nodes (9): bundled_app_py(), _default_dist(), find_executable(), free_port(), main(), Path, Post-build smoke check: does the frozen CareScribe binary actually start? A…, Locate the frozen entry-point inside a PyInstaller output directory. (+1 more)

### Community 106 - "Per-field retrieval planner — design"
Cohesion: 0.17
Nodes (11): `app.py`, Architecture, `core/reference_library.py`, `core/retrieval_planner.py` (new), `core/text_search.py`, Decision, Follow-ups (not blocking), Per-field retrieval planner — design (+3 more)

### Community 108 - "test_build_dataset.py"
Cohesion: 0.18
Nodes (15): _degrade(), _header(), _lines(), _med(), Random, `EncounterFacts` -> a realistic, messy clinician note (the INPUT side of a…, (section label, lines) in a fixed clinical order, skipping empty sections., A little OCR/casing/spacing noise, sampled. (+7 more)

### Community 109 - "batch.py"
Cohesion: 0.11
Nodes (29): approved_docx_path(), approved_path(), _default_output_dir(), Path, Batch input and approved-output handling. The single module in CareScribe that…, The folder a write lands in — an explicit override, or the default.…, Where the approved de-identified text for ``name`` will be written., The raw bytes behind an upload or a path, without copying it to disk. (+21 more)

### Community 111 - "compilerOptions"
Cohesion: 0.10
Nodes (19): node, vite.config.ts, compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection (+11 more)

### Community 112 - "patients.py"
Cohesion: 0.16
Nodes (23): _clean_name(), get_patient(), _now(), Patient, patient_dir(), PatientError, Path, RuntimeError (+15 more)

### Community 113 - "Generation backend selection order (Ollama > built-in GGUF > Cloud)"
Cohesion: 0.18
Nodes (11): core/model_setup.py (model download, isolated), packaging/build_macos.sh, packaging/build_windows.ps1, packaging/carescribe.iss (Inno Setup script), packaging/make_icon.py, The desktop app (PyInstaller packaging), Generation backend selection order (Ollama > built-in GGUF > Cloud), run_app.py entry point (+3 more)

### Community 114 - "AGENTS.md — rules for automated coding agents in this repo"
Cohesion: 0.40
Nodes (4): AGENTS.md — rules for automated coding agents in this repo, Do, Never, Task spec shape

### Community 115 - "Task board"
Cohesion: 0.11
Nodes (17): App bug the user hit (2026-09-01) — FIXED in `e9bcc3b`, Fine-tune decisions locked (2026-09-01), Fine-tune hardware facts (2026-09-01), Fine-tune progress — cockpit-driven, COMMITTED on integration branch, Local clinical LLM fine-tune (started 2026-09-01), M3–M5 DONE — model trained, evaluated, integrated (2026-09-01), Pipeline incident 2026-09-01 (fixed), Punch-list — "address all 10 issues" (2026-09-02) (+9 more)

### Community 116 - "Global Constraints"
Cohesion: 0.18
Nodes (10): Global Constraints, LLM Backend Flexibility + Realistic Test Corpus Implementation Plan, Task 1: Settings persistence module, Task 2: `select_backend()` explicit model/temperature overrides + Ollama temperature fix, Task 3: Settings panel UI + wiring generation call sites through it, Task 4: Stress corpus expansion — batch 1 (5 documents), Task 5: Stress corpus expansion — batch 2 (5 documents), Task 6: Sample documents expansion (full-pipeline generation exercise) (+2 more)

### Community 117 - "assign_placeholders"
Cohesion: 0.29
Nodes (7): assign_placeholders(), Attach a stable placeholder to each unique entity. A type with exactly one…, assign_placeholders is analyze()'s last step — a silent drop here is permanent., test_assign_placeholders_keeps_confidence(), test_existing_placeholder_is_preserved(), test_multiple_values_get_numbered_placeholders(), test_single_value_gets_a_bare_placeholder()

### Community 118 - "finetune/"
Cohesion: 0.40
Nodes (4): Environment, finetune/, Layout, Milestones

### Community 119 - "resolve_placeholder"
Cohesion: 0.29
Nodes (7): _edit_distance(), Levenshtein distance, short-circuiting once it exceeds ``cap``., Map a possibly-corrupted placeholder onto a known one. Returns the exact token…, resolve_placeholder(), Guessing between [MRN_1] and [MRN_2] would attach the wrong identity., test_ambiguous_placeholder_is_refused_not_guessed(), test_edit_distance_caps_out()

### Community 120 - "load_protected_terms"
Cohesion: 0.29
Nodes (8): _build_protected_pattern(), load_protected_terms(), Path, Pattern, Read the editable allow-list. Blank lines and ``#`` comments are ignored., Re-read the allow-list from disk (the file is meant to be edited by hand)., reload_protected_terms(), test_the_allow_list_is_an_editable_file()

### Community 121 - "reference_library.py"
Cohesion: 0.22
Nodes (14): Add clinic reference files (formulary, pathways, protocols) to a local library.…, _render_reference_uploader(), _all_chunks(), _bounded(), Chunk, _dir(), _files(), _paragraphs() (+6 more)

### Community 122 - "_build_analyzer"
Cohesion: 0.18
Nodes (12): _build_analyzer(), is_frozen_build(), Build a Presidio ``AnalyzerEngine`` over spaCy. Returns (engine, model, error)., pandas, pdfplumber, Pinned Dependencies, presidio-analyzer, python-docx (+4 more)

### Community 123 - "get_analyzer"
Cohesion: 0.12
Nodes (19): cache_resource, load_detection_engine(), Load the NER model once per session, not once per rerun. Streamlit re-runs the…, engine_status(), get_analyzer(), get_gliner(), Return the shared Presidio analyzer, or ``None`` if it can't be built. First…, Return the shared GLiNER model, or ``None`` if it isn't available. Guarded end… (+11 more)

### Community 126 - "test_mapping.py"
Cohesion: 0.20
Nodes (10): dedupe_entities(), Drop blank and duplicate entities, keeping first-seen order and casing.…, Mapping-layer checks: type normalisation, surface forms, and re-identification.…, If ANY occurrence of a value was low-confidence, the whole entity is., test_dedupe_carries_the_keep_action(), test_dedupe_drops_dangerously_short_values(), test_dedupe_entities_defaults_missing_confidence_to_review(), test_dedupe_entities_keeps_confidence() (+2 more)

### Community 127 - "parse_fields"
Cohesion: 0.44
Nodes (9): parse_fields(), Turn the model's marker-delimited output into ``{field_key: text}``. Any field…, _spec(), test_parse_fields_defaults_missing_field_to_not_documented(), test_parse_fields_first_occurrence_wins_on_duplicate_marker(), test_parse_fields_handles_empty_output(), test_parse_fields_happy_path(), test_parse_fields_ignores_unknown_marker_without_raising() (+1 more)

### Community 131 - "test_letterhead_address_leak.py"
Cohesion: 0.31
Nodes (8): _letterhead_line(), parametrize, Regression: an unlabelled letterhead street address leaks in the clear. Found…, The de-identified form of the address/phone letterhead line., The new letterhead rule must not fire on a street word in a sentence., test_a_letterhead_street_address_line_is_taken_whole(), test_street_words_in_prose_are_not_over_redacted(), test_the_sample_letterhead_address_is_fully_redacted()

### Community 132 - "render_patient_bar"
Cohesion: 0.18
Nodes (11): Read-only list of what has been filed for this patient., Pick or create the patient whose folder approved output is filed into. "No…, render_filed_documents(), render_patient_bar(), delete_patient(), filed_documents(), FiledDocument, Remove a patient folder and everything filed in it. (+3 more)

### Community 133 - "plan"
Cohesion: 0.22
Nodes (13): plan(), Protocol, RetrievalPlan, RetrievalPlanner, _field(), Per-field retrieval planning (roadmap item E). The shipped planner is rule-…, test_diagnoses_field_wants_section_reference(), test_medication_field_wants_sentence_level_reference() (+5 more)

### Community 134 - "carenotes.py"
Cohesion: 0.12
Nodes (17): Backend, _ends_mid_tag(), generate_care_note(), Protocol, Care note generation — local, on approved de-identified text only. The contract…, True if ``text`` ends part-way through what could be a reasoning tag., Filter a token stream so a reasoning prefix never reaches the consumer. Buffers…, Prepend the review banner, without duplicating one already there. (+9 more)

### Community 135 - "render_clinical_form_panel"
Cohesion: 0.15
Nodes (17): _draft_state(), _form_draft_state(), Which backend will be used, and the fix if none is available., Shown instead of an empty panel when no model is available yet. An empty…, Option A. The only outbound request the app makes, on an explicit click., Option B. Ollama does the fetching; the request goes to loopback., Generate, refine, re-identify and export — for one approved document. Two…, Let a clinic add its own table-based .docx form to the selector. Parsing and… (+9 more)

### Community 137 - "is_model_present"
Cohesion: 0.50
Nodes (4): is_model_present(), True if a usable model file is already on this computer. This is the marker…, Setup is one-time because the file itself is the state., test_model_presence_is_the_persisted_marker()

### Community 138 - "CareScribe site"
Cohesion: 0.50
Nodes (3): CareScribe site, Local, Notes

### Community 140 - "residual_scan"
Cohesion: 0.10
Nodes (23): Re-scan ALREADY-REDACTED text for anything that still looks identifying. Runs…, residual_scan(), main(), normalise(), Per-document pass/fail report for the stress corpus. python…, Placeholders are the point of the exercise, not leaks., A .txt file read off a Windows disk arrives with CRLF endings. NER tokenises…, test_crlf_and_lf_documents_behave_identically() (+15 more)

### Community 141 - "_run"
Cohesion: 0.60
Nodes (4): AppTest, _run(), test_saving_settings_persists_and_survives_reload(), test_settings_expander_renders_without_error()

### Community 143 - "review_spans.py"
Cohesion: 0.32
Nodes (7): _review_span_style(), _entity_spans(), Unifies the two things a reviewer might still need to act on in one document's…, One clickable span in a document's redacted text., Placeholder occurrences for low-confidence, not-yet-confirmed entities., _residual_spans(), ReviewSpan

### Community 145 - "render_refinement"
Cohesion: 0.13
Nodes (19): _active_backend(), _invalidate_form_export(), Drop any previously re-identified/exportable content — called whenever the…, Resolve the backend to generate with, honouring saved settings. Centralises…, A concrete "it works", rather than asking the clinician to trust a flag., Render a stream token by token so a slow local model looks alive., First-pass generation. The model receives de-identified text only., Follow-up instructions, on de-identified text only. (+11 more)

### Community 146 - "safe_stem"
Cohesion: 0.32
Nodes (8): _as_docx(), The de-identified draft, refinement, re-identification, and exports., Opt-in, local-only substitution of placeholders back to real values., Render generated text to a .docx in memory — nothing touches disk., render_draft(), render_reidentification(), Reduce a filename to a safe output stem — no paths, no surprises., safe_stem()

### Community 147 - "BackendError"
Cohesion: 0.18
Nodes (10): BackendError, LocalGGUFBackend, RuntimeError, True if the runtime and a model file are both present., Raised when a backend cannot be used, with the fix in the message., Shared message for a completion cut off by the token/context budget. A half-…, CPU-only generation from a bundled GGUF via ``llama-cpp-python``. The model is…, _truncation_error() (+2 more)

### Community 148 - "reidentify"
Cohesion: 0.18
Nodes (11): Outcome of a re-identification pass., Swap placeholders back to originals, repairing mangled tokens. Never raises on…, Swap placeholders back to their original values. Thin wrapper over…, reidentify(), reidentify_detailed(), ReidentifyResult, test_empty_map_is_a_no_op(), test_invented_placeholder_is_left_alone() (+3 more)

### Community 149 - "applog.py"
Cohesion: 0.15
Nodes (18): BaseException, ensure_engine_ready(), Load the model at startup, behind a visible spinner. Deliberately not lazy. If…, The last line of defence: a calm message instead of a stack trace. A clinician…, render_unexpected_error(), exception(), get_logger(), log() (+10 more)

### Community 150 - "normalise_action"
Cohesion: 0.40
Nodes (5): build_map(), normalise_action(), Build the placeholder -> original-value map used for re-identification. If two…, Coerce a table cell to :data:`REDACT` or :data:`KEEP`. Defaults to redact., test_kept_rows_are_absent_from_the_map()

### Community 151 - "test_the_whole_deid_path_works_with_no_model_at_all"
Cohesion: 0.40
Nodes (5): _nothing_available(), A fresh PC must still de-identify, review and approve., A fresh PC: no Ollama, no model file, no cloud., test_cloud_alone_counts_as_ready(), test_the_whole_deid_path_works_with_no_model_at_all()

### Community 152 - "test_clinical_forms.py"
Cohesion: 0.24
Nodes (9): _load(), Generic table-row classification: which rows are fields, which are section…, test_biopsychosocial_spec_field_count_and_grid(), test_session_notes_field_walk_finds_nine_fields(), test_session_notes_signature_row_is_excluded(), test_session_notes_spec(), test_treatment_review_header_fields(), test_treatment_review_spec_has_fourteen_fields() (+1 more)

### Community 153 - "test_app_clinical_forms.py"
Cohesion: 0.29
Nodes (7): _form_draft_key(), _header_values_complete(), Pure-logic pieces of the clinical-form UI: the session-state key used to key a…, test_form_draft_key_differs_by_form_or_selection(), test_form_draft_key_is_stable_for_the_same_selection(), test_header_values_complete_requires_every_non_reason_field(), test_invalidate_form_export_drops_stale_resolved_values()

### Community 154 - "theme.py"
Cohesion: 0.33
Nodes (4): CareScribe UI layer — the visual identity, applied over Streamlit. `theme.CSS`…, inject(), CareScribe visual identity — one stylesheet, injected once per rerun. DIRECTION…, Apply the stylesheet. Import Streamlit lazily so the module stays cheap.

### Community 155 - "wipe_phi"
Cohesion: 0.67
Nodes (4): PHI_KEYS (session-state PHI registry), Drop every document, identifier table, and identity map from memory., wipe_phi(), Bug: form_drafts never registered with PHI_KEYS/wipe_phi

### Community 156 - "patients_root"
Cohesion: 0.50
Nodes (4): patients_root(), Root of the records store. ``CARESCRIBE_PATIENTS_DIR`` if set, else…, test_root_defaults_under_app_data_without_the_env(), test_root_follows_the_env_override()

### Community 157 - "_store"
Cohesion: 0.67
Nodes (3): fixture, Point the store at a scratch dir for every test., _store()

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
- **304 isolated node(s):** `medgpt-finetune`, `merge_and_convert.sh script`, `build_dmg.sh script`, `build_macos.sh script`, `$schema` (+299 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

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
- **Why does `inject()` connect `inject` to `build_dataset.py`, `run_eval.py`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `deidentify()` connect `deidentify` to `build_dataset.py`, `test_letterhead_address_leak.py`, `test_app.py`, `residual_scan`, `test_patients.py`, `applog.py`, `normalise_action`, `test_deid_regressions.py`, `deidentify.py`, `extract_text`, `test_stress_corpus.py`, `test_batch.py`, `available_forms`, `mapping.py`, `test_deid_pipeline.py`, `NoEgress`, `load_documents`, `test_generation_setup.py`, `analyze`, `batch.py`, `_build_analyzer`, `get_analyzer`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._