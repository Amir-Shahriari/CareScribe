# Graph Report - medgpt  (2026-09-01)

## Corpus Check
- 157 files · ~122,107 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2173 nodes · 4194 edges · 138 communities (114 shown, 24 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 95 edges (avg confidence: 0.61)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ce895935`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Cardiology Discharge Summary (doc02)
- clinical_forms.py
- build_dataset.py
- schema.py
- batch.py
- Reference: verified template structure
- template_ingest.py
- test_docx_roundtrip.py
- test_app.py
- mapping.py
- check_placeholder_integrity
- test_template_ingest.py
- Local clinical LLM fine-tune — design
- generation_status
- deidentify.py
- test_mapping.py
- model_setup.py
- test_train_and_grammar.py
- backends.py
- fill_template
- test_desktop_packaging.py
- get_form_spec
- test_cloud_client.py
- Clinic reference library — design
- Document
- deidentify
- components.py
- app.py
- core/__init__.py
- stress_corpus/README.md
- assert_deidentified
- BackendError
- Architecture
- test_stress_corpus.py
- combine_sources
- structured_spans
- FormType
- expand_name_variants
- make_icon.py
- rebuild
- exemplars.py
- render_clinical_form_panel
- ollama_client.py
- run_app.py
- test_buildinfo.py
- GP Referral Letter (doc05)
- highlight_review
- test_deid_regressions.py
- generate_form_document
- docx_redact.py
- Model Card for phi35-v1
- Installing CareScribe
- test_validators.py
- Clinic-uploaded clinical form templates — design
- [0.1.0] - 2026-09-01
- Report templates (SOAP / GP letter / discharge / custom)
- Outpatient Respiratory Clinic Letter (doc03)
- ram_verdict
- Reference: verified against the real codebase
- swarm-pipeline.md
- train/__init__.py
- Ward 7B Nursing Handover (doc04)
- inject
- analyze
- test_clinical_form_templates.py
- carescribe/__init__.py
- deid_prompt.py
- prompts/__init__.py
- build_dmg.sh
- build_macos.sh
- rthook_carescribe.py
- tests/__init__.py
- run_all.py
- test_generation.py
- House-style exemplar retrieval — design
- select_backend
- desktop.py
- retrieval_planner.py
- Cloud generation transport (`CloudBackend`) — design
- test_reference_library.py
- merge_and_convert.sh
- GLiNER Deliberately Uninstalled
- run_eval.py
- Sample Source Documents README
- Recurring fictional staff roster (e.g. A. Whitfield) across documents
- Lightweight review UX for de-identification — design
- test_deid_pipeline.py
- make_sample_docs.py
- review_spans
- NoEgress
- blocking_reason
- test_generator_backend.py
- test_review_gate.py
- candidate_residuals
- metrics.py
- test_generation_setup.py
- CareScribe clinical drafting model — model card
- Stress corpus
- reference_library.py
- <id> — <title>
- render
- _RecordingBackend
- EncounterFacts
- verify_frozen.py
- Per-field retrieval planner — design
- components/__init__.py
- answer_key.json
- test_batch.py
- Evaluation report
- review_spans.py
- outstanding
- The desktop app (PyInstaller packaging)
- AGENTS.md — rules for automated coding agents in this repo
- Task board
- redact
- carenotes.py
- finetune/
- render_draft
- test_the_corpus_and_its_answer_key_agree
- _all_chunks
- load_detection_engine
- extract_text
- finetune/__init__.py
- integrate/__init__.py
- theme.py
- parse_fields
- medgpt-finetune
- list_folder
- approved_map
- eval/__init__.py
- is_model_present
- assemble/__init__.py
- wipe_phi
- stress_report.py

## God Nodes (most connected - your core abstractions)
1. `deidentify()` - 68 edges
2. `EncounterFacts` - 46 edges
3. `get_form_spec()` - 44 edges
4. `FormType` - 43 edges
5. `Document` - 38 edges
6. `generate_document()` - 27 edges
7. `residual_scan()` - 27 edges
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

## Communities (138 total, 24 thin omitted)

### Community 0 - "Cardiology Discharge Summary (doc02)"
Cohesion: 0.22
Nodes (10): Community MH Discharge Letter (doc01), Mohammed Al-Rashid ('Mo'), Cardiology Discharge Summary (doc02), Mariam Aisha Rahman, Mental Health Act Assessment Record (doc10), Facility short forms, In-prose vs anchored dates, Initials-only patient reference (e.g. M.A.R.) (+2 more)

### Community 1 - "clinical_forms.py"
Cohesion: 0.21
Nodes (17): _biopsychosocial_spec(), build_prompt(), FormField, FormSpec, _grid_fields(), HeaderField, _paragraph_texts(), Fill the three bundled APS clinical form templates from approved, de-identified… (+9 more)

### Community 2 - "build_dataset.py"
Cohesion: 0.09
Nodes (44): build(), _fallback_inject(), _load_datagen_config(), main(), Path, End-to-end: sampled encounters -> validated SFT pairs + manifest. python -m…, Fill ``[[TOKEN]]`` slots with simple fake values. Used only until…, Return ``{"pairs": [...], "kept": k, "dropped": d, "reasons": {...}}``. (+36 more)

### Community 3 - "schema.py"
Cohesion: 0.06
Nodes (60): BaseModel, Enum, field_validator, _blank_for(), expand(), Random, Turn vignettes into `EncounterFacts` instances with a seeded RNG. `expand`…, Build one `EncounterFacts` from a vignette. With ``gap_probability`` > 0, each… (+52 more)

### Community 4 - "batch.py"
Cohesion: 0.13
Nodes (21): approved_docx_path(), approved_path(), _default_output_dir(), Path, Batch input and approved-output handling. The single module in CareScribe that…, Reduce a filename to a safe output stem — no paths, no surprises., Where the approved de-identified text for ``name`` will be written., The raw bytes behind an upload or a path, without copying it to disk. (+13 more)

### Community 5 - "Reference: verified template structure"
Cohesion: 0.10
Nodes (20): carescribe/core/clinical_forms.py (module), Refine prompt (clinical form, marker-preserving), Refine prompt (free-form draft revision), Clinical Form Generation (APS Templates) Implementation Plan, Global Constraints, Reference: verified template structure, Self-Review Notes (for the implementer), Task 10: End-to-end generation glue (`generate_form_document`, `refine_form_document`, `render_preview`) (+12 more)

### Community 6 - "template_ingest.py"
Cohesion: 0.14
Nodes (28): ClinicalFormError, RuntimeError, Raised when a clinical form can't be built or filled., slugify(), delete_template(), _find_grids(), _infer_header(), _is_blank_row() (+20 more)

### Community 7 - "test_docx_roundtrip.py"
Cohesion: 0.09
Nodes (31): document_has_text_boxes(), Redact the original .docx into the output folder, structure preserved. The same…, True if a .docx holds text this redaction pass cannot reach., write_approved_docx(), extract_text(), Flatten a docx to text (body + tables + headers/footers) for a residual scan., _build(), fixture (+23 more)

### Community 8 - "test_app.py"
Cohesion: 0.07
Nodes (53): AppTest, deid(), ner_available(), fixture, Shared pytest fixtures. The spaCy model load costs several seconds, so the…, The full pipeline's output for the fixture document., True when a spaCy model loaded — layer 2 tests skip without one., raw_text() (+45 more)

### Community 9 - "mapping.py"
Cohesion: 0.09
Nodes (27): _edit_distance(), expand_facility_variants(), find_known_as(), find_spans(), _form_pattern(), Pattern, In-memory PII <-> placeholder mapping. This module is deliberately pure: it…, Return the full organisation name plus short forms. "St. Aidan's General… (+19 more)

### Community 10 - "check_placeholder_integrity"
Cohesion: 0.11
Nodes (19): finalise(), Re-identify a draft locally and refuse to hand back a leaky document. Returns…, check_placeholder_integrity(), Issue, One placeholder problem found in a generated draft., Compare a draft's bracketed tokens against the placeholders it should use. An…, Local re-identification of a generated draft. Returns ``(text, unresolved)``.…, reidentify_document() (+11 more)

### Community 11 - "test_template_ingest.py"
Cohesion: 0.12
Nodes (23): available_forms(), (form_id, title) pairs — bundled forms first, then clinic-uploaded ones., fill_parsed_template(), Fill an in-memory copy of ``original_docx`` from ``spec``'s anchors. A thin…, test_no_field_key_collides_within_a_spec(), _anchors(), _build_synthetic(), _merge_full_width() (+15 more)

### Community 12 - "Local clinical LLM fine-tune — design"
Cohesion: 0.06
Nodes (30): 10. Workstream E — integration, 11. What needs a human / external resource, 12. Milestones (testable deliverables), 13. Testing strategy, 1. Goal, 2. Constraints inherited from CareScribe, 3. Approach (selected), 4. Base model (+22 more)

### Community 13 - "generation_status"
Cohesion: 0.10
Nodes (23): cache_data, generation_status(), _llama_runtime_available(), missing_reason(), Is generation usable right now, and if not, what should the user do? Kept…, One plain sentence on why generation is not available yet., Which generation backends are usable at this moment., Which backend would actually be used, matching the backend ladder. (+15 more)

### Community 14 - "deidentify.py"
Cohesion: 0.05
Nodes (56): available_models(), _build_protected_pattern(), classify_person(), _collapse_facility_subsets(), _collapse_person_subsets(), date_span_wanted(), get_gliner(), _has_contact_anchor() (+48 more)

### Community 15 - "test_mapping.py"
Cohesion: 0.08
Nodes (31): assign_placeholders(), dedupe_entities(), normalise_type(), Coerce a model-supplied type string onto the canonical list., Drop blank and duplicate entities, keeping first-seen order and casing.…, Attach a stable placeholder to each unique entity. A type with exactly one…, Swap placeholders back to originals, repairing mangled tokens. Never raises on…, Swap placeholders back to their original values. Thin wrapper over… (+23 more)

### Community 16 - "model_setup.py"
Cohesion: 0.14
Nodes (20): clear_partial_download(), download_model(), _free_bytes(), model_destination(), ModelSetupError, Progress, pull_ollama_model(), Path (+12 more)

### Community 17 - "test_train_and_grammar.py"
Cohesion: 0.07
Nodes (39): build_grammar(), _gbnf_string_literal(), _placeholder_alt(), GBNF grammars for constrained decoding — the belt-and-braces guarantee on top…, A GBNF double-quoted literal with the necessary escapes., Alternation of the inner names of ``[NAME]`` tokens, e.g. ``"PATIENT" |…, A GBNF grammar string for one form + this document's placeholder set., Compile with llama-cpp-python if available; return the object or None. (+31 more)

### Community 18 - "backends.py"
Cohesion: 0.14
Nodes (20): privacy_indicator(), A persistent, honest statement of where data goes. It must change when cloud…, cloud_enabled(), cloud_key_present(), cloud_provider(), CloudBackend, describe_backends(), Generation backends, layered so the app works with nothing installed. Selection… (+12 more)

### Community 19 - "fill_template"
Cohesion: 0.12
Nodes (24): _clear_cell(), _dedupe_row(), _fill_cell(), _fill_cell_after_label(), _fill_header_cell(), fill_template(), Remove every paragraph after the first, and every run in the first, leaving one…, Overwrite a dedicated value cell (label lives in a different cell). (+16 more)

### Community 20 - "test_desktop_packaging.py"
Cohesion: 0.11
Nodes (11): _cloud_off(), fixture, The packaging invariants: what the desktop app may and may not do. Packaging is…, No key may be committed, defaulted, or written anywhere., Even fully configured, cloud is last., A local build and a CI build must freeze the same model., test_cloud_selection_is_never_reached_while_off(), test_output_goes_under_the_user_profile() (+3 more)

### Community 21 - "get_form_spec"
Cohesion: 0.17
Nodes (20): get_form_spec(), plan(), _load(), Generic table-row classification: which rows are fields, which are section…, test_biopsychosocial_spec_field_count_and_grid(), test_session_notes_field_walk_finds_nine_fields(), test_session_notes_signature_row_is_excluded(), test_session_notes_spec() (+12 more)

### Community 22 - "test_cloud_client.py"
Cohesion: 0.10
Nodes (25): CloudError, _config(), _post(), RuntimeError, Transport for the optional cloud generation backend. Reached only when a…, Yield the payload of each ``data:`` line in an SSE stream., Stream a completion from the configured cloud provider, yielding text. Raises…, A recoverable problem talking to the configured cloud provider. (+17 more)

### Community 23 - "Clinic reference library — design"
Cohesion: 0.17
Nodes (11): `app.py`, Architecture, Clinic reference library — design, Decision, Follow-ups (not blocking), New `core/reference_library.py`, Privacy / safety, Problem (+3 more)

### Community 24 - "Document"
Cohesion: 0.12
Nodes (30): document_flags(), entity_confirmed(), entity_frame(), flag_dismissals(), Re-derive the preview and map from an edited entity list., Redact the original .docx using the map the reviewer just approved. Detection…, Offer the redacted .docx, but only once it has cleared the sweep., Candidate residuals for this document, recomputed from current text. (+22 more)

### Community 25 - "deidentify"
Cohesion: 0.12
Nodes (30): deidentify(), Run the full local pipeline over one document. CPU-only and offline: no model…, parametrize, Regression suite for the round-2 leaks (A1-A9). The corpus tests in…, Flattening the break made one span of the org and the next line's town., The dangerous direction: this used to fail open, leaking the whole name., Brother: David Chen\\nWei Chen" was one span covering two people., A sibling listed above must not drag the patient into being a relative. (+22 more)

### Community 26 - "components.py"
Cohesion: 0.15
Nodes (23): Name the generation model, and show its model card if one ships with it., _render_generation_model(), render_sidebar(), chip(), detection_layer(), empty_state(), _esc(), hero() (+15 more)

### Community 27 - "app.py"
Cohesion: 0.12
Nodes (28): current(), documents(), _draft_state(), ingest_sources(), main(), _pipeline_step(), _privacy_state(), CareScribe — local, privacy-preserving de-identification and review. Run with:… (+20 more)

### Community 29 - "stress_corpus/README.md"
Cohesion: 0.22
Nodes (9): Margaret Elizabeth Chen ('Peggy'), Priya Venkataraman, Psychological Medicine Clinic Letter (doc06), CMHT Family Review Letter (doc07), Wei Chen, Crisis Team Contact Log (doc09), Tomasz Wisniewski, No real patient documents policy (+1 more)

### Community 30 - "assert_deidentified"
Cohesion: 0.13
Nodes (17): assert_deidentified(), CloudBackend (unwired seam), True only when ``needle`` occurs in ``haystack`` as a whole token run. Both are…, Refuse to send anything carrying a value from the identity mapping. A cheap,…, _value_present(), core/model_setup.py (model download, isolated), System prompt (anti-fabrication rules), Optional cloud generation path (off by default) (+9 more)

### Community 31 - "BackendError"
Cohesion: 0.19
Nodes (8): BackendError, LocalGGUFBackend, RuntimeError, Raised when a backend cannot be used, with the fix in the message., CPU-only generation from a bundled GGUF via ``llama-cpp-python``. The model is…, True if the runtime and a model file are both present., It fabricates otherwise — measured, not assumed., test_the_local_model_stays_pinned_at_temperature_zero()

### Community 32 - "Architecture"
Cohesion: 0.13
Nodes (14): 1. Template assets, 2. Form spec extraction, 3. Header fields (practitioner-entered), 4. Multi-document source combination, 5. Generation, 6. Review, 7. Export, 8. UI (`app.py`, Step 5) (+6 more)

### Community 33 - "test_stress_corpus.py"
Cohesion: 0.21
Nodes (12): _entities(), _normalise(), parametrize, Corpus-driven regression net. Every document in ``stress_corpus/`` is run…, Confidence tiering must never make the reviewer's job LESS safe. An "auto"…, Whatever the sweep still flags must not be a structured identifier. A surviving…, Collapse every whitespace run to one space, so line breaks stop mattering., _redacted() (+4 more)

### Community 34 - "combine_sources"
Cohesion: 0.21
Nodes (13): combine_sources(), Concatenate several documents' de-identified text into one source. ``sources``…, Regression test for Finding 3: raw filename must not leak into model-facing…, Regression test for Finding 1: cap at 26 documents (A-Z)., Regression test for Finding 1: prefixed placeholders must match PLACEHOLDER_RE.…, Regression test for Finding 2: text and map rewrites must be consistent. A…, test_combine_sources_no_filename_in_output(), test_combine_sources_non_standard_placeholder_consistency() (+5 more)

### Community 35 - "structured_spans"
Cohesion: 0.10
Nodes (21): _header_footer_bounds(), _plausible_surname(), Character ranges of the document's opening and closing lines., True if the trailing token of an initial+surname reads like a real name.…, Layer 1: deterministic regex detections over ``text``., REDACT_INPROSE_DATES flag, structured_spans(), expand_org_variants (Layer 4 — variant expansion) (+13 more)

### Community 36 - "FormType"
Cohesion: 0.16
Nodes (18): build_messages(), Care note templates. Every template shares the same hard rule: the input is…, Return ``(system, user)`` for a template label and de-identified document., FormType, The output form a training example asks the model to fill., build_messages(), default_instruction(), The prompt construction shared by training and production. Training pairs MUST… (+10 more)

### Community 37 - "expand_name_variants"
Cohesion: 0.09
Nodes (24): _collapse_person_identities(), True for a person row whose role is known (patient / relative / clinician)., Collapse every written form of one person onto a single entity row.…, _specific_person_type(), canonical_person_key(), expand_name_variants(), _initial_letters(), keys_are_compatible() (+16 more)

### Community 38 - "make_icon.py"
Cohesion: 0.29
Nodes (12): Image, _load_font(), main(), Path, Generate CareScribe's placeholder icon. A real icon is a design job; this…, The first usable bold face, or ``None`` if none of them load., A rounded square with "CS" centred on it., macOS only. Silently skipped elsewhere — the .app is built on a Mac. (+4 more)

### Community 39 - "rebuild"
Cohesion: 0.09
Nodes (23): add_manual_entity(), DeidentificationError, DeidResult, RuntimeError, Re-derive redacted text and the PHI map from a reviewer-edited table. Called…, Add an identifier the tools missed and immediately re-redact. The new value…, Raised when de-identification can't run at all., Everything the de-identification stage produces for one document. (+15 more)

### Community 40 - "exemplars.py"
Cohesion: 0.13
Nodes (27): add_exemplar(), count(), _dir(), ExemplarError, _load(), _path(), Path, RuntimeError (+19 more)

### Community 41 - "render_clinical_form_panel"
Cohesion: 0.22
Nodes (10): _form_draft_key(), _form_draft_state(), _header_values_complete(), Let a clinic add its own table-based .docx form to the selector. Parsing and…, render_clinical_form_panel(), _render_template_uploader(), Pure-logic pieces of the clinical-form UI: the session-state key used to key a…, test_form_draft_key_differs_by_form_or_selection() (+2 more)

### Community 42 - "ollama_client.py"
Cohesion: 0.14
Nodes (19): default_model(), generate(), is_up(), list_models(), missing_model_message(), OllamaError, RuntimeError, Local Ollama client — pinned to the loopback interface. Generation is the first… (+11 more)

### Community 43 - "run_app.py"
Cohesion: 0.16
Nodes (17): Popen, close_splash(), _fatal(), free_port(), main(), _no_window_kwargs(), CareScribe desktop launcher — the app's entry point. Starts the Streamlit…, Dismiss the bootloader splash, if this is a frozen build that has one.… (+9 more)

### Community 44 - "test_buildinfo.py"
Cohesion: 0.24
Nodes (10): build_info(), Build information for CareScribe., Return standard HTTP User-Agent string., Return application identity and version., user_agent(), Tests for buildinfo module., Test that user_agent returns correct format., Test that build_info returns correct name and version. (+2 more)

### Community 45 - "GP Referral Letter (doc05)"
Cohesion: 0.25
Nodes (8): Elspeth Mackenzie-Ford ('Ellie'), GP Referral Letter (doc05), Oluwaseun Adeyinka, Resource Centre Referral (doc08), Hyphenated surname pattern, 'Known as' alias pattern, Two label styles pattern, Shared case number 990214 reused across fictional patients

### Community 46 - "highlight_review"
Cohesion: 0.24
Nodes (9): highlight_review(), Click-to-redact highlighted text. Renders already-redacted (or already-flagged)…, Render ``html`` and return the ``data-span-id`` of the last click. Returns…, _frontend_path(), Path, Offline-first: nothing in this file may fetch from a CDN., test_frontend_file_exists(), test_frontend_has_no_external_script_or_link_tags() (+1 more)

### Community 47 - "test_deid_regressions.py"
Cohesion: 0.10
Nodes (26): _mrn_values(), parametrize, Regression suite for the five leaks found on a second, non-fixture document.…, Layer 1 must carry this on its own — NER catching it is luck, not a guarantee., Regardless of REDACT_INPROSE_DATES, which stays False by default., 14 June 2026\\nDate" swallowed the next line's label and mangled the text., The label shapes document #2 actually used, including the parenthetical., Context-anchoring is the whole point — a bare digit run is a lab value. (+18 more)

### Community 48 - "generate_form_document"
Cohesion: 0.22
Nodes (10): generate_form_document(), Human-readable rendering for display only — the marker text in ``draft_state``…, render_preview(), Captures exactly what generation handed the model — mirrors the fixture in…, RecordingBackend, test_generate_form_document_refuses_a_real_identifier(), test_generate_form_document_sends_the_field_marker_prompt(), test_refine_form_document_preserves_markers_instruction() (+2 more)

### Community 49 - "docx_redact.py"
Cohesion: 0.19
Nodes (15): apply_redactions(), _delete_prefix(), has_unreachable_text(), _iter_groups(), _iter_paragraphs(), _norm(), Structure-preserving .docx redaction. apply_redactions(path_in, path_out,…, Redact a literal split across a paragraph boundary (wrapped name). (+7 more)

### Community 50 - "Model Card for phi35-v1"
Cohesion: 0.33
Nodes (5): Citations, Framework versions, Model Card for phi35-v1, Quick start, Training procedure

### Community 51 - "Installing CareScribe"
Cohesion: 0.22
Nodes (8): Before you start, First launch, If it will not start, Installing CareScribe, macOS, Updating, Where your files go, Windows

### Community 52 - "test_validators.py"
Cohesion: 0.21
Nodes (15): check_format(), check_placeholders(), check_residual(), Fail on a mangled or invented bracket token; ignore ``missing``. A filled form…, A regression set built from the repo's own corpus, not synthetic data.…, regression_items(), RegressionItem, score_regression() (+7 more)

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

### Community 57 - "ram_verdict"
Cohesion: 0.33
Nodes (6): available_ram_gb(), ram_verdict(), Total system RAM in GB, or 0.0 if it cannot be determined., Whether this machine can run the bundled local model. Returns a verdict rather…, test_a_capable_laptop_gets_no_warning(), test_a_weak_laptop_gets_a_warning_not_a_crash()

### Community 58 - "Reference: verified against the real codebase"
Cohesion: 0.15
Nodes (12): Global Constraints, Lightweight Review UX Redesign Implementation Plan, Reference: verified against the real codebase, Self-Review Notes, Task 1: Confidence tiering in the detection pipeline, Task 2: Unified review-span module, Task 3: Click-to-redact custom Streamlit component, Task 4: Simplify `review_checklist.py` to a two-input gate (+4 more)

### Community 61 - "Ward 7B Nursing Handover (doc04)"
Cohesion: 0.50
Nodes (4): Aiden Braithwaite, Ward 7B Nursing Handover (doc04), 'A. Surname' against full name in header, Labelled date fields

### Community 62 - "inject"
Cohesion: 0.15
Nodes (26): _collect(), _date(), _dob(), inject(), _make(), _mrn(), _name(), nhs_number() (+18 more)

### Community 63 - "analyze"
Cohesion: 0.10
Nodes (22): analyze(), flatten_lines(), gliner_spans(), ner_spans(), Layer 2: Presidio/spaCy detections, mapped onto CareScribe entity types.…, Layer 3: GLiNER detections, or an empty list when it isn't installed., Run every enabled layer over ``text`` and return reviewable entities. Each…, One detection, in character offsets over the source text. (+14 more)

### Community 64 - "test_clinical_form_templates.py"
Cohesion: 0.50
Nodes (3): parametrize, The three bundled APS templates load and match the structure this feature's…, test_bundled_template_shape()

### Community 73 - "test_generation.py"
Cohesion: 0.08
Nodes (40): generate_document(), Stream a drafted document from approved de-identified text. ``phi_values`` is…, Revise an existing draft against a follow-up instruction. Operates on the same…, The shared preamble — role, anti-fabrication rules, placeholder rules., refine_document(), system_prompt(), parametrize, Local generation: the privacy contract, placeholder integrity, and the gate. No… (+32 more)

### Community 74 - "House-style exemplar retrieval — design"
Cohesion: 0.18
Nodes (10): `app.py`, Architecture, `core/clinical_forms.py`, Follow-ups (not blocking), House-style exemplar retrieval — design, New module `core/exemplars.py`, Privacy, Problem (+2 more)

### Community 76 - "select_backend"
Cohesion: 0.13
Nodes (20): _invalidate_form_export(), Drop any previously re-identified/exportable content — called whenever the…, Render a stream token by token so a slow local model looks alive., First-pass generation. The model receives de-identified text only., Follow-up instructions, on de-identified text only., Verbatim reference passages, retrieved per field at the granularity the planner…, render_form_draft(), render_form_refinement() (+12 more)

### Community 77 - "desktop.py"
Cohesion: 0.13
Nodes (26): app_data_dir(), bundle_root(), ensure_dirs(), find_local_model(), is_frozen(), _model_search_dirs(), models_dir(), output_dir() (+18 more)

### Community 78 - "retrieval_planner.py"
Cohesion: 0.27
Nodes (6): Protocol, Per-field retrieval planning for clinical-form generation. Roadmap item E…, Deterministic planner driven by a keyword taxonomy over field labels., RetrievalPlan, RetrievalPlanner, RuleBasedPlanner

### Community 80 - "Cloud generation transport (`CloudBackend`) — design"
Cohesion: 0.20
Nodes (9): Architecture, Cloud generation transport (`CloudBackend`) — design, `core/backends.py`, Follow-ups (not blocking), New module `core/cloud_client.py`, Privacy properties (unchanged, inherited), Problem, Scope (+1 more)

### Community 81 - "test_reference_library.py"
Cohesion: 0.12
Nodes (24): Add clinic reference files (formulary, pathways, protocols) to a local library.…, _render_reference_uploader(), add_file(), _dir(), _files(), is_empty(), Path, ``(filename, paragraph_count)`` per loaded reference file. (+16 more)

### Community 84 - "run_eval.py"
Cohesion: 0.09
Nodes (35): aggregate(), DraftScore, Mean of each metric over ``scores`` (style_match over styled drafts only)., score_draft(), regressed(), build_report(), Path, EVAL_REPORT.md + eval_report.json from a base-vs-tuned comparison. The report… (+27 more)

### Community 87 - "Lightweight review UX for de-identification — design"
Cohesion: 0.14
Nodes (13): 1. Confidence tiering (drives what gets a click at all), 2. One primary review view, not three, 3. The click-to-redact component, 4. Attestation & audit trail, 5. Crash-risk fixes, Architecture, Current state (for reference), Goals (+5 more)

### Community 88 - "test_deid_pipeline.py"
Cohesion: 0.05
Nodes (41): Re-scan ALREADY-REDACTED text for anything that still looks identifying. Runs…, residual_scan(), parametrize, Regression suite for the layered de-identification pipeline. Two guarantees,…, With REDACT_INPROSE_DATES False, a procedure date is clinical, not identity., DOB and admission/discharge dates carry identity, so they go., spaCy labels "ECG" and "NSTEMI" as organisations; the filter must drop them., Placeholders are the point of the exercise, not leaks. (+33 more)

### Community 89 - "make_sample_docs.py"
Cohesion: 0.20
Nodes (18): build_intake_notes(), build_referral_letter(), build_session_log(), build_treatment_review_source(), _grid_table(), _heading(), _para(), Generate synthetic, complex .docx source documents for manually testing the… (+10 more)

### Community 90 - "review_spans"
Cohesion: 0.32
Nodes (12): Every clickable span in ``redacted_text``, in reading order. ``confirmed`` is…, review_spans(), _entity(), action=Keep means the reviewer already decided — nothing to click on the…, test_a_confirmed_entity_produces_no_span(), test_a_kept_entity_produces_no_entity_span(), test_auto_confidence_entities_produce_no_span(), test_dismissed_residual_flags_are_excluded() (+4 more)

### Community 91 - "NoEgress"
Cohesion: 0.11
Nodes (15): get_analyzer(), Return the shared Presidio analyzer, or ``None`` if it can't be built. First…, NoEgress, Fails the test if anything opens a non-loopback socket. Loopback is allowed:…, Stands in for a model so the egress test does not need one installed., Re-identification is pure Python — it must not phone anywhere., StubBackend, test_reidentification_opens_no_socket() (+7 more)

### Community 92 - "blocking_reason"
Cohesion: 0.17
Nodes (11): blocking_reason(), The approval gate. Only the **authoritative safety sweep** blocks approval. A…, Why Approve is disabled, in one short line. Empty string means it isn't.…, Low-confidence redactions are already in place; the permissive flags are…, The streamlined gate: a permissive flag the reviewer left untouched does not…, test_advisory_spans_do_not_block_approval(), test_an_advisory_flag_alone_no_longer_blocks_approval(), test_approval_is_blocked_while_the_sweep_has_findings() (+3 more)

### Community 93 - "test_generator_backend.py"
Cohesion: 0.11
Nodes (19): GeneratorBackend, get_backend(), OllamaBackend, OpenAICompatibleBackend, TemplateBackend, Test that TemplateBackend properly renders facts in proforma style, Test that TemplateBackend properly renders facts in prose style, Test that TemplateBackend is deterministic - same input gives same output (+11 more)

### Community 94 - "test_review_gate.py"
Cohesion: 0.15
Nodes (13): _flag_values(), fixture, parametrize, The reviewer gate: candidate highlighting, the adaptive checklist, and the no-…, The real test: nothing the corpus calls an identifier may appear., A dismissal key holds the span text, so it must be wiped with the rest., record(), test_a_planted_residual_is_flagged() (+5 more)

### Community 95 - "candidate_residuals"
Cohesion: 0.18
Nodes (11): candidate_residuals(), _is_common(), _placeholder_ranges(), True if every word in the run is ordinary English or a month name., Spans in already-redacted text that could still hide an identifier. Permissive…, Five-digit rule must not fire on "10mg" style clinical numbers., test_a_clean_document_produces_no_flags(), test_a_dose_is_not_flagged_as_an_id() (+3 more)

### Community 96 - "metrics.py"
Cohesion: 0.31
Nodes (8): _headings(), _lexical_overlap(), _order_agreement(), The four target metrics, scored per draft and reducible to a mean. Format,…, Fraction of ``a``'s headings that appear in ``b`` in the same relative order., 0..1 — heading-order agreement and lexical overlap, evenly weighted. Falls back…, style_match(), test_style_match_is_one_for_identical_text()

### Community 97 - "test_generation_setup.py"
Cohesion: 0.08
Nodes (16): _cloud_off(), _fresh_generation_status_cache(), mapping_module(), fixture, First-run generation setup: never an empty panel, and the egress line held. The…, The one outbound path must not be reachable from the de-id flow., generation_status() is now @st.cache_data(ttl=5) — a process-global cache keyed…, `state` held the draft dict, then the backend dict overwrote it. The draft dict… (+8 more)

### Community 98 - "CareScribe clinical drafting model — model card"
Cohesion: 0.40
Nodes (4): CareScribe clinical drafting model — model card, Evaluation, Known limitations, Training data

### Community 99 - "Stress corpus"
Cohesion: 0.50
Nodes (4): Running it, Stress corpus, The answer key, What each document covers

### Community 100 - "reference_library.py"
Cohesion: 0.17
Nodes (14): RuntimeError, Clinic reference material — formularies, care pathways, local protocols — as a…, Top-``k`` reference passages for ``query`` at ``granularity``. BM25, ``score >…, Raised when a reference file cannot be stored., ReferenceError, ReferenceHit, search(), BM25 (+6 more)

### Community 101 - "<id> — <title>"
Cohesion: 0.29
Nodes (6): Acceptance criteria, Do NOT touch, Files in scope, Goal, <id> — <title>, Notes

### Community 102 - "render"
Cohesion: 0.31
Nodes (10): _degrade(), _header(), _lines(), _med(), Random, `EncounterFacts` -> a realistic, messy clinician note (the INPUT side of a…, (section label, lines) in a fixed clinical order, skipping empty sections., A little OCR/casing/spacing noise, sampled. (+2 more)

### Community 104 - "EncounterFacts"
Cohesion: 0.12
Nodes (32): build_target(), _care_plan(), _handover(), _history_lines(), _med_line(), _objective_lines(), _plan_lines(), _progress_note() (+24 more)

### Community 105 - "verify_frozen.py"
Cohesion: 0.36
Nodes (9): bundled_app_py(), _default_dist(), find_executable(), free_port(), main(), Path, Post-build smoke check: does the frozen CareScribe binary actually start? A…, Locate the frozen entry-point inside a PyInstaller output directory. (+1 more)

### Community 106 - "Per-field retrieval planner — design"
Cohesion: 0.17
Nodes (11): `app.py`, Architecture, `core/reference_library.py`, `core/retrieval_planner.py` (new), `core/text_search.py`, Decision, Follow-ups (not blocking), Per-field retrieval planner — design (+3 more)

### Community 108 - "answer_key.json"
Cohesion: 0.67
Nodes (3): answer_key.json, must_preserve (answer key field), must_redact (answer key field)

### Community 109 - "test_batch.py"
Cohesion: 0.09
Nodes (33): analyze_document(), load_documents(), Extract text from uploads or paths. Returns ``(documents, errors)``. One…, Run the de-identification layers over one document, in place., Findings from the safety sweep, minus the ones the reviewer has cleared. A…, Write approved de-identified text to the output folder. Re-runs the safety…, sweep(), write_approved() (+25 more)

### Community 111 - "review_spans.py"
Cohesion: 0.32
Nodes (7): _review_span_style(), _entity_spans(), Unifies the two things a reviewer might still need to act on in one document's…, One clickable span in a document's redacted text., Placeholder occurrences for low-confidence, not-yet-confirmed entities., _residual_spans(), ReviewSpan

### Community 112 - "outstanding"
Cohesion: 0.25
Nodes (7): Flag, outstanding(), One span worth a second look, with its offsets in the redacted text., Identity for dismissal — per value, so one decision covers repeats., Flags the reviewer has neither redacted away nor dismissed., test_dismissing_a_flag_clears_it(), test_the_gate_unblocks_after_dismissing_the_last_flag()

### Community 113 - "The desktop app (PyInstaller packaging)"
Cohesion: 0.25
Nodes (8): packaging/build_macos.sh, packaging/build_windows.ps1, packaging/carescribe.iss (Inno Setup script), packaging/make_icon.py, The desktop app (PyInstaller packaging), run_app.py entry point, Path A — you have the built app, Path B — building from source

### Community 114 - "AGENTS.md — rules for automated coding agents in this repo"
Cohesion: 0.40
Nodes (4): AGENTS.md — rules for automated coding agents in this repo, Do, Never, Task spec shape

### Community 115 - "Task board"
Cohesion: 0.12
Nodes (16): App bug the user hit (2026-09-01) — FIXED in `e9bcc3b`, Fine-tune decisions locked (2026-09-01), Fine-tune hardware facts (2026-09-01), Fine-tune progress — cockpit-driven, COMMITTED on integration branch, Local clinical LLM fine-tune (started 2026-09-01), M3–M5 DONE — model trained, evaluated, integrated (2026-09-01), Pipeline incident 2026-09-01 (fixed), Swarm tasks 015 / 016 — both failed, cockpit did them (+8 more)

### Community 116 - "redact"
Cohesion: 0.33
Nodes (6): Replace every surface form of every entity with its placeholder. Replacement…, redact(), Form tokens are joined with \\s+, so a name split across lines still matches., test_longest_match_wins_on_overlap(), test_matcher_does_not_fire_inside_a_longer_word(), test_matcher_tolerates_a_line_break()

### Community 117 - "carenotes.py"
Cohesion: 0.08
Nodes (27): assert_no_residual_identifiers(), Backend, CareNoteError, generate_care_note(), load_prompt(), OllamaBackend, Protocol, RuntimeError (+19 more)

### Community 118 - "finetune/"
Cohesion: 0.40
Nodes (4): Environment, finetune/, Layout, Milestones

### Community 119 - "render_draft"
Cohesion: 0.40
Nodes (6): _as_docx(), The de-identified draft, refinement, re-identification, and exports., Opt-in, local-only substitution of placeholders back to real values., Render generated text to a .docx in memory — nothing touches disk., render_draft(), render_reidentification()

### Community 121 - "_all_chunks"
Cohesion: 0.29
Nodes (8): _all_chunks(), _bounded(), Chunk, _paragraphs(), Chunk one file at the requested granularity, tracking Markdown headings. *…, ``(heading, paragraph_text)`` for every blank-line-separated block., _split_file(), test_a_long_paragraph_is_split_into_bounded_chunks()

### Community 122 - "load_detection_engine"
Cohesion: 0.40
Nodes (5): cache_resource, load_detection_engine(), Load the NER model once per session, not once per rerun. Streamlit re-runs the…, engine_status(), Report which layers are live, for the sidebar. Loads nothing by itself.

### Community 123 - "extract_text"
Cohesion: 0.05
Nodes (55): BaseException, ensure_engine_ready(), Load the model at startup, behind a visible spinner. Deliberately not lazy. If…, The last line of defence: a calm message instead of a stack trace. A clinician…, render_unexpected_error(), exception(), get_logger(), log() (+47 more)

### Community 126 - "theme.py"
Cohesion: 0.33
Nodes (4): CareScribe UI layer — the visual identity, applied over Streamlit. `theme.CSS`…, inject(), CareScribe visual identity — one stylesheet, injected once per rerun. DIRECTION…, Apply the stylesheet. Import Streamlit lazily so the module stays cheap.

### Community 127 - "parse_fields"
Cohesion: 0.44
Nodes (9): parse_fields(), Turn the model's marker-delimited output into ``{field_key: text}``. Any field…, _spec(), test_parse_fields_defaults_missing_field_to_not_documented(), test_parse_fields_first_occurrence_wins_on_duplicate_marker(), test_parse_fields_handles_empty_output(), test_parse_fields_happy_path(), test_parse_fields_ignores_unknown_marker_without_raising() (+1 more)

### Community 131 - "list_folder"
Cohesion: 0.25
Nodes (8): BatchError, list_folder(), RuntimeError, Return the supported documents in ``folder``, sorted by name. Non-recursive on…, Raised for input-folder and output-write problems., test_list_folder_finds_documents(), test_list_folder_rejects_a_missing_path(), test_list_folder_rejects_an_empty_folder()

### Community 132 - "approved_map"
Cohesion: 0.40
Nodes (5): approved_map(), The reviewer-approved ``{literal: placeholder}`` map for the Word pass. This is…, test_a_kept_row_contributes_nothing_to_the_approved_map(), test_the_approved_map_covers_every_surface_form(), test_the_approved_map_is_longest_literal_first()

### Community 137 - "is_model_present"
Cohesion: 0.50
Nodes (4): is_model_present(), True if a usable model file is already on this computer. This is the marker…, Setup is one-time because the file itself is the state., test_model_presence_is_the_persisted_marker()

### Community 141 - "wipe_phi"
Cohesion: 0.67
Nodes (4): PHI_KEYS (session-state PHI registry), Drop every document, identifier table, and identity map from memory., wipe_phi(), Bug: form_drafts never registered with PHI_KEYS/wipe_phi

### Community 145 - "stress_report.py"
Cohesion: 0.67
Nodes (3): main(), normalise(), Per-document pass/fail report for the stress corpus. python…

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
- **198 isolated node(s):** `medgpt-finetune`, `merge_and_convert.sh script`, `build_dmg.sh script`, `build_macos.sh script`, `Worker capability ceiling on the fine-tune workstream (2026-09-01)` (+193 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

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
- **Why does `FormType` connect `FormType` to `metrics.py`, `build_dataset.py`, `schema.py`, `EncounterFacts`, `test_train_and_grammar.py`, `test_validators.py`, `run_eval.py`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `Document` connect `Document` to `batch.py`, `test_docx_roundtrip.py`, `test_app.py`, `select_backend`, `test_batch.py`, `docx_redact.py`, `render_draft`, `make_sample_docs.py`, `app.py`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._