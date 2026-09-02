# Graph Report - medgpt  (2026-09-02)

## Corpus Check
- 168 files · ~139,463 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2303 nodes · 4462 edges · 157 communities (127 shown, 30 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 98 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9a8fc1bf`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- candidate_residuals
- clinical_forms.py
- test_assemble_pipeline.py
- render_prompt
- batch.py
- Reference: verified template structure
- template_ingest.py
- test_docx_roundtrip.py
- test_app.py
- schema.py
- test_generation.py
- test_template_ingest.py
- Local clinical LLM fine-tune — design
- generation_status
- deidentify.py
- test_app_screens.py
- model_setup.py
- test_train_and_grammar.py
- backends.py
- get_form_spec
- test_desktop_packaging.py
- plan
- test_cloud_client.py
- Clinic reference library — design
- Document
- deidentify
- components.py
- available_forms
- test_deid_regressions.py
- make_sample_docs.py
- assert_deidentified
- extract_text
- Architecture
- test_stress_corpus.py
- combine_sources
- load_documents
- FormType
- CareScribe — design system
- make_icon.py
- EncounterFacts
- test_exemplars.py
- redact
- ollama_client.py
- run_app.py
- test_buildinfo.py
- residual_scan
- highlight_review
- load_settings
- BackendError
- docx_redact.py
- Model Card for phi35-v1
- Installing CareScribe
- validators.py
- Clinic-uploaded clinical form templates — design
- [0.1.0] - 2026-09-01
- Report templates (SOAP / GP letter / discharge / custom)
- Outpatient Respiratory Clinic Letter (doc03)
- mapping.py
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
- app.py
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
- structured_spans
- NoEgress
- test_clinical_forms_generate.py
- test_generator_backend.py
- test_review_gate.py
- select_backend
- cloud_client.py
- test_generation_setup.py
- CareScribe clinical drafting model — model card
- expand_name_variants
- BM25
- <id> — <title>
- analyze
- ner_spans
- LLM backend flexibility + realistic test corpus + full-pipeline validation
- verify_frozen.py
- Per-field retrieval planner — design
- components/__init__.py
- build_dataset.py
- test_batch.py
- Evaluation report
- blocking_reason
- main
- Generation backend selection order (Ollama > built-in GGUF > Cloud)
- AGENTS.md — rules for automated coding agents in this repo
- Task board
- Global Constraints
- reidentify
- finetune/
- run_eval.py
- load_protected_terms
- reference_library.py
- test_clinical_forms.py
- CloudBackend
- finetune/__init__.py
- integrate/__init__.py
- test_mapping.py
- parse_fields
- medgpt-finetune
- canonical_person_key
- resolve_placeholder
- exemplars.py
- carenotes.py
- render_generation_panel
- eval/__init__.py
- is_model_present
- rebuild
- assemble/__init__.py
- get_analyzer
- _run
- theme.py
- wipe_phi
- resolve_model_path
- document_has_text_boxes
- DeidResult
- _fresh_generation_status_cache
- test_an_html_error_page_is_rejected
- test_pipeline_runs_without_ner
- test_pipeline_is_deterministic
- test_a_date_entity_never_spans_a_line_break
- test_nothing_downloads_on_import_or_launch
- test_the_draft_state_and_backend_state_are_not_confused
- test_the_draft_state_carries_the_expected_keys
- test_the_helpers_name_the_draft_dict_explicitly
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

## Communities (157 total, 30 thin omitted)

### Community 0 - "candidate_residuals"
Cohesion: 0.12
Nodes (20): candidate_residuals(), Flag, _is_common(), outstanding(), _placeholder_ranges(), Residual-candidate highlighter — where the reviewer's eye should go first. This…, One span worth a second look, with its offsets in the redacted text., Identity for dismissal — per value, so one decision covers repeats. (+12 more)

### Community 1 - "clinical_forms.py"
Cohesion: 0.17
Nodes (21): _biopsychosocial_spec(), build_prompt(), _fill_cell_after_label(), _form_grammar(), FormField, FormSpec, generate_form_document(), _grid_fields() (+13 more)

### Community 2 - "test_assemble_pipeline.py"
Cohesion: 0.18
Nodes (20): build_manifest(), _carescribe_sha(), content_hash(), Provenance for a built dataset. A content hash over the pair list, plus how it…, SHA-256 over the sorted JSON lines — stable regardless of pair order., make_pair(), make_template_pair(), Pair (+12 more)

### Community 3 - "render_prompt"
Cohesion: 0.40
Nodes (5): Build the user prompt for one template with the source text embedded., render_prompt(), test_an_unknown_template_is_refused(), test_the_custom_template_carries_the_clinicians_own_format(), test_the_custom_template_needs_instructions()

### Community 4 - "batch.py"
Cohesion: 0.15
Nodes (19): approved_docx_path(), approved_path(), _default_output_dir(), Path, Batch input and approved-output handling. The single module in CareScribe that…, Reduce a filename to a safe output stem — no paths, no surprises., Where the approved de-identified text for ``name`` will be written., The raw bytes behind an upload or a path, without copying it to disk. (+11 more)

### Community 5 - "Reference: verified template structure"
Cohesion: 0.10
Nodes (20): carescribe/core/clinical_forms.py (module), Refine prompt (clinical form, marker-preserving), Refine prompt (free-form draft revision), Clinical Form Generation (APS Templates) Implementation Plan, Global Constraints, Reference: verified template structure, Self-Review Notes (for the implementer), Task 10: End-to-end generation glue (`generate_form_document`, `refine_form_document`, `render_preview`) (+12 more)

### Community 6 - "template_ingest.py"
Cohesion: 0.15
Nodes (26): slugify(), delete_template(), _find_grids(), _infer_header(), _is_blank_row(), load_user_spec(), _match_header(), _parse_document() (+18 more)

### Community 7 - "test_docx_roundtrip.py"
Cohesion: 0.09
Nodes (32): approved_map(), The reviewer-approved ``{literal: placeholder}`` map for the Word pass. This is…, Redact the original .docx into the output folder, structure preserved. The same…, write_approved_docx(), extract_text(), Flatten a docx to text (body + tables + headers/footers) for a residual scan., _build(), fixture (+24 more)

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
Cohesion: 0.15
Nodes (18): fill_parsed_template(), Fill an in-memory copy of ``original_docx`` from ``spec``'s anchors. A thin…, _anchors(), _build_synthetic(), _merge_full_width(), fixture, parametrize, A clinic can add its own table-based .docx form. The generic parser must infer… (+10 more)

### Community 12 - "Local clinical LLM fine-tune — design"
Cohesion: 0.06
Nodes (30): 10. Workstream E — integration, 11. What needs a human / external resource, 12. Milestones (testable deliverables), 13. Testing strategy, 1. Goal, 2. Constraints inherited from CareScribe, 3. Approach (selected), 4. Base model (+22 more)

### Community 13 - "generation_status"
Cohesion: 0.11
Nodes (19): cache_data, Shown instead of an empty panel when no model is available yet. An empty…, Option A. The only outbound request the app makes, on an explicit click., Option B. Ollama does the fetching; the request goes to loopback., render_setup_card(), run_model_download(), run_ollama_pull(), generation_status() (+11 more)

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
Cohesion: 0.18
Nodes (15): _model_card_path(), privacy_indicator(), Path, A persistent, honest statement of where data goes. It must change when cloud…, Which backend will be used, and the fix if none is available., render_generation_status(), cloud_enabled(), cloud_key_present() (+7 more)

### Community 19 - "get_form_spec"
Cohesion: 0.15
Nodes (24): _clear_cell(), ClinicalFormError, _dedupe_row(), _fill_cell(), _fill_header_cell(), fill_template(), get_form_spec(), RuntimeError (+16 more)

### Community 20 - "test_desktop_packaging.py"
Cohesion: 0.10
Nodes (14): available_ram_gb(), ram_verdict(), Total system RAM in GB, or 0.0 if it cannot be determined., Whether this machine can run the bundled local model. Returns a verdict rather…, _cloud_off(), fixture, The packaging invariants: what the desktop app may and may not do. Packaging is…, No key may be committed, defaulted, or written anywhere. (+6 more)

### Community 21 - "plan"
Cohesion: 0.18
Nodes (15): Verbatim reference passages, retrieved per field at the granularity the planner…, _render_reference_panel(), plan(), Protocol, RetrievalPlan, RetrievalPlanner, _field(), Per-field retrieval planning (roadmap item E). The shipped planner is rule-… (+7 more)

### Community 22 - "test_cloud_client.py"
Cohesion: 0.15
Nodes (14): Stream a completion from the configured cloud provider, yielding text. Raises…, stream_generation(), _capture(), _clean_cloud_env(), _FakeResponse, fixture, The optional cloud generation transport — stdlib HTTP, two wire formats, key…, test_a_missing_key_raises_before_any_request() (+6 more)

### Community 23 - "Clinic reference library — design"
Cohesion: 0.17
Nodes (11): `app.py`, Architecture, Clinic reference library — design, Decision, Follow-ups (not blocking), New `core/reference_library.py`, Privacy / safety, Problem (+3 more)

### Community 24 - "Document"
Cohesion: 0.13
Nodes (29): document_flags(), entity_confirmed(), entity_frame(), flag_dismissals(), One click to approve every document that comes back clean. Each is re-run…, Re-derive the preview and map from an edited entity list., Redact the original .docx using the map the reviewer just approved. Detection…, Offer the redacted .docx, but only once it has cleared the sweep. (+21 more)

### Community 25 - "deidentify"
Cohesion: 0.12
Nodes (30): deidentify(), Run the full local pipeline over one document. CPU-only and offline: no model…, parametrize, Regression suite for the round-2 leaks (A1-A9). The corpus tests in…, Flattening the break made one span of the org and the next line's town., The dangerous direction: this used to fail open, leaking the whole name., Brother: David Chen\\nWei Chen" was one span covering two people., A sibling listed above must not drag the patient into being a relative. (+22 more)

### Community 26 - "components.py"
Cohesion: 0.10
Nodes (32): _model_card_dialog(), Name the generation model with a readable label; the card opens in a dialog…, _render_generation_model(), render_sidebar(), chip(), detection_layer(), empty_state(), _esc() (+24 more)

### Community 27 - "available_forms"
Cohesion: 0.20
Nodes (10): available_forms(), (form_id, title) pairs — bundled forms first, then clinic-uploaded ones., skipif, test_no_field_key_collides_within_a_spec(), parametrize, Deterministic stand-in for a real generation backend., _StubBackend, test_combined_sources_generate_every_form_type_with_a_stub_backend() (+2 more)

### Community 28 - "test_deid_regressions.py"
Cohesion: 0.09
Nodes (29): _mrn_values(), parametrize, Regression suite for the five leaks found on a second, non-fixture document.…, A two-part capitalised phrase mid-document is not a letterhead., Layer 1 must carry this on its own — NER catching it is luck, not a guarantee., M.E.C.\\nFollow-up" must not become the name "M.E.C. Follow"., Regardless of REDACT_INPROSE_DATES, which stays False by default., The label shapes document #2 actually used, including the parenthetical. (+21 more)

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

### Community 35 - "load_documents"
Cohesion: 0.12
Nodes (20): analyze_document(), load_documents(), Extract text from uploads or paths. Returns ``(documents, errors)``. One…, Run the de-identification layers over one document, in place., FakeUpload, Stands in for a Streamlit UploadedFile., test_analyze_document_populates_state(), test_duplicate_filenames_are_reported() (+12 more)

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

### Community 40 - "test_exemplars.py"
Cohesion: 0.11
Nodes (26): add_exemplar(), count(), _dir(), _load(), _path(), Path, Top-``k`` stored values for ``field_key``, ranked by BM25 against ``query``., ``{field_key: [examples]}`` for every key that has at least one exemplar. (+18 more)

### Community 41 - "redact"
Cohesion: 0.12
Nodes (17): find_known_as(), find_spans(), _form_pattern(), Pattern, Pull a patient's preferred name out of a "Known as:" field, if present., Whitespace-tolerant, case-insensitive pattern for one surface form. Tokens are…, Find non-overlapping ``(start, end, placeholder)`` spans for every form. All…, Replace every surface form of every entity with its placeholder. Replacement… (+9 more)

### Community 42 - "ollama_client.py"
Cohesion: 0.13
Nodes (22): generate_care_note(), Draft a care note from ALREADY DE-IDENTIFIED text, returning it whole. The…, default_model(), generate(), is_up(), list_models(), missing_model_message(), OllamaError (+14 more)

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

### Community 47 - "load_settings"
Cohesion: 0.30
Nodes (12): load_settings(), _path(), Persisted app settings — which generation backend/model/temperature to use.…, Read persisted settings. A missing or unreadable file yields defaults., Persist non-secret settings, creating the app data dir if needed., save_settings(), Settings, test_load_settings_ignores_unknown_fields_keeps_missing_as_default() (+4 more)

### Community 48 - "BackendError"
Cohesion: 0.19
Nodes (8): BackendError, LocalGGUFBackend, RuntimeError, Raised when a backend cannot be used, with the fix in the message., CPU-only generation from a bundled GGUF via ``llama-cpp-python``. The model is…, True if the runtime and a model file are both present., It fabricates otherwise — measured, not assumed., test_the_local_model_stays_pinned_at_temperature_zero()

### Community 49 - "docx_redact.py"
Cohesion: 0.19
Nodes (15): apply_redactions(), _delete_prefix(), _iter_groups(), _iter_paragraphs(), _norm(), Structure-preserving .docx redaction. apply_redactions(path_in, path_out,…, Redact a literal split across a paragraph boundary (wrapped name)., Delete the leading text of a paragraph matching normalized_prefix (ws-… (+7 more)

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

### Community 57 - "mapping.py"
Cohesion: 0.17
Nodes (14): build_map(), expand_facility_variants(), Issue, normalise_action(), In-memory PII <-> placeholder mapping. This module is deliberately pure: it…, Return the full organisation name plus short forms. "St. Aidan's General…, All strings that redact to a placeholder, plus collisions worth flagging., Expand entities into every surface form that should be redacted. Entity values… (+6 more)

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

### Community 76 - "app.py"
Cohesion: 0.09
Nodes (36): current(), documents(), _form_draft_key(), _form_draft_state(), _header_values_complete(), ingest_sources(), _invalidate_form_export(), main() (+28 more)

### Community 77 - "desktop.py"
Cohesion: 0.19
Nodes (17): app_data_dir(), bundle_root(), ensure_dirs(), find_local_model(), is_frozen(), _model_search_dirs(), models_dir(), output_dir() (+9 more)

### Community 78 - "with_banner"
Cohesion: 0.40
Nodes (5): Prepend the review banner, without duplicating one already there., with_banner(), test_generated_output_keeps_the_review_banner(), test_every_draft_carries_the_review_banner(), test_the_banner_is_not_duplicated_on_refinement()

### Community 80 - "Cloud generation transport (`CloudBackend`) — design"
Cohesion: 0.20
Nodes (9): Architecture, Cloud generation transport (`CloudBackend`) — design, `core/backends.py`, Follow-ups (not blocking), New module `core/cloud_client.py`, Privacy properties (unchanged, inherited), Problem, Scope (+1 more)

### Community 81 - "test_reference_library.py"
Cohesion: 0.18
Nodes (17): add_file(), Top-``k`` reference passages for ``query`` at ``granularity``. BM25, ``score >…, Store an uploaded reference file. Returns the stored filename., ReferenceHit, search(), _library(), fixture, Clinic reference library: paragraph chunking with heading tracking, BM25… (+9 more)

### Community 84 - "test_eval.py"
Cohesion: 0.09
Nodes (34): aggregate(), DraftScore, _headings(), _lexical_overlap(), _order_agreement(), The four target metrics, scored per draft and reducible to a mean. Format,…, Mean of each metric over ``scores`` (style_match over styled drafts only)., Fraction of ``a``'s headings that appear in ``b`` in the same relative order. (+26 more)

### Community 87 - "Lightweight review UX for de-identification — design"
Cohesion: 0.14
Nodes (13): 1. Confidence tiering (drives what gets a click at all), 2. One primary review view, not three, 3. The click-to-redact component, 4. Attestation & audit trail, 5. Crash-risk fixes, Architecture, Current state (for reference), Goals (+5 more)

### Community 88 - "test_deid_pipeline.py"
Cohesion: 0.06
Nodes (31): parametrize, Regression suite for the layered de-identification pipeline. Two guarantees,…, With REDACT_INPROSE_DATES False, a procedure date is clinical, not identity., DOB and admission/discharge dates carry identity, so they go., spaCy labels "ECG" and "NSTEMI" as organisations; the filter must drop them., One real value, one placeholder — the whole point of the mapping., The add action IS the human decision — no second click to confirm it., The map is a return value the caller holds; nothing module-level keeps it. (+23 more)

### Community 89 - "review_spans"
Cohesion: 0.21
Nodes (17): _entity_spans(), Unifies the two things a reviewer might still need to act on in one document's…, Every clickable span in ``redacted_text``, in reading order. ``confirmed`` is…, One clickable span in a document's redacted text., Placeholder occurrences for low-confidence, not-yet-confirmed entities., _residual_spans(), review_spans(), ReviewSpan (+9 more)

### Community 90 - "structured_spans"
Cohesion: 0.17
Nodes (12): _header_footer_bounds(), _plausible_surname(), Character ranges of the document's opening and closing lines., A clock time is identifying only when it belongs to an appointment., True if the trailing token of an initial+surname reads like a real name.…, Layer 1: deterministic regex detections over ``text``., structured_spans(), _time_span_wanted() (+4 more)

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
Cohesion: 0.15
Nodes (13): _flag_values(), fixture, parametrize, The reviewer gate: candidate highlighting, the adaptive checklist, and the no-…, The real test: nothing the corpus calls an identifier may appear., A dismissal key holds the span text, so it must be wiped with the rest., record(), test_a_planted_residual_is_flagged() (+5 more)

### Community 95 - "select_backend"
Cohesion: 0.17
Nodes (14): Pick a backend. Returns ``(kind, backend, label)``. ``prefer`` lets the UI…, select_backend(), OllamaBackend, Local generation through the loopback-pinned Ollama daemon., The default (no prefer/model/temperature) path is unchanged., test_ollama_backend_default_temperature_is_zero(), test_select_backend_falls_back_when_requested_model_not_installed(), test_select_backend_honours_explicit_ollama_model() (+6 more)

### Community 96 - "cloud_client.py"
Cohesion: 0.27
Nodes (11): CloudError, _config(), _post(), RuntimeError, Transport for the optional cloud generation backend. Reached only when a…, Yield the payload of each ``data:`` line in an SSE stream., A recoverable problem talking to the configured cloud provider., Return ``(api_key, base_url, model)`` from the environment, or raise. (+3 more)

### Community 97 - "test_generation_setup.py"
Cohesion: 0.10
Nodes (12): mapping_module(), _nothing_available(), First-run generation setup: never an empty panel, and the egress line held. The…, A second call within the TTL must not re-probe Ollama., The one outbound path must not be reachable from the de-id flow., A fresh PC: no Ollama, no model file, no cloud., test_a_fresh_pc_is_not_ready_and_says_what_to_do(), test_a_present_gguf_makes_it_ready() (+4 more)

### Community 98 - "CareScribe clinical drafting model — model card"
Cohesion: 0.40
Nodes (4): CareScribe clinical drafting model — model card, Evaluation, Known limitations, Training data

### Community 99 - "expand_name_variants"
Cohesion: 0.17
Nodes (12): expand_name_variants(), _initial_letters(), name_core(), Split a name into its parts with any leading honorific removed. "Mrs Margaret…, Initials for a name, with hyphenated components contributing each part.…, Return every plausible written form of one person's name. Covers: the full…, Dr" as a standalone form would redact every "Dr" in the document., St." must never become a bare "St" that matches clinical text. (+4 more)

### Community 100 - "BM25"
Cohesion: 0.18
Nodes (9): ExemplarError, RuntimeError, Raised when an exemplar cannot be stored — e.g. it still holds an identifier., RuntimeError, Raised when a reference file cannot be stored., ReferenceError, BM25, Okapi BM25. ``documents`` is a list of token lists. (+1 more)

### Community 101 - "<id> — <title>"
Cohesion: 0.29
Nodes (6): Acceptance criteria, Do NOT touch, Files in scope, Goal, <id> — <title>, Notes

### Community 102 - "analyze"
Cohesion: 0.11
Nodes (19): analyze(), _crosses_paragraph_break(), flatten_lines(), gliner_spans(), Layer 3: GLiNER detections, or an empty list when it isn't installed., Run every enabled layer over ``text`` and return reviewable entities. Each…, One detection, in character offsets over the source text., Return ``text`` with every line break collapsed to one space, plus an offset… (+11 more)

### Community 103 - "ner_spans"
Cohesion: 0.18
Nodes (11): ner_spans(), Layer 2: Presidio/spaCy detections, mapped onto CareScribe entity types.…, REDACT_INPROSE_DATES flag, expand_org_variants (Layer 4 — variant expansion), Protected terms list (never redacted), In-prose date redaction policy, Layered de-identification pipeline, GLiNER (optional Layer 3 NER) (+3 more)

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
Cohesion: 0.10
Nodes (28): BatchError, list_folder(), RuntimeError, Return the supported documents in ``folder``, sorted by name. Non-recursive on…, Findings from the safety sweep, minus the ones the reviewer has cleared. A…, Write approved de-identified text to the output folder. Re-runs the safety…, Raised for input-folder and output-write problems., sweep() (+20 more)

### Community 111 - "blocking_reason"
Cohesion: 0.17
Nodes (11): blocking_reason(), The approval gate. Only the **authoritative safety sweep** blocks approval. A…, Why Approve is disabled, in one short line. Empty string means it isn't.…, Low-confidence redactions are already in place; the permissive flags are…, The streamlined gate: a permissive flag the reviewer left untouched does not…, test_advisory_spans_do_not_block_approval(), test_an_advisory_flag_alone_no_longer_blocks_approval(), test_approval_is_blocked_while_the_sweep_has_findings() (+3 more)

### Community 112 - "main"
Cohesion: 0.27
Nodes (9): The bundled Streamlit config that pins the server to loopback., Resolve a bundled resource, in a build or in a checkout., resource_path(), streamlit_config_path(), _guarded(), main(), Headless smoke test for the packaged app. Runs a synthetic corpus document…, test_resources_resolve_in_a_checkout() (+1 more)

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

### Community 117 - "reidentify"
Cohesion: 0.18
Nodes (11): Outcome of a re-identification pass., Swap placeholders back to originals, repairing mangled tokens. Never raises on…, Swap placeholders back to their original values. Thin wrapper over…, reidentify(), reidentify_detailed(), ReidentifyResult, test_empty_map_is_a_no_op(), test_invented_placeholder_is_left_alone() (+3 more)

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
Cohesion: 0.17
Nodes (19): Add clinic reference files (formulary, pathways, protocols) to a local library.…, _render_reference_uploader(), _all_chunks(), _bounded(), Chunk, _dir(), _files(), is_empty() (+11 more)

### Community 122 - "test_clinical_forms.py"
Cohesion: 0.24
Nodes (9): _load(), Generic table-row classification: which rows are fields, which are section…, test_biopsychosocial_spec_field_count_and_grid(), test_session_notes_field_walk_finds_nine_fields(), test_session_notes_signature_row_is_excluded(), test_session_notes_spec(), test_treatment_review_header_fields(), test_treatment_review_spec_has_fourteen_fields() (+1 more)

### Community 123 - "CloudBackend"
Cohesion: 0.22
Nodes (9): CloudBackend, A remote provider, reachable only when explicitly configured. Receives approved…, test_cloud_backend_streams_via_the_transport(), test_cloud_backend_translates_transport_errors_to_backend_error(), A key left by another tool must not silently turn on off-device work., It must not quietly fall back to a local backend and look like it worked., test_a_stray_api_key_alone_does_not_enable_cloud(), test_cloud_backend_cannot_be_constructed_when_off() (+1 more)

### Community 126 - "test_mapping.py"
Cohesion: 0.11
Nodes (22): assign_placeholders(), dedupe_entities(), normalise_type(), Coerce a model-supplied type string onto the canonical list., Drop blank and duplicate entities, keeping first-seen order and casing.…, Attach a stable placeholder to each unique entity. A type with exactly one…, parametrize, Mapping-layer checks: type normalisation, surface forms, and re-identification.… (+14 more)

### Community 127 - "parse_fields"
Cohesion: 0.44
Nodes (9): parse_fields(), Turn the model's marker-delimited output into ``{field_key: text}``. Any field…, _spec(), test_parse_fields_defaults_missing_field_to_not_documented(), test_parse_fields_first_occurrence_wins_on_duplicate_marker(), test_parse_fields_handles_empty_output(), test_parse_fields_happy_path(), test_parse_fields_ignores_unknown_marker_without_raising() (+1 more)

### Community 131 - "canonical_person_key"
Cohesion: 0.22
Nodes (9): canonical_person_key(), keys_are_compatible(), A stable identity key for one person: full given name plus surname. This…, True if two canonical keys can denote the same person. Exact match, or one side…, test_canonical_key_separates_two_people_with_one_surname(), test_canonical_key_unifies_the_forms_of_one_person(), test_a_shared_surname_is_not_a_shared_identity(), test_an_initial_can_stand_in_for_a_given_name() (+1 more)

### Community 132 - "resolve_placeholder"
Cohesion: 0.29
Nodes (7): _edit_distance(), Levenshtein distance, short-circuiting once it exceeds ``cap``., Map a possibly-corrupted placeholder onto a known one. Returns the exact token…, resolve_placeholder(), Guessing between [MRN_1] and [MRN_2] would attach the wrong identity., test_ambiguous_placeholder_is_refused_not_guessed(), test_edit_distance_caps_out()

### Community 133 - "exemplars.py"
Cohesion: 0.20
Nodes (9): House-style exemplar retrieval for clinical-form generation. A clinic…, Core logic: Ollama access, ingestion, de-identification, care notes, PHI…, Per-field retrieval planning for clinical-form generation. Roadmap item E…, Deterministic planner driven by a keyword taxonomy over field labels., RuleBasedPlanner, query_tokens(), Okapi BM25 over a small in-memory document set — standard library only. Shared…, Tokens for the *query* side — content words only. (+1 more)

### Community 134 - "carenotes.py"
Cohesion: 0.12
Nodes (21): assert_no_residual_identifiers(), CareNoteError, load_prompt(), RuntimeError, Care note generation — local, on approved de-identified text only. The contract…, The shared preamble — role, anti-fabrication rules, placeholder rules., Refuse to send text the residual sweep still flags. :func:`assert_deidentified`…, Revise an existing draft against a follow-up instruction. Operates on the same… (+13 more)

### Community 135 - "render_generation_panel"
Cohesion: 0.14
Nodes (17): _active_backend(), _as_docx(), _draft_state(), Resolve the backend to generate with, honouring saved settings. Centralises…, A concrete "it works", rather than asking the clinician to trust a flag., Generate, refine, re-identify and export — for one approved document. Two…, First-pass generation. The model receives de-identified text only., The de-identified draft, refinement, re-identification, and exports. (+9 more)

### Community 137 - "is_model_present"
Cohesion: 0.50
Nodes (4): is_model_present(), True if a usable model file is already on this computer. This is the marker…, Setup is one-time because the file itself is the state., test_model_presence_is_the_persisted_marker()

### Community 138 - "rebuild"
Cohesion: 0.22
Nodes (9): Re-derive redacted text and the PHI map from a reviewer-edited table. Called…, rebuild(), Marking a row Keep must un-redact exactly that value and nothing else., A value the layers missed is expanded like a detected one., A false positive the reviewer deleted must stay deleted., test_add_manual_entity_expands_variants(), test_keep_action_leaves_the_text_alone(), test_rebuild_does_not_resurrect_deleted_rows() (+1 more)

### Community 140 - "get_analyzer"
Cohesion: 0.20
Nodes (11): cache_resource, load_detection_engine(), Load the NER model once per session, not once per rerun. Streamlit re-runs the…, engine_status(), get_analyzer(), get_gliner(), Return the shared Presidio analyzer, or ``None`` if it can't be built. First…, Return the shared GLiNER model, or ``None`` if it isn't available. Guarded end… (+3 more)

### Community 141 - "_run"
Cohesion: 0.60
Nodes (4): AppTest, _run(), test_saving_settings_persists_and_survives_reload(), test_settings_expander_renders_without_error()

### Community 142 - "theme.py"
Cohesion: 0.33
Nodes (4): CareScribe UI layer — the visual identity, applied over Streamlit. `theme.CSS`…, inject(), CareScribe visual identity — one stylesheet, injected once per rerun. DIRECTION…, Apply the stylesheet. Import Streamlit lazily so the module stays cheap.

### Community 143 - "wipe_phi"
Cohesion: 0.67
Nodes (4): PHI_KEYS (session-state PHI registry), Drop every document, identifier table, and identity map from memory., wipe_phi(), Bug: form_drafts never registered with PHI_KEYS/wipe_phi

### Community 144 - "resolve_model_path"
Cohesion: 0.50
Nodes (5): available_models(), Where a spaCy model package actually lives, or ``None`` if absent. Resolved…, Every spaCy model importable in this environment., resolve_model_path(), test_model_paths_resolve_explicitly()

### Community 145 - "document_has_text_boxes"
Cohesion: 0.33
Nodes (6): document_has_text_boxes(), True if a .docx holds text this redaction pass cannot reach., has_unreachable_text(), True if the document holds text this module cannot reach. Text boxes,…, test_a_document_with_a_text_box_is_flagged(), test_a_plain_document_is_not_flagged()

### Community 147 - "_fresh_generation_status_cache"
Cohesion: 0.50
Nodes (4): _cloud_off(), _fresh_generation_status_cache(), fixture, generation_status() is now @st.cache_data(ttl=5) — a process-global cache keyed…

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
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

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
- **Why does `deidentify()` connect `deidentify` to `test_app.py`, `deidentify.py`, `test_app_screens.py`, `DeidResult`, `test_pipeline_runs_without_ner`, `test_pipeline_is_deterministic`, `test_a_date_entity_never_spans_a_line_break`, `available_forms`, `test_deid_regressions.py`, `DeidentificationError`, `extract_text`, `test_stress_corpus.py`, `load_documents`, `redact`, `residual_scan`, `mapping.py`, `test_deid_pipeline.py`, `NoEgress`, `test_generation_setup.py`, `analyze`, `test_batch.py`, `run_eval.py`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `FormType` connect `FormType` to `test_assemble_pipeline.py`, `EncounterFacts`, `schema.py`, `build_dataset.py`, `test_train_and_grammar.py`, `validators.py`, `test_eval.py`, `run_eval.py`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._