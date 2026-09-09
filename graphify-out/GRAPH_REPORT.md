# Graph Report - medgpt  (2026-09-08)

## Corpus Check
- 206 files · ~172,504 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3027 nodes · 6022 edges · 170 communities (142 shown, 28 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 107 edges (avg confidence: 0.63)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `af946954`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- candidate_residuals
- ingest.py
- build_dataset.py
- render_refinement
- EncounterType
- Reference: verified template structure
- template_ingest.py
- test_docx_roundtrip.py
- test_app.py
- schema.py
- generate_document
- test_template_ingest.py
- Local clinical LLM fine-tune — design
- patients.py
- devDependencies
- test_app_screens.py
- model_setup.py
- test_train_and_grammar.py
- test_reasoning_strip.py
- fill_template
- test_desktop_packaging.py
- get_form_spec
- test_cloud_client.py
- Clinic reference library — design
- main
- deidentify
- render_sidebar
- compilerOptions
- test_generation.py
- deidentify.py
- assert_deidentified
- test_patient_browser.py
- Architecture
- test_stress_corpus.py
- combine_sources
- write_approved
- FormType
- CareScribe — design system
- make_icon.py
- expand_name_variants
- exemplars.py
- theme.py
- ollama_client.py
- auth.py
- test_buildinfo.py
- docx_redact.py
- highlight_review
- test_combined_sources_generate_every_form_type_with_a_stub_backend
- test_docx_revision_leak.py
- batch.py
- Model Card for phi35-v1
- Installing CareScribe
- EncounterFacts
- Clinic-uploaded clinical form templates — design
- [Unreleased]
- Report templates (SOAP / GP letter / discharge / custom)
- Outpatient Respiratory Clinic Letter (doc03)
- App.tsx
- Reference: verified against the real codebase
- swarm-pipeline.md
- train/__init__.py
- Ward 7B Nursing Handover (doc04)
- inject
- Document
- test_clinical_form_templates.py
- carescribe/__init__.py
- deid_prompt.py
- prompts/__init__.py
- build_dmg.sh
- build_macos.sh
- rthook_carescribe.py
- tests/__init__.py
- run_all.py
- create_patient
- House-style exemplar retrieval — design
- clinical_forms.py
- load_settings
- test_crisis_lines_preserved.py
- Cloud generation transport (`CloudBackend`) — design
- reference_library.py
- merge_and_convert.sh
- GLiNER Deliberately Uninstalled
- run_eval.py
- Sample Source Documents README
- Recurring fictional staff roster (e.g. A. Whitfield) across documents
- Lightweight review UX for de-identification — design
- test_deid_pipeline.py
- review_spans
- query_tokens
- mapping.py
- Patient records store — design
- test_generator_backend.py
- test_review_gate.py
- test_backend_overrides.py
- load_documents
- test_generation_setup.py
- CareScribe clinical drafting model — model card
- NoEgress
- search
- <id> — <title>
- blocking_reason
- carenotes.py
- LLM backend flexibility + realistic test corpus + full-pipeline validation
- verify_frozen.py
- Per-field retrieval planner — design
- components/__init__.py
- test_build_dataset.py
- write_review_record
- Evaluation report
- compilerOptions
- redact
- test_docx_letterhead_leak.py
- AGENTS.md — rules for automated coding agents in this repo
- Task board
- Global Constraints
- test_full_pipeline_accounts.py
- finetune/
- test_medicare_number_leak.py
- load_protected_terms
- test_reference_library.py
- test_patient_pipeline.py
- set_active_user
- finetune/__init__.py
- integrate/__init__.py
- document_has_text_boxes
- test_clinical_forms_generate.py
- medgpt-finetune
- test_letterhead_address_leak.py
- Path
- Pattern
- extract_text
- create_user
- eval/__init__.py
- _build_analyzer
- CareScribe site
- assemble/__init__.py
- test_labelled_id_leaks.py
- structured_spans
- tsconfig.json
- Jordan Whitfield (fictional test client)
- Generation backend selection order (Ollama > built-in GGUF > Cloud)
- analyze
- app.py
- parse_fields
- applog.py
- render_draft
- backends.py
- desktop.py
- test_mapping.py
- run_app.py
- Pinned Dependencies
- test_sample_document_identifiers.py
- delete_patient
- rebuild
- assign_placeholders
- resolve_placeholder
- reidentify_detailed
- Path
- RuntimeError
- with_banner
- wipe_phi
- stress_report.py
- Any
- _RecordingBackend
- render_clinical_form_panel

## God Nodes (most connected - your core abstractions)
1. `deidentify()` - 92 edges
2. `Document` - 53 edges
3. `create_user()` - 52 edges
4. `EncounterFacts` - 49 edges
5. `get_form_spec()` - 47 edges
6. `create_patient()` - 43 edges
7. `FormType` - 43 edges
8. `residual_scan()` - 39 edges
9. `extract_text()` - 35 edges
10. `set_active_user()` - 35 edges

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

## Communities (170 total, 28 thin omitted)

### Community 0 - "candidate_residuals"
Cohesion: 0.12
Nodes (20): candidate_residuals(), Flag, _is_common(), outstanding(), _placeholder_ranges(), Residual-candidate highlighter — where the reviewer's eye should go first. This…, One span worth a second look, with its offsets in the redacted text., Identity for dismissal — per value, so one decision covers repeats. (+12 more)

### Community 1 - "ingest.py"
Cohesion: 0.13
Nodes (19): Any, _block_text(), _extract_docx(), _extract_pdf(), _extract_txt(), _header_footer_parts(), IngestError, normalise_line_endings() (+11 more)

### Community 2 - "build_dataset.py"
Cohesion: 0.10
Nodes (40): build(), _fallback_inject(), _load_datagen_config(), main(), Path, End-to-end: sampled encounters -> validated SFT pairs + manifest. python -m…, Return ``{"pairs": [...], "kept": k, "dropped": d, "reasons": {...}}``.…, Fill ``[[TOKEN]]`` slots with simple fake values. Used only until… (+32 more)

### Community 3 - "render_refinement"
Cohesion: 0.13
Nodes (19): _active_backend(), _invalidate_form_export(), Drop any previously re-identified/exportable content — called whenever the…, Resolve the backend to generate with, honouring saved settings. Centralises…, A concrete "it works", rather than asking the clinician to trust a flag., Render a stream token by token so a slow local model looks alive., First-pass generation. The model receives de-identified text only., Follow-up instructions, on de-identified text only. (+11 more)

### Community 4 - "EncounterType"
Cohesion: 0.13
Nodes (25): Choice, Any, Random, Range, Small seeded-sampling primitives shared by the vignette sampler. A vignette is…, Pick one of ``options`` uniformly., Pick one of ``options`` by matching ``weights``., An integer in ``[low, high]``, optionally rendered with ``unit``. (+17 more)

### Community 5 - "Reference: verified template structure"
Cohesion: 0.10
Nodes (20): carescribe/core/clinical_forms.py (module), Refine prompt (clinical form, marker-preserving), Refine prompt (free-form draft revision), Clinical Form Generation (APS Templates) Implementation Plan, Global Constraints, Reference: verified template structure, Self-Review Notes (for the implementer), Task 10: End-to-end generation glue (`generate_form_document`, `refine_form_document`, `render_preview`) (+12 more)

### Community 6 - "template_ingest.py"
Cohesion: 0.13
Nodes (27): ClinicalFormError, RuntimeError, Raised when a clinical form can't be built or filled., slugify(), delete_template(), _find_grids(), _infer_header(), _is_blank_row() (+19 more)

### Community 7 - "test_docx_roundtrip.py"
Cohesion: 0.09
Nodes (33): approved_map(), The reviewer-approved ``{literal: placeholder}`` map for the Word pass. This is…, extract_text(), Flatten a docx to text (body + tables + headers/footers) for a residual scan., _build(), fixture, parametrize, Word round-trip: upload -> redact -> download, structure preserved. The… (+25 more)

### Community 8 - "test_app.py"
Cohesion: 0.10
Nodes (40): analysed_batch(), _clean_auto_doc(), data_editors(), loaded_batch(), _NullBackend, AppTest, UI checks for the batch review app via Streamlit's AppTest. No server of any…, After the read-and-confirmed tick, a clean auto-confidence document has nothing… (+32 more)

### Community 9 - "schema.py"
Cohesion: 0.09
Nodes (35): BaseModel, field_validator, _blank_for(), expand(), Random, Turn vignettes into `EncounterFacts` instances with a seeded RNG. `expand`…, Yield ``n`` `EncounterFacts`, deterministic for a given ``seed``., Build one `EncounterFacts` from a vignette. With ``gap_probability`` > 0, each… (+27 more)

### Community 10 - "generate_document"
Cohesion: 0.11
Nodes (24): generate_document(), Stream a drafted document from approved de-identified text. ``phi_values`` is…, parametrize, A 2-char mapping value must not refuse a clean draft just because those…, The boundary check must not weaken a real leak: a short value standing alone as…, The complement of the mapping-value check: a leaked identifier that was never…, `acknowledged` carries the residual-sweep findings approval accepted (a town…, `phi_values` exists to assert absence, never to be forwarded. (+16 more)

### Community 11 - "test_template_ingest.py"
Cohesion: 0.11
Nodes (25): Let a clinic add its own table-based .docx form to the selector. Parsing and…, _render_template_uploader(), available_forms(), (form_id, title) pairs — bundled forms first, then clinic-uploaded ones., fill_parsed_template(), Fill an in-memory copy of ``original_docx`` from ``spec``'s anchors. A thin…, Validate an uploaded ``.docx``, store it, and return its new form id. Raises…, save_template() (+17 more)

### Community 12 - "Local clinical LLM fine-tune — design"
Cohesion: 0.06
Nodes (30): 10. Workstream E — integration, 11. What needs a human / external resource, 12. Milestones (testable deliverables), 13. Testing strategy, 1. Goal, 2. Constraints inherited from CareScribe, 3. Approach (selected), 4. Base model (+22 more)

### Community 13 - "patients.py"
Cohesion: 0.12
Nodes (29): _clean_name(), get_patient(), _now(), Patient, patient_dir(), PatientError, patients_root(), Path (+21 more)

### Community 14 - "devDependencies"
Cohesion: 0.06
Nodes (35): lucide-react, oxlint, react, react-dom, dependencies, lucide-react, react, react-dom (+27 more)

### Community 15 - "test_app_screens.py"
Cohesion: 0.10
Nodes (32): deid(), ner_available(), fixture, Shared pytest fixtures. The spaCy model load costs several seconds, so the…, The full pipeline's output for the fixture document., True when a spaCy model loaded — layer 2 tests skip without one., raw_text(), redacted() (+24 more)

### Community 16 - "model_setup.py"
Cohesion: 0.11
Nodes (26): Option A. The only outbound request the app makes, on an explicit click., run_model_download(), clear_partial_download(), download_model(), _free_bytes(), is_model_present(), model_destination(), ModelSetupError (+18 more)

### Community 17 - "test_train_and_grammar.py"
Cohesion: 0.05
Nodes (54): _body_rules(), compile_grammar(), field_grammar(), _lit(), note_grammar(), _placeholder_rule(), GBNF grammars for constrained local decoding — a structural guarantee on top of…, Compile a GBNF string with llama-cpp-python, or return ``None``. Never raises:… (+46 more)

### Community 18 - "test_reasoning_strip.py"
Cohesion: 0.11
Nodes (28): generate_care_note(), Remove a model's reasoning monologue from a finished draft. Idempotent. Text…, Draft a care note from ALREADY DE-IDENTIFIED text, returning it whole. The…, strip_reasoning(), _drain(), Generation must hand the clinician the finished document, not the model's…, A backend that prefixes its answer with a planning monologue., ReasoningBackend (+20 more)

### Community 19 - "fill_template"
Cohesion: 0.14
Nodes (22): _clear_cell(), _dedupe_row(), _fill_cell(), _fill_cell_after_label(), _fill_header_cell(), fill_template(), Remove every paragraph after the first, and every run in the first, leaving one…, Overwrite a dedicated value cell (label lives in a different cell). (+14 more)

### Community 20 - "test_desktop_packaging.py"
Cohesion: 0.08
Nodes (18): available_ram_gb(), ram_verdict(), Total system RAM in GB, or 0.0 if it cannot be determined., Whether this machine can run the bundled local model. Returns a verdict rather…, _cloud_off(), fixture, The packaging invariants: what the desktop app may and may not do. Packaging is…, No key may be committed, defaulted, or written anywhere. (+10 more)

### Community 21 - "get_form_spec"
Cohesion: 0.17
Nodes (21): get_form_spec(), plan(), _load(), Generic table-row classification: which rows are fields, which are section…, test_biopsychosocial_spec_field_count_and_grid(), test_no_field_key_collides_within_a_spec(), test_session_notes_field_walk_finds_nine_fields(), test_session_notes_signature_row_is_excluded() (+13 more)

### Community 22 - "test_cloud_client.py"
Cohesion: 0.10
Nodes (25): CloudError, _config(), _post(), RuntimeError, Transport for the optional cloud generation backend. Reached only when a…, Yield the payload of each ``data:`` line in an SSE stream., Stream a completion from the configured cloud provider, yielding text. Raises…, A recoverable problem talking to the configured cloud provider. (+17 more)

### Community 23 - "Clinic reference library — design"
Cohesion: 0.17
Nodes (11): `app.py`, Architecture, Clinic reference library — design, Decision, Follow-ups (not blocking), New `core/reference_library.py`, Privacy / safety, Problem (+3 more)

### Community 24 - "main"
Cohesion: 0.12
Nodes (19): current(), documents(), ensure_engine_ready(), ingest_sources(), main(), _pipeline_step(), _privacy_state(), Load the model at startup, behind a visible spinner. Deliberately not lazy. If… (+11 more)

### Community 25 - "deidentify"
Cohesion: 0.06
Nodes (61): deidentify(), Run the full local pipeline over one document. CPU-only and offline: no model…, _mrn_values(), parametrize, Regression suite for the five leaks found on a second, non-fixture document.…, The precision guard that keeps clinical context intact., Layer 1 must carry this on its own — NER catching it is luck, not a guarantee., Regardless of REDACT_INPROSE_DATES, which stays False by default. (+53 more)

### Community 26 - "render_sidebar"
Cohesion: 0.10
Nodes (32): _model_card_dialog(), Name the generation model with a readable label; the card opens in a dialog…, _render_generation_model(), render_sidebar(), chip(), detection_layer(), empty_state(), _esc() (+24 more)

### Community 27 - "compilerOptions"
Cohesion: 0.08
Nodes (23): DOM, src, vite/client, compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx (+15 more)

### Community 28 - "test_generation.py"
Cohesion: 0.07
Nodes (33): finalise(), Build the user prompt for one template with the source text embedded., Re-identify a draft locally and refuse to hand back a leaky document. Returns…, render_prompt(), check_placeholder_integrity(), Compare a draft's bracketed tokens against the placeholders it should use. An…, Local re-identification of a generated draft. Returns ``(text, unresolved)``.…, reidentify_document() (+25 more)

### Community 29 - "deidentify.py"
Cohesion: 0.06
Nodes (51): classify_person(), _collapse_facility_subsets(), _collapse_person_subsets(), date_span_wanted(), engine_status(), get_gliner(), gliner_spans(), _has_contact_anchor() (+43 more)

### Community 30 - "assert_deidentified"
Cohesion: 0.11
Nodes (19): assert_deidentified(), Backend, CloudBackend (unwired seam), Protocol, True only when ``needle`` occurs in ``haystack`` as a whole token run. Both are…, Refuse to send anything carrying a value from the identity mapping. A cheap,…, One method wide: the seam a different provider would be swapped in at.…, _value_present() (+11 more)

### Community 31 - "test_patient_browser.py"
Cohesion: 0.08
Nodes (44): FiledDocument, document_label(), filter_patients(), format_modified(), group_documents_by_kind(), human_size(), kind_label(), normalise_query() (+36 more)

### Community 32 - "Architecture"
Cohesion: 0.13
Nodes (14): 1. Template assets, 2. Form spec extraction, 3. Header fields (practitioner-entered), 4. Multi-document source combination, 5. Generation, 6. Review, 7. Export, 8. UI (`app.py`, Step 5) (+6 more)

### Community 33 - "test_stress_corpus.py"
Cohesion: 0.05
Nodes (48): answer_key.json, Community MH Discharge Letter (doc01), Mohammed Al-Rashid ('Mo'), Cardiology Discharge Summary (doc02), Margaret Elizabeth Chen ('Peggy'), Elspeth Mackenzie-Ford ('Ellie'), GP Referral Letter (doc05), Priya Venkataraman (+40 more)

### Community 34 - "combine_sources"
Cohesion: 0.21
Nodes (13): combine_sources(), Concatenate several documents' de-identified text into one source. ``sources``…, Regression test for Finding 3: raw filename must not leak into model-facing…, Regression test for Finding 1: cap at 26 documents (A-Z)., Regression test for Finding 1: prefixed placeholders must match PLACEHOLDER_RE.…, Regression test for Finding 2: text and map rewrites must be consistent. A…, test_combine_sources_no_filename_in_output(), test_combine_sources_non_standard_placeholder_consistency() (+5 more)

### Community 35 - "write_approved"
Cohesion: 0.12
Nodes (23): list_folder(), Return the supported documents in ``folder``, sorted by name. Non-recursive on…, Findings from the safety sweep, minus the ones the reviewer has cleared. A…, Write approved de-identified text to the output folder. Re-runs the safety…, sweep(), write_approved(), Batch loading and the approved-write path. The privacy invariant under test:…, The guarantee must not depend on the UI having run the sweep first. (+15 more)

### Community 36 - "FormType"
Cohesion: 0.14
Nodes (20): build_messages(), Care note templates. Every template shares the same hard rule: the input is…, Return ``(system, user)`` for a template label and de-identified document., Enum, FormType, The output form a training example asks the model to fill., build_messages(), default_instruction() (+12 more)

### Community 37 - "CareScribe — design system"
Cohesion: 0.20
Nodes (9): Browser surfaces, CareScribe — design system, Components (`carescribe/ui/components.py`), Direction, Palette, Sidebar order, Space & shape, Type (+1 more)

### Community 38 - "make_icon.py"
Cohesion: 0.29
Nodes (12): Image, _load_font(), main(), Path, Generate CareScribe's placeholder icon. A real icon is a design job; this…, The first usable bold face, or ``None`` if none of them load., A rounded square with "CS" centred on it., macOS only. Silently skipped elsewhere — the .app is built on a Mac. (+4 more)

### Community 39 - "expand_name_variants"
Cohesion: 0.09
Nodes (24): _collapse_person_identities(), True for a person row whose role is known (patient / relative / clinician)., Collapse every written form of one person onto a single entity row.…, _specific_person_type(), canonical_person_key(), expand_name_variants(), _initial_letters(), keys_are_compatible() (+16 more)

### Community 40 - "exemplars.py"
Cohesion: 0.14
Nodes (25): add_exemplar(), count(), _dir(), _load(), _path(), Path, House-style exemplar retrieval for clinical-form generation. A clinic…, Top-``k`` stored values for ``field_key``, ranked by BM25 against ``query``. (+17 more)

### Community 41 - "theme.py"
Cohesion: 0.33
Nodes (4): CareScribe UI layer — the visual identity, applied over Streamlit. `theme.CSS`…, inject(), CareScribe visual identity — one stylesheet, injected once per rerun. DIRECTION…, Apply the stylesheet. Import Streamlit lazily so the module stays cheap.

### Community 42 - "ollama_client.py"
Cohesion: 0.15
Nodes (20): default_model(), generate(), is_up(), list_models(), missing_model_message(), OllamaError, RuntimeError, Local Ollama client — pinned to the loopback interface. Generation is the first… (+12 more)

### Community 43 - "auth.py"
Cohesion: 0.08
Nodes (43): apply_scope(), current_user_id(), _honesty_caption(), is_signed_in(), normalise_username(), password_confirmation_error(), password_error(), The sign-in gate, and the account panel in the sidebar. CareScribe now opens on… (+35 more)

### Community 44 - "test_buildinfo.py"
Cohesion: 0.24
Nodes (10): build_info(), Build information for CareScribe., Return standard HTTP User-Agent string., Return application identity and version., user_agent(), Tests for buildinfo module., Test that user_agent returns correct format., Test that build_info returns correct name and version. (+2 more)

### Community 45 - "docx_redact.py"
Cohesion: 0.23
Nodes (13): apply_redactions(), _delete_prefix(), _iter_groups(), _iter_paragraphs(), _norm(), Structure-preserving .docx redaction. apply_redactions(path_in, path_out,…, Redact a literal split across a paragraph boundary (wrapped name)., Delete the leading text of a paragraph matching normalized_prefix (ws-… (+5 more)

### Community 46 - "highlight_review"
Cohesion: 0.24
Nodes (9): highlight_review(), Click-to-redact highlighted text. Renders already-redacted (or already-flagged)…, Render ``html`` and return the ``data-span-id`` of the last click. Returns…, _frontend_path(), Path, Offline-first: nothing in this file may fetch from a CDN., test_frontend_file_exists(), test_frontend_has_no_external_script_or_link_tags() (+1 more)

### Community 47 - "test_combined_sources_generate_every_form_type_with_a_stub_backend"
Cohesion: 0.32
Nodes (6): skipif, parametrize, Deterministic stand-in for a real generation backend., _StubBackend, test_combined_sources_generate_every_form_type_with_a_stub_backend(), test_ingest_and_deidentify_every_sample_document()

### Community 48 - "test_docx_revision_leak.py"
Cohesion: 0.19
Nodes (18): _document(), Regression: text deleted with track changes on rode out in the approved file.…, Why the sweep has to be what catches it: nothing else can see it., Before the fix this wrote a file with the deleted name still inside it., w:author carries a clinician's name in an attribute, not a text node., Comments are a separate part of the package that no other pass loads., A deletion is not itself a finding -- only an identifier inside one is., A .docx whose body is ordinary and whose revision history is not. (+10 more)

### Community 49 - "batch.py"
Cohesion: 0.16
Nodes (16): BatchError, _blanked_properties(), _document_property_text(), Batch input and approved-output handling. The single module in CareScribe that…, Blank the .docx metadata fields that carry names, places and dates. Rewrites…, Every scrap of text in the .docx property parts, for the residual sweep. Read…, Text in a .docx that no other pass reads: deletions, comments, notes. All of it…, Header, footer and text-box content -- what ``_extract_docx`` never reads.… (+8 more)

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

### Community 54 - "[Unreleased]"
Cohesion: 0.25
Nodes (7): [0.1.0] - 2026-09-01, Added, Added, Added, Changelog, Fixed, [Unreleased]

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

### Community 63 - "Document"
Cohesion: 0.34
Nodes (22): Document, One document's state for the whole review pass. Everything here except…, build_case_conference_note(), build_discharge_summary(), build_gp_progress_note(), build_imaging_report(), build_intake_notes(), build_medication_chart() (+14 more)

### Community 64 - "test_clinical_form_templates.py"
Cohesion: 0.50
Nodes (3): parametrize, The three bundled APS templates load and match the structure this feature's…, test_bundled_template_shape()

### Community 73 - "create_patient"
Cohesion: 0.13
Nodes (27): create_patient(), patient_output_dir(), Where this patient's approved de-identified artefacts are filed., Create a patient folder and roster entry. Returns the new record., test_filed_documents_are_scoped(), fixture, parametrize, The per-patient records store. `patients.py` owns no detection logic — it is… (+19 more)

### Community 74 - "House-style exemplar retrieval — design"
Cohesion: 0.18
Nodes (10): `app.py`, Architecture, `core/clinical_forms.py`, Follow-ups (not blocking), House-style exemplar retrieval — design, New module `core/exemplars.py`, Privacy, Problem (+2 more)

### Community 76 - "clinical_forms.py"
Cohesion: 0.16
Nodes (22): _biopsychosocial_spec(), build_prompt(), _form_grammar(), FormField, FormSpec, generate_form_document(), _grid_fields(), HeaderField (+14 more)

### Community 77 - "load_settings"
Cohesion: 0.25
Nodes (15): load_settings(), _path(), Persisted app settings — which generation backend/model/temperature to use.…, Read persisted settings. A missing or unreadable file yields defaults., Persist non-secret settings, creating the app data dir if needed., save_settings(), Settings, test_load_settings_coerces_stringy_temperature() (+7 more)

### Community 78 - "test_crisis_lines_preserved.py"
Cohesion: 0.33
Nodes (6): parametrize, Regression: public crisis-line names are not identifiers and must not be…, The allow-list entry is the helpline name only — a real name beside it still…, test_a_crisis_line_name_survives_deidentification(), test_a_person_named_near_a_crisis_line_is_still_redacted(), test_crisis_line_name_and_number_both_survive_in_context()

### Community 80 - "Cloud generation transport (`CloudBackend`) — design"
Cohesion: 0.20
Nodes (9): Architecture, Cloud generation transport (`CloudBackend`) — design, `core/backends.py`, Follow-ups (not blocking), New module `core/cloud_client.py`, Privacy properties (unchanged, inherited), Problem, Scope (+1 more)

### Community 81 - "reference_library.py"
Cohesion: 0.22
Nodes (14): Add clinic reference files (formulary, pathways, protocols) to a local library.…, _render_reference_uploader(), _all_chunks(), _bounded(), Chunk, _dir(), _files(), _paragraphs() (+6 more)

### Community 84 - "run_eval.py"
Cohesion: 0.07
Nodes (47): aggregate(), DraftScore, _headings(), _lexical_overlap(), _order_agreement(), The four target metrics, scored per draft and reducible to a mean. Format,…, Mean of each metric over ``scores`` (style_match over styled drafts only)., Fraction of ``a``'s headings that appear in ``b`` in the same relative order. (+39 more)

### Community 87 - "Lightweight review UX for de-identification — design"
Cohesion: 0.14
Nodes (13): 1. Confidence tiering (drives what gets a click at all), 2. One primary review view, not three, 3. The click-to-redact component, 4. Attestation & audit trail, 5. Crash-risk fixes, Architecture, Current state (for reference), Goals (+5 more)

### Community 88 - "test_deid_pipeline.py"
Cohesion: 0.04
Nodes (57): add_manual_entity(), DeidentificationError, DeidResult, RuntimeError, Raised when de-identification can't run at all., Add an identifier the tools missed and immediately re-redact. The new value…, Re-scan ALREADY-REDACTED text for anything that still looks identifying. Runs…, Everything the de-identification stage produces for one document. (+49 more)

### Community 89 - "review_spans"
Cohesion: 0.21
Nodes (17): _entity_spans(), Unifies the two things a reviewer might still need to act on in one document's…, Every clickable span in ``redacted_text``, in reading order. ``confirmed`` is…, One clickable span in a document's redacted text., Placeholder occurrences for low-confidence, not-yet-confirmed entities., _residual_spans(), review_spans(), ReviewSpan (+9 more)

### Community 90 - "query_tokens"
Cohesion: 0.20
Nodes (10): Protocol, Per-field retrieval planning for clinical-form generation. Roadmap item E…, Deterministic planner driven by a keyword taxonomy over field labels., RetrievalPlan, RetrievalPlanner, RuleBasedPlanner, query_tokens(), Okapi BM25 over a small in-memory document set — standard library only. Shared… (+2 more)

### Community 91 - "mapping.py"
Cohesion: 0.15
Nodes (16): build_map(), expand_facility_variants(), Issue, normalise_action(), normalise_type(), In-memory PII <-> placeholder mapping. This module is deliberately pure: it…, Coerce a model-supplied type string onto the canonical list., Return the full organisation name plus short forms. "St. Aidan's General… (+8 more)

### Community 92 - "Patient records store — design"
Cohesion: 0.11
Nodes (17): 10. Rejected alternatives, 1. Goal, 2. Constraints inherited from CareScribe, 3. The one deliberate change to the privacy posture, 4. Storage layout, 5.1 `carescribe/core/desktop.py`, 5.2 `carescribe/core/patients.py` (new), 5.3 `carescribe/core/batch.py` (+9 more)

### Community 93 - "test_generator_backend.py"
Cohesion: 0.11
Nodes (19): GeneratorBackend, get_backend(), OllamaBackend, OpenAICompatibleBackend, TemplateBackend, Test that TemplateBackend properly renders facts in proforma style, Test that TemplateBackend properly renders facts in prose style, Test that TemplateBackend is deterministic - same input gives same output (+11 more)

### Community 94 - "test_review_gate.py"
Cohesion: 0.15
Nodes (13): _flag_values(), fixture, parametrize, The reviewer gate: candidate highlighting, the adaptive checklist, and the no-…, The real test: nothing the corpus calls an identifier may appear., A dismissal key holds the span text, so it must be wiped with the rest., record(), test_a_planted_residual_is_flagged() (+5 more)

### Community 95 - "test_backend_overrides.py"
Cohesion: 0.10
Nodes (26): Pick a backend. Returns ``(kind, backend, label)``. ``prefer`` lets the UI…, select_backend(), OllamaBackend, Local generation through the loopback-pinned Ollama daemon., _backend_with_fake_model(), _FakeModel, _raising_stream(), The happy path must keep working: finish_reason 'stop' yields the text with no… (+18 more)

### Community 96 - "load_documents"
Cohesion: 0.14
Nodes (17): analyze_document(), load_documents(), The raw bytes behind an upload or a path, without copying it to disk., Extract text from uploads or paths. Returns ``(documents, errors)``. One…, Run the de-identification layers over one document, in place., _source_bytes(), FakeUpload, Stands in for a Streamlit UploadedFile. (+9 more)

### Community 97 - "test_generation_setup.py"
Cohesion: 0.05
Nodes (40): cache_data, generation_status(), _llama_runtime_available(), missing_reason(), Is generation usable right now, and if not, what should the user do? Kept…, One plain sentence on why generation is not available yet., Which generation backends are usable at this moment., Which backend would actually be used, matching the backend ladder. (+32 more)

### Community 98 - "CareScribe clinical drafting model — model card"
Cohesion: 0.40
Nodes (4): CareScribe clinical drafting model — model card, Evaluation, Known limitations, Training data

### Community 99 - "NoEgress"
Cohesion: 0.11
Nodes (15): NoEgress, Fails the test if anything opens a non-loopback socket. Loopback is allowed:…, Stands in for a model so the egress test does not need one installed., Load → de-identify → approve → generate, with egress forbidden., Re-identification is pure Python — it must not phone anywhere., StubBackend, test_reidentification_opens_no_socket(), test_the_whole_flow_opens_no_outbound_socket() (+7 more)

### Community 100 - "search"
Cohesion: 0.15
Nodes (12): ExemplarError, RuntimeError, Raised when an exemplar cannot be stored — e.g. it still holds an identifier., RuntimeError, Top-``k`` reference passages for ``query`` at ``granularity``. BM25, ``score >…, Raised when a reference file cannot be stored., ReferenceError, ReferenceHit (+4 more)

### Community 101 - "<id> — <title>"
Cohesion: 0.29
Nodes (6): Acceptance criteria, Do NOT touch, Files in scope, Goal, <id> — <title>, Notes

### Community 102 - "blocking_reason"
Cohesion: 0.17
Nodes (11): blocking_reason(), The approval gate. Only the **authoritative safety sweep** blocks approval. A…, Why Approve is disabled, in one short line. Empty string means it isn't.…, Low-confidence redactions are already in place; the permissive flags are…, The streamlined gate: a permissive flag the reviewer left untouched does not…, test_advisory_spans_do_not_block_approval(), test_an_advisory_flag_alone_no_longer_blocks_approval(), test_approval_is_blocked_while_the_sweep_has_findings() (+3 more)

### Community 103 - "carenotes.py"
Cohesion: 0.11
Nodes (25): assert_no_residual_identifiers(), CareNoteError, _ends_mid_tag(), load_prompt(), RuntimeError, Care note generation — local, on approved de-identified text only. The contract…, The shared preamble — role, anti-fabrication rules, placeholder rules., Refuse to send text the residual sweep still flags. :func:`assert_deidentified`… (+17 more)

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

### Community 109 - "write_review_record"
Cohesion: 0.13
Nodes (22): approved_docx_path(), approved_path(), _default_output_dir(), Reduce a filename to a safe output stem — no paths, no surprises., The folder a write lands in — an explicit override, or the default.…, Where the approved de-identified text for ``name`` will be written., Where the review audit sidecar for ``name`` will be written., Write the no-PHI audit sidecar for one approved document. Evidence that a… (+14 more)

### Community 111 - "compilerOptions"
Cohesion: 0.10
Nodes (19): node, vite.config.ts, compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection (+11 more)

### Community 112 - "redact"
Cohesion: 0.12
Nodes (17): find_known_as(), find_spans(), _form_pattern(), Pattern, Pull a patient's preferred name out of a "Known as:" field, if present., Whitespace-tolerant, case-insensitive pattern for one surface form. Tokens are…, Find non-overlapping ``(start, end, placeholder)`` spans for every form. All…, Replace every surface form of every entity with its placeholder. Replacement… (+9 more)

### Community 113 - "test_docx_letterhead_leak.py"
Cohesion: 0.09
Nodes (39): parametrize, _detected(), _document(), A .docx letterhead, and a text box: what is redacted and what is refused.…, None of these was extracted at all before the header/footer read., The whole point: a letterhead is redacted, not a document you cannot use., python-docx's paragraph walk does not descend into a w:txbxContent., Before the fix this call succeeded and wrote the box's contents to disk. (+31 more)

### Community 114 - "AGENTS.md — rules for automated coding agents in this repo"
Cohesion: 0.40
Nodes (4): AGENTS.md — rules for automated coding agents in this repo, Do, Never, Task spec shape

### Community 115 - "Task board"
Cohesion: 0.11
Nodes (17): App bug the user hit (2026-09-01) — FIXED in `e9bcc3b`, Fine-tune decisions locked (2026-09-01), Fine-tune hardware facts (2026-09-01), Fine-tune progress — cockpit-driven, COMMITTED on integration branch, Local clinical LLM fine-tune (started 2026-09-01), M3–M5 DONE — model trained, evaluated, integrated (2026-09-01), Pipeline incident 2026-09-01 (fixed), Punch-list — "address all 10 issues" (2026-09-02) (+9 more)

### Community 116 - "Global Constraints"
Cohesion: 0.18
Nodes (10): Global Constraints, LLM Backend Flexibility + Realistic Test Corpus Implementation Plan, Task 1: Settings persistence module, Task 2: `select_backend()` explicit model/temperature overrides + Ollama temperature fix, Task 3: Settings panel UI + wiring generation call sites through it, Task 4: Stress corpus expansion — batch 1 (5 documents), Task 5: Stress corpus expansion — batch 2 (5 documents), Task 6: Sample documents expansion (full-pipeline generation exercise) (+2 more)

### Community 117 - "test_full_pipeline_accounts.py"
Cohesion: 0.10
Nodes (41): filed_documents(), Approved artefacts filed for this patient, newest first., _approve_document(), _every_file(), Filed, AppTest, fixture, Path (+33 more)

### Community 118 - "finetune/"
Cohesion: 0.40
Nodes (4): Environment, finetune/, Layout, Milestones

### Community 119 - "test_medicare_number_leak.py"
Cohesion: 0.25
Nodes (10): _mrn_values(), parametrize, Regression: an Australian Medicare number left in the clear. Found by a cockpit…, The number after a Medicare label is taken, like any other MRN., A Medicare mention with no number attached is not a record-number hit., Safety-net: if a Medicare number ever reaches redacted text, approval blocks., test_a_medicare_labelled_number_is_detected_as_a_record_number(), test_residual_scan_catches_a_leaked_medicare_number() (+2 more)

### Community 120 - "load_protected_terms"
Cohesion: 0.29
Nodes (7): _build_protected_pattern(), load_protected_terms(), Read the editable allow-list. Blank lines and ``#`` comments are ignored., Re-read the allow-list from disk (the file is meant to be edited by hand)., reload_protected_terms(), Pattern, test_the_allow_list_is_an_editable_file()

### Community 121 - "test_reference_library.py"
Cohesion: 0.15
Nodes (19): add_file(), is_empty(), ``(filename, paragraph_count)`` per loaded reference file., Store an uploaded reference file. Returns the stored filename., sources(), _library(), fixture, Clinic reference library: paragraph chunking with heading tracking, BM25… (+11 more)

### Community 122 - "test_patient_pipeline.py"
Cohesion: 0.15
Nodes (25): _approve_document(), filed(), FiledCase, fixture, parametrize, Path, End-to-end evaluation of the patient records pipeline, one stage of the user…, Drive the whole pipeline once: two patients, 15 documents filed under one. (+17 more)

### Community 123 - "set_active_user"
Cohesion: 0.12
Nodes (31): warn(), active_user(), list_patients(), migrate_unscoped_into(), Scope every subsequent store call to one account, or to none. Passing ``None``…, The account the store is currently scoped to, or ``None``., Every readable patient, sorted by name (case-insensitive) then id. A folder…, Patient folders sitting in the base, from before accounts existed. These are… (+23 more)

### Community 126 - "document_has_text_boxes"
Cohesion: 0.50
Nodes (4): document_has_text_boxes(), True if a .docx holds text this redaction pass cannot reach., has_unreachable_text(), True if the document holds text this module cannot reach. Text boxes,…

### Community 127 - "test_clinical_forms_generate.py"
Cohesion: 0.23
Nodes (9): Human-readable rendering for display only — the marker text in ``draft_state``…, render_preview(), Captures exactly what generation handed the model — mirrors the fixture in…, RecordingBackend, test_generate_form_document_refuses_a_real_identifier(), test_generate_form_document_sends_the_field_marker_prompt(), test_refine_form_document_preserves_markers_instruction(), test_render_preview_defaults_missing_value() (+1 more)

### Community 131 - "test_letterhead_address_leak.py"
Cohesion: 0.31
Nodes (8): _letterhead_line(), parametrize, Regression: an unlabelled letterhead street address leaks in the clear. Found…, The de-identified form of the address/phone letterhead line., The new letterhead rule must not fire on a street word in a sentence., test_a_letterhead_street_address_line_is_taken_whole(), test_street_words_in_prose_are_not_over_redacted(), test_the_sample_letterhead_address_is_fully_redacted()

### Community 134 - "extract_text"
Cohesion: 0.25
Nodes (14): extract_text(), Extract plain text from an uploaded pdf/docx/txt file. Raises…, FakeUpload, parametrize, Document ingestion checks. No network, no temp copies of PHI., A Windows-authored .txt file must not leak its raw \\r into the pipeline. De-…, test_reads_a_file_path(), test_reads_the_encodings_clinical_exports_use() (+6 more)

### Community 135 - "create_user"
Cohesion: 0.05
Nodes (94): any_users(), _as_user(), authenticate(), change_password(), _check_password(), _clean_username(), create_user(), _derive() (+86 more)

### Community 137 - "_build_analyzer"
Cohesion: 0.10
Nodes (22): cache_resource, load_detection_engine(), Load the NER model once per session, not once per rerun. Streamlit re-runs the…, available_models(), _build_analyzer(), get_analyzer(), is_frozen_build(), ner_spans() (+14 more)

### Community 138 - "CareScribe site"
Cohesion: 0.50
Nodes (3): CareScribe site, Local, Notes

### Community 140 - "test_labelled_id_leaks.py"
Cohesion: 0.36
Nodes (8): _mrn_values(), parametrize, Regression: two more labelled patient/clinician record numbers left in the…, Guard against the widened value pattern breaking the shapes it already caught., test_a_labelled_ur_or_provider_number_is_detected(), test_bare_provider_or_ur_is_not_over_captured(), test_existing_labelled_record_numbers_still_detected(), test_the_sample_document_labelled_id_does_not_survive()

### Community 141 - "structured_spans"
Cohesion: 0.13
Nodes (15): _header_footer_bounds(), _plausible_surname(), True if the trailing token of an initial+surname reads like a real name.…, Layer 1: deterministic regex detections over ``text``., Character ranges of the document's opening and closing lines., structured_spans(), Layer 1 alone must still catch every purely structured identifier., A bare digit run is a lab value; only a labelled one is a record number. (+7 more)

### Community 143 - "Jordan Whitfield (fictional test client)"
Cohesion: 0.31
Nodes (9): 01_gp_referral_letter.docx, 02_biopsychosocial_intake_notes.docx, 03_session_log_progress_notes.docx, 04_treatment_review_source.docx, Biopsychosocial Assessment form, Client Session Notes form, Client Treatment Review form, Clinical-Forms Pipeline (upload -> de-identify -> approve -> combine sources -> generate form) (+1 more)

### Community 145 - "Generation backend selection order (Ollama > built-in GGUF > Cloud)"
Cohesion: 0.18
Nodes (11): core/model_setup.py (model download, isolated), packaging/build_macos.sh, packaging/build_windows.ps1, packaging/carescribe.iss (Inno Setup script), packaging/make_icon.py, The desktop app (PyInstaller packaging), Generation backend selection order (Ollama > built-in GGUF > Cloud), run_app.py entry point (+3 more)

### Community 146 - "analyze"
Cohesion: 0.15
Nodes (13): analyze(), _crosses_paragraph_break(), flatten_lines(), True if the ORIGINAL-text span ``text[start:end]`` contains a blank line., Run every enabled layer over ``text`` and return reviewable entities. Each…, Return ``text`` with every line break collapsed to one space, plus an offset…, An NHS number is Layer 1 (regex) — pattern-certain, no review needed., A bare forename with no structural corroboration is single-layer. (+5 more)

### Community 147 - "app.py"
Cohesion: 0.09
Nodes (38): active_output_dir(), active_patient_id(), _document_bytes(), document_flags(), entity_confirmed(), entity_frame(), flag_dismissals(), _model_card_path() (+30 more)

### Community 148 - "parse_fields"
Cohesion: 0.44
Nodes (9): parse_fields(), Turn the model's marker-delimited output into ``{field_key: text}``. Any field…, _spec(), test_parse_fields_defaults_missing_field_to_not_documented(), test_parse_fields_first_occurrence_wins_on_duplicate_marker(), test_parse_fields_handles_empty_output(), test_parse_fields_happy_path(), test_parse_fields_ignores_unknown_marker_without_raising() (+1 more)

### Community 149 - "applog.py"
Cohesion: 0.11
Nodes (33): BaseException, The last line of defence: a calm message instead of a stack trace. A clinician…, render_unexpected_error(), exception(), get_logger(), log(), log_path(), Path (+25 more)

### Community 150 - "render_draft"
Cohesion: 0.40
Nodes (6): _as_docx(), The de-identified draft, refinement, re-identification, and exports., Opt-in, local-only substitution of placeholders back to real values., Render generated text to a .docx in memory — nothing touches disk., render_draft(), render_reidentification()

### Community 151 - "backends.py"
Cohesion: 0.08
Nodes (30): privacy_indicator(), A persistent, honest statement of where data goes. It must change when cloud…, BackendError, cloud_enabled(), cloud_key_present(), cloud_provider(), CloudBackend, describe_backends() (+22 more)

### Community 152 - "desktop.py"
Cohesion: 0.14
Nodes (28): app_data_dir(), bundle_root(), ensure_dirs(), find_local_model(), is_frozen(), _model_search_dirs(), models_dir(), output_dir() (+20 more)

### Community 153 - "test_mapping.py"
Cohesion: 0.13
Nodes (18): dedupe_entities(), Drop blank and duplicate entities, keeping first-seen order and casing.…, Swap placeholders back to their original values. Thin wrapper over…, reidentify(), parametrize, Mapping-layer checks: type normalisation, surface forms, and re-identification.…, If ANY occurrence of a value was low-confidence, the whole entity is., test_dedupe_carries_the_keep_action() (+10 more)

### Community 154 - "run_app.py"
Cohesion: 0.16
Nodes (17): Popen, close_splash(), _fatal(), free_port(), main(), _no_window_kwargs(), CareScribe desktop launcher — the app's entry point. Starts the Streamlit…, Poll the loopback port until Streamlit answers. (+9 more)

### Community 155 - "Pinned Dependencies"
Cohesion: 0.25
Nodes (8): pandas, pdfplumber, Pinned Dependencies, presidio-analyzer, python-docx, spaCy, spaCy Model Fallback Chain, streamlit

### Community 156 - "test_sample_document_identifiers.py"
Cohesion: 0.43
Nodes (7): parametrize, Answer-key regression net for ``sample_documents/``. Unlike ``stress_corpus/``…, Whitfield" on its own (not just the full name) must not survive anywhere., _redacted(), test_patient_identifier_is_absent_from_redacted_text(), test_sample_document_residual_scan_is_clean(), test_the_patient_surname_alone_is_also_gone()

### Community 157 - "delete_patient"
Cohesion: 0.50
Nodes (4): delete_patient(), Remove a patient folder and everything filed in it., test_deleting_in_one_account_leaves_the_other_alone(), test_delete_an_unknown_id_raises()

### Community 158 - "rebuild"
Cohesion: 0.29
Nodes (7): Re-derive redacted text and the PHI map from a reviewer-edited table. Called…, rebuild(), Marking a row Keep must un-redact exactly that value and nothing else., A false positive the reviewer deleted must stay deleted., test_keep_action_leaves_the_text_alone(), test_rebuild_does_not_resurrect_deleted_rows(), test_rebuild_preserves_a_reviewer_edited_placeholder()

### Community 159 - "assign_placeholders"
Cohesion: 0.29
Nodes (7): assign_placeholders(), Attach a stable placeholder to each unique entity. A type with exactly one…, assign_placeholders is analyze()'s last step — a silent drop here is permanent., test_assign_placeholders_keeps_confidence(), test_existing_placeholder_is_preserved(), test_multiple_values_get_numbered_placeholders(), test_single_value_gets_a_bare_placeholder()

### Community 160 - "resolve_placeholder"
Cohesion: 0.29
Nodes (7): _edit_distance(), Levenshtein distance, short-circuiting once it exceeds ``cap``., Map a possibly-corrupted placeholder onto a known one. Returns the exact token…, resolve_placeholder(), Guessing between [MRN_1] and [MRN_2] would attach the wrong identity., test_ambiguous_placeholder_is_refused_not_guessed(), test_edit_distance_caps_out()

### Community 161 - "reidentify_detailed"
Cohesion: 0.33
Nodes (6): Outcome of a re-identification pass., Swap placeholders back to originals, repairing mangled tokens. Never raises on…, reidentify_detailed(), ReidentifyResult, test_invented_placeholder_is_left_alone(), test_mangled_placeholder_is_repaired()

### Community 164 - "with_banner"
Cohesion: 0.40
Nodes (5): Prepend the review banner, without duplicating one already there., with_banner(), test_generated_output_keeps_the_review_banner(), test_every_draft_carries_the_review_banner(), test_the_banner_is_not_duplicated_on_refinement()

### Community 165 - "wipe_phi"
Cohesion: 0.67
Nodes (4): PHI_KEYS (session-state PHI registry), Drop every document, identifier table, and identity map from memory., wipe_phi(), Bug: form_drafts never registered with PHI_KEYS/wipe_phi

### Community 166 - "stress_report.py"
Cohesion: 0.67
Nodes (3): main(), normalise(), Per-document pass/fail report for the stress corpus. python…

### Community 169 - "render_clinical_form_panel"
Cohesion: 0.13
Nodes (19): _draft_state(), _form_draft_key(), _form_draft_state(), _header_values_complete(), Which backend will be used, and the fix if none is available., Shown instead of an empty panel when no model is available yet. An empty…, Option B. Ollama does the fetching; the request goes to loopback., Generate, refine, re-identify and export — for one approved document. Two… (+11 more)

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
- **305 isolated node(s):** `medgpt-finetune`, `merge_and_convert.sh script`, `build_dmg.sh script`, `build_macos.sh script`, `$schema` (+300 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

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
- **Why does `deidentify()` connect `deidentify` to `build_dataset.py`, `test_letterhead_address_leak.py`, `test_app.py`, `_build_analyzer`, `test_labelled_id_leaks.py`, `test_app_screens.py`, `analyze`, `applog.py`, `test_sample_document_identifiers.py`, `deidentify.py`, `test_stress_corpus.py`, `write_approved`, `stress_report.py`, `test_combined_sources_generate_every_form_type_with_a_stub_backend`, `test_docx_revision_leak.py`, `create_patient`, `test_crisis_lines_preserved.py`, `test_deid_pipeline.py`, `mapping.py`, `load_documents`, `test_generation_setup.py`, `NoEgress`, `write_review_record`, `redact`, `test_docx_letterhead_leak.py`, `test_full_pipeline_accounts.py`, `test_medicare_number_leak.py`, `test_patient_pipeline.py`, `set_active_user`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `Document` connect `Document` to `load_documents`, `render_refinement`, `test_docx_roundtrip.py`, `test_app.py`, `render_clinical_form_panel`, `create_user`, `docx_redact.py`, `test_app_screens.py`, `batch.py`, `app.py`, `test_full_pipeline_accounts.py`, `render_draft`, `main`, `test_generation.py`, `document_has_text_boxes`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._