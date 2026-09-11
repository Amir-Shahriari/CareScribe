# Graph Report - medgpt  (2026-09-11)

## Corpus Check
- 261 files · ~207,054 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3909 nodes · 7609 edges · 228 communities (186 shown, 42 thin omitted)
- Extraction: 98% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 112 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `02742def`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- candidate_residuals
- ingest.py
- build_dataset.py
- render_clinical_form_panel
- schema.py
- Reference: verified template structure
- template_ingest.py
- test_docx_roundtrip.py
- test_app.py
- expand
- generate_document
- test_template_ingest.py
- Local clinical LLM fine-tune — design
- patients.py
- devDependencies
- rebuild
- BackendError
- test_train_and_grammar.py
- test_reasoning_strip.py
- fill_template
- test_desktop_packaging.py
- test_app_screens.py
- test_cloud_client.py
- Clinic reference library — design
- generation_status.py
- deidentify
- components.py
- compilerOptions
- test_generation.py
- deidentify.py
- write_approved
- test_patient_browser.py
- Architecture
- test_stress_corpus.py
- combine_sources
- fixture
- make_gap_probes
- CareScribe — design system
- make_icon.py
- expand_name_variants
- _RecordingBackend
- theme.py
- test_reference_library.py
- test_auth_forms.py
- test_buildinfo.py
- docx_redact.py
- test_highlight_review_component.py
- available_forms
- test_docx_revision_leak.py
- split_by_vignette
- Model Card for phi35-v1
- Installing CareScribe
- load_eval_items
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
- parametrize
- House-style exemplar retrieval — design
- clinical_forms.py
- load_settings
- test_crisis_lines_preserved.py
- Cloud generation transport (`CloudBackend`) — design
- app.py
- merge_and_convert.sh
- GLiNER Deliberately Uninstalled
- run_eval.py
- Sample Source Documents README
- Recurring fictional staff roster (e.g. A. Whitfield) across documents
- Lightweight review UX for de-identification — design
- test_deid_pipeline.py
- review_spans
- test_eld_vignettes_b.py
- Clinical fine-tune v2 — honest evaluation, corpus rebuild, patient roll-up
- Patient records store — design
- test_generator_backend.py
- NoEgress
- test_backend_overrides.py
- load_documents
- test_generation_setup.py
- CareScribe clinical drafting model — model card
- users.py
- test_patients_concurrent_sessions.py
- <id> — <title>
- cloud_client.py
- generate
- LLM backend flexibility + realistic test corpus + full-pipeline validation
- Path
- Per-field retrieval planner — design
- components/__init__.py
- pull_ollama_model
- is_up
- Evaluation report
- compilerOptions
- batch.py
- test_docx_letterhead_leak.py
- AGENTS.md — rules for automated coding agents in this repo
- Task board
- Global Constraints
- test_full_pipeline_accounts.py
- finetune/
- test_review_gate.py
- load_protected_terms
- exemplars.py
- test_patient_pipeline.py
- set_active_user
- finetune/__init__.py
- integrate/__init__.py
- carenotes.py
- test_clinical_forms_generate.py
- medgpt-finetune
- test_letterhead_address_leak.py
- test_download_model.py
- model_setup.py
- Defects this plan fixes
- create_user
- eval/__init__.py
- backends.py
- CareScribe site
- assemble/__init__.py
- test_run_eval_wiring.py
- build_messages
- tsconfig.json
- EncounterFacts
- Generation backend selection order (Ollama > built-in GGUF > Cloud)
- test_labelled_line_columns.py
- Document
- parse_fields
- applog.py
- test_cardio_vignettes_b.py
- render_generation_panel
- desktop.py
- mapping.py
- run_app.py
- extract_text
- test_sample_document_identifiers.py
- test_auth_gate.py
- residual_scan
- reference_library.py
- search
- make_pair
- Pinned Dependencies
- test_phone_number_leaks.py
- test_overlap.py
- Evaluation report
- test_relative_line_trailing.py
- test_ingest_read_and_encodings.py
- test_sample_document_labels.py
- test_docx_metadata_leak.py
- conftest.py
- is_model_present
- test_re_line_patient_name.py
- create_patient
- auth.py
- judge_draft
- test_date_of_death_leak.py
- test_dob_facility_mislabel.py
- test_hyphen_month_dates.py
- test_address_line_labels.py
- test_ihi_passport_leaks.py
- test_ollama_empty_response.py
- test_patient_line_trailing.py
- test_ingest_binary_txt.py
- deid
- query_tokens
- test_stress_corpus_rules_only.py
- ollama_client.py
- test_bracketed_identifier_value.py
- test_claim_number_label.py
- test_gp_vignettes_a.py
- FormType
- test_build_dataset_wiring.py
- get_form_spec
- pairs.py
- fixtures.py
- resolve_model_path
- _NullBackend
- test_eld_vignettes_a.py
- test_settings_panel_screen.py
- test_cmht_vignettes_a.py
- test_resp_vignettes_a.py
- test_a_batch_of_clean_documents_needs_roughly_one_click_each
- test_pipeline_opens_no_socket
- test_datagen_config_is_live.py
- test_cardio_vignettes_a.py
- core/__init__.py
- Evaluation report
- test_manifest_split_mode.py
- Path
- Path
- RuntimeError
- test_resp_vignettes_b.py
- fixture
- wipe_phi
- render_refinement
- write_review_record
- Path
- Path
- Protocol
- fixture
- Path
- Pattern
- RuntimeError
- parametrize
- Path
- RuntimeError
- AppTest

## God Nodes (most connected - your core abstractions)
1. `deidentify()` - 102 edges
2. `expand()` - 69 edges
3. `FormType` - 53 edges
4. `create_user()` - 52 edges
5. `EncounterFacts` - 48 edges
6. `get_form_spec()` - 47 edges
7. `create_patient()` - 43 edges
8. `set_active_user()` - 39 edges
9. `residual_scan()` - 39 edges
10. `extract_text()` - 39 edges

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

## Communities (228 total, 42 thin omitted)

### Community 0 - "candidate_residuals"
Cohesion: 0.12
Nodes (19): candidate_residuals(), Flag, _is_common(), outstanding(), _placeholder_ranges(), Residual-candidate highlighter — where the reviewer's eye should go first. This…, One span worth a second look, with its offsets in the redacted text., Identity for dismissal — per value, so one decision covers repeats. (+11 more)

### Community 1 - "ingest.py"
Cohesion: 0.17
Nodes (15): _block_text(), _extract_docx(), _extract_pdf(), _header_footer_parts(), IngestError, normalise_line_endings(), RuntimeError, Text extraction for uploaded documents (PDF / DOCX / TXT). Nothing here writes… (+7 more)

### Community 2 - "build_dataset.py"
Cohesion: 0.08
Nodes (42): build(), _fallback_inject(), _load_datagen_config(), main(), Path, End-to-end: sampled encounters -> validated SFT pairs + manifest. python -m…, Return ``{"pairs": [...], "kept": k, "dropped": d, "reasons": {...}}``.…, Fill ``[[TOKEN]]`` slots with simple fake values. Used only until… (+34 more)

### Community 3 - "render_clinical_form_panel"
Cohesion: 0.12
Nodes (17): _form_draft_key(), _form_draft_state(), _header_values_complete(), Shown instead of an empty panel when no model is available yet. An empty…, Option A. The only outbound request the app makes, on an explicit click., Option B. Ollama does the fetching; the request goes to loopback., Let a clinic add its own table-based .docx form to the selector. Parsing and…, render_clinical_form_panel() (+9 more)

### Community 4 - "schema.py"
Cohesion: 0.12
Nodes (27): Enum, Choice, Any, Random, Range, Small seeded-sampling primitives shared by the vignette sampler. A vignette is…, Pick one of ``options`` uniformly., Pick one of ``options`` by matching ``weights``. (+19 more)

### Community 5 - "Reference: verified template structure"
Cohesion: 0.11
Nodes (19): carescribe/core/clinical_forms.py (module), Refine prompt (clinical form, marker-preserving), Refine prompt (free-form draft revision), Clinical Form Generation (APS Templates) Implementation Plan, Global Constraints, Reference: verified template structure, Self-Review Notes (for the implementer), Task 10: End-to-end generation glue (`generate_form_document`, `refine_form_document`, `render_preview`) (+11 more)

### Community 6 - "template_ingest.py"
Cohesion: 0.12
Nodes (30): ClinicalFormError, RuntimeError, Raised when a clinical form can't be built or filled., slugify(), delete_template(), _find_grids(), _infer_header(), _is_blank_row() (+22 more)

### Community 7 - "test_docx_roundtrip.py"
Cohesion: 0.09
Nodes (32): approved_map(), document_has_text_boxes(), The reviewer-approved ``{literal: placeholder}`` map for the Word pass. This is…, True if a .docx holds text this redaction pass cannot reach., extract_text(), Flatten a docx to text (body + tables + headers/footers) for a residual scan., _build(), fixture (+24 more)

### Community 8 - "test_app.py"
Cohesion: 0.15
Nodes (32): AppTest, analysed_batch(), _clean_auto_doc(), data_editors(), loaded_batch(), UI checks for the batch review app via Streamlit's AppTest. No server of any…, After the read-and-confirmed tick, a clean auto-confidence document has nothing…, Generation must never run on text a human has not approved. (+24 more)

### Community 9 - "expand"
Cohesion: 0.07
Nodes (46): BaseModel, _blank_for(), expand(), Random, Turn vignettes into `EncounterFacts` instances with a seeded RNG. `expand`…, Yield ``n`` `EncounterFacts`, deterministic for a given ``seed``., Build one `EncounterFacts` from a vignette. With ``gap_probability`` > 0, each…, sample_encounters() (+38 more)

### Community 10 - "generate_document"
Cohesion: 0.09
Nodes (32): generate_document(), The shared preamble — role, anti-fabrication rules, placeholder rules., Stream a drafted document from approved de-identified text. ``phi_values`` is…, Revise an existing draft against a follow-up instruction. Operates on the same…, refine_document(), system_prompt(), A 2-char mapping value must not refuse a clean draft just because those…, The boundary check must not weaken a real leak: a short value standing alone as… (+24 more)

### Community 11 - "test_template_ingest.py"
Cohesion: 0.16
Nodes (18): fill_parsed_template(), parse_template_bytes(), Fill an in-memory copy of ``original_docx`` from ``spec``'s anchors. A thin…, _anchors(), _build_synthetic(), _merge_full_width(), fixture, parametrize (+10 more)

### Community 12 - "Local clinical LLM fine-tune — design"
Cohesion: 0.06
Nodes (30): 10. Workstream E — integration, 11. What needs a human / external resource, 12. Milestones (testable deliverables), 13. Testing strategy, 1. Goal, 2. Constraints inherited from CareScribe, 3. Approach (selected), 4. Base model (+22 more)

### Community 13 - "patients.py"
Cohesion: 0.17
Nodes (22): _clean_name(), delete_patient(), get_patient(), _now(), Patient, patient_dir(), PatientError, The per-patient records store. CareScribe's output has always been a flat… (+14 more)

### Community 14 - "devDependencies"
Cohesion: 0.06
Nodes (35): lucide-react, oxlint, react, react-dom, dependencies, lucide-react, react, react-dom (+27 more)

### Community 15 - "rebuild"
Cohesion: 0.09
Nodes (23): add_manual_entity(), DeidentificationError, DeidResult, Raised when de-identification can't run at all., Everything the de-identification stage produces for one document., Re-derive redacted text and the PHI map from a reviewer-edited table. Called…, Add an identifier the tools missed and immediately re-redact. The new value…, rebuild() (+15 more)

### Community 16 - "BackendError"
Cohesion: 0.18
Nodes (10): BackendError, LocalGGUFBackend, RuntimeError, True if the runtime and a model file are both present., Raised when a backend cannot be used, with the fix in the message., Shared message for a completion cut off by the token/context budget. A half-…, CPU-only generation from a bundled GGUF via ``llama-cpp-python``. The model is…, _truncation_error() (+2 more)

### Community 17 - "test_train_and_grammar.py"
Cohesion: 0.06
Nodes (52): _body_rules(), field_grammar(), _lit(), note_grammar(), _placeholder_rule(), GBNF grammars for constrained local decoding — a structural guarantee on top of…, A GBNF double-quoted literal., ``placeholder ::= "[" ( "PATIENT" | "DATE_1" | ... ) "]"`` or ``None``. (+44 more)

### Community 18 - "test_reasoning_strip.py"
Cohesion: 0.10
Nodes (29): _ends_mid_tag(), Remove a model's reasoning monologue from a finished draft. Idempotent. Text…, True if ``text`` ends part-way through what could be a reasoning tag., Filter a token stream so a reasoning prefix never reaches the consumer. Buffers…, strip_reasoning(), _without_reasoning(), _drain(), Generation must hand the clinician the finished document, not the model's… (+21 more)

### Community 19 - "fill_template"
Cohesion: 0.14
Nodes (22): _clear_cell(), _dedupe_row(), _fill_cell(), _fill_cell_after_label(), _fill_header_cell(), fill_template(), Remove every paragraph after the first, and every run in the first, leaving one…, Overwrite a dedicated value cell (label lives in a different cell). (+14 more)

### Community 20 - "test_desktop_packaging.py"
Cohesion: 0.08
Nodes (20): available_ram_gb(), ram_verdict(), Total system RAM in GB, or 0.0 if it cannot be determined., Whether this machine can run the bundled local model. Returns a verdict rather…, _cloud_off(), fixture, The packaging invariants: what the desktop app may and may not do. Packaging is…, No key may be committed, defaulted, or written anywhere. (+12 more)

### Community 21 - "test_app_screens.py"
Cohesion: 0.33
Nodes (14): _analysed(), _approved(), _loaded(), _md(), AppTest, Every screen renders without error through the pipeline, after the UI refresh.…, _run(), test_analysed_screen_shows_review_and_awaiting_review_chips() (+6 more)

### Community 22 - "test_cloud_client.py"
Cohesion: 0.15
Nodes (14): Stream a completion from the configured cloud provider, yielding text. Raises…, stream_generation(), _capture(), _clean_cloud_env(), _FakeResponse, fixture, The optional cloud generation transport — stdlib HTTP, two wire formats, key…, test_a_missing_key_raises_before_any_request() (+6 more)

### Community 23 - "Clinic reference library — design"
Cohesion: 0.17
Nodes (11): `app.py`, Architecture, Clinic reference library — design, Decision, Follow-ups (not blocking), New `core/reference_library.py`, Privacy / safety, Problem (+3 more)

### Community 24 - "generation_status.py"
Cohesion: 0.12
Nodes (20): _llama_runtime_available(), missing_reason(), Is generation usable right now, and if not, what should the user do? Kept…, One plain sentence on why generation is not available yet., Which generation backends are usable at this moment., Which backend would actually be used, matching the backend ladder., Status, test_ollama_running_but_empty_recommends_pulling() (+12 more)

### Community 25 - "deidentify"
Cohesion: 0.05
Nodes (66): deidentify(), Run the full local pipeline over one document. CPU-only and offline: no model…, _mrn_values(), parametrize, Regression suite for the five leaks found on a second, non-fixture document.…, The precision guard that keeps clinical context intact., A two-part capitalised phrase mid-document is not a letterhead., Layer 1 must carry this on its own — NER catching it is luck, not a guarantee. (+58 more)

### Community 26 - "components.py"
Cohesion: 0.10
Nodes (33): _model_card_dialog(), _model_card_path(), Name the generation model with a readable label; the card opens in a dialog…, _render_generation_model(), render_sidebar(), chip(), detection_layer(), empty_state() (+25 more)

### Community 27 - "compilerOptions"
Cohesion: 0.08
Nodes (23): DOM, src, vite/client, compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx (+15 more)

### Community 28 - "test_generation.py"
Cohesion: 0.07
Nodes (34): finalise(), Build the user prompt for one template with the source text embedded., Re-identify a draft locally and refuse to hand back a leaky document. Returns…, render_prompt(), check_placeholder_integrity(), Compare a draft's bracketed tokens against the placeholders it should use. An…, Local re-identification of a generated draft. Returns ``(text, unresolved)``.…, reidentify_document() (+26 more)

### Community 29 - "deidentify.py"
Cohesion: 0.04
Nodes (78): cache_resource, load_detection_engine(), Load the NER model once per session, not once per rerun. Streamlit re-runs the…, analyze(), _build_analyzer(), classify_person(), _collapse_facility_subsets(), _collapse_person_subsets() (+70 more)

### Community 30 - "write_approved"
Cohesion: 0.09
Nodes (32): list_folder(), Return the supported documents in ``folder``, sorted by name. Non-recursive on…, Findings from the safety sweep, minus the ones the reviewer has cleared. A…, Write approved de-identified text to the output folder. Re-runs the safety…, sweep(), write_approved(), parametrize, Batch loading and the approved-write path. The privacy invariant under test:… (+24 more)

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

### Community 35 - "fixture"
Cohesion: 0.40
Nodes (5): args(), fixture, _cloud_off(), _fresh_generation_status_cache(), generation_status() is now @st.cache_data(ttl=5) — a process-global cache keyed…

### Community 36 - "make_gap_probes"
Cohesion: 0.16
Nodes (23): confabulated(), confabulation_rate(), gapped_headings(), make_gap_probes(), _norm(), Fraction of probes that invented content. ``None`` when uncomputable., Compare headings without tripping on case or spacing., ``{normalised heading: body}`` for a bold-headed form. (+15 more)

### Community 37 - "CareScribe — design system"
Cohesion: 0.20
Nodes (9): Browser surfaces, CareScribe — design system, Components (`carescribe/ui/components.py`), Direction, Palette, Sidebar order, Space & shape, Type (+1 more)

### Community 38 - "make_icon.py"
Cohesion: 0.29
Nodes (12): Image, _load_font(), main(), Path, Generate CareScribe's placeholder icon. A real icon is a design job; this…, The first usable bold face, or ``None`` if none of them load., A rounded square with "CS" centred on it., macOS only. Silently skipped elsewhere — the .app is built on a Mac. (+4 more)

### Community 39 - "expand_name_variants"
Cohesion: 0.07
Nodes (30): _collapse_person_identities(), True for a person row whose role is known (patient / relative / clinician)., Collapse every written form of one person onto a single entity row.…, REDACT_INPROSE_DATES flag, _specific_person_type(), canonical_person_key(), expand_name_variants(), expand_org_variants (Layer 4 — variant expansion) (+22 more)

### Community 41 - "theme.py"
Cohesion: 0.15
Nodes (11): _font_css(), highlight_review(), Click-to-redact highlighted text. Renders already-redacted (or already-flagged)…, The bundled `@font-face` rules, or "" if the faces are unavailable., Render ``html`` and return the ``data-span-id`` of the last click. Returns…, CareScribe UI layer — the visual identity, applied over Streamlit. `theme.CSS`…, _font_face_css(), inject() (+3 more)

### Community 42 - "test_reference_library.py"
Cohesion: 0.15
Nodes (19): add_file(), is_empty(), ``(filename, paragraph_count)`` per loaded reference file., Store an uploaded reference file. Returns the stored filename., sources(), _library(), fixture, Clinic reference library: paragraph chunking with heading tracking, BM25… (+11 more)

### Community 43 - "test_auth_forms.py"
Cohesion: 0.11
Nodes (27): normalise_username(), password_confirmation_error(), password_error(), Collapse internal whitespace and strip the ends. Never raises., ``None`` if the username is acceptable, else why not., ``None`` if the password is acceptable, else why not. Length is the only rule.…, ``None`` if the two match, else why not., Every problem at once. An empty dict means the form is submittable. (+19 more)

### Community 44 - "test_buildinfo.py"
Cohesion: 0.24
Nodes (10): build_info(), Build information for CareScribe., Return standard HTTP User-Agent string., Return application identity and version., user_agent(), Tests for buildinfo module., Test that user_agent returns correct format., Test that build_info returns correct name and version. (+2 more)

### Community 45 - "docx_redact.py"
Cohesion: 0.16
Nodes (17): apply_redactions(), _delete_prefix(), has_unreachable_text(), _iter_groups(), _iter_paragraphs(), _norm(), Structure-preserving .docx redaction. apply_redactions(path_in, path_out,…, Redact a literal split across a paragraph boundary (wrapped name). (+9 more)

### Community 46 - "test_highlight_review_component.py"
Cohesion: 0.09
Nodes (19): html(), fixture, Contract of the click-to-redact review component. This is the reviewer's…, The host silently drops postMessages without this flag., A CDN here would breach the offline guarantee as surely as in the theme., They were click-only: no tabindex, no role, no key handler., 360px hid most of a real letter behind a scroll with no way to search., A vh unit here feeds back into the height the host derives from it. The host… (+11 more)

### Community 47 - "available_forms"
Cohesion: 0.20
Nodes (10): available_forms(), (form_id, title) pairs — bundled forms first, then clinic-uploaded ones., skipif, test_no_field_key_collides_within_a_spec(), parametrize, Deterministic stand-in for a real generation backend., _StubBackend, test_combined_sources_generate_every_form_type_with_a_stub_backend() (+2 more)

### Community 48 - "test_docx_revision_leak.py"
Cohesion: 0.19
Nodes (18): _document(), Regression: text deleted with track changes on rode out in the approved file.…, Why the sweep has to be what catches it: nothing else can see it., Before the fix this wrote a file with the deleted name still inside it., w:author carries a clinician's name in an attribute, not a text node., Comments are a separate part of the package that no other pass loads., A deletion is not itself a finding -- only an identifier inside one is., A .docx whose body is ordinary and whose revision history is not. (+10 more)

### Community 49 - "split_by_vignette"
Cohesion: 0.26
Nodes (14): Split so that no vignette skeleton appears in more than one split. Row-level…, split_by_vignette(), _ids(), _pairs(), Holdout is by vignette: a skeleton in test is absent from train., With 2 vignettes there is no honest holdout. Say so, don't return {}., This task adds a splitter; it does not replace the old one., test_a_pair_without_a_vignette_id_is_rejected() (+6 more)

### Community 50 - "Model Card for phi35-v1"
Cohesion: 0.33
Nodes (5): Citations, Framework versions, Model Card for phi35-v1, Quick start, Training procedure

### Community 51 - "Installing CareScribe"
Cohesion: 0.22
Nodes (8): Before you start, First launch, If it will not start, Installing CareScribe, macOS, Updating, Where your files go, Windows

### Community 52 - "load_eval_items"
Cohesion: 0.29
Nodes (12): load_eval_items(), Rebuild eval items from a committed split file. Evaluation must read the split…, Eval reads the committed held-out split; it does not re-sample., An old jsonl lacks document/facts. Fail, don't silently eval on nothing., test_a_pair_written_before_task_079_is_rejected_loudly(), test_blank_lines_are_skipped(), test_one_item_is_rebuilt_from_the_file(), test_the_document_and_form_survive() (+4 more)

### Community 53 - "Clinic-uploaded clinical form templates — design"
Cohesion: 0.18
Nodes (10): Architecture, Clinic-uploaded clinical form templates — design, Follow-ups (not blocking), New module `core/template_ingest.py`, Persistence, Problem, Registry integration (`core/clinical_forms.py`), Scope (+2 more)

### Community 54 - "[Unreleased]"
Cohesion: 0.22
Nodes (8): [0.1.0] - 2026-09-01, Added, Added, Added, Changelog, Fixed, Fixed, [Unreleased]

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
Cohesion: 0.08
Nodes (49): Document, document_from_deidentified(), A :class:`Document` standing for text de-identified in an earlier session. This…, One document's state for the whole review pass. Everything here except…, build_case_conference_note(), build_discharge_summary(), build_gp_progress_note(), build_imaging_report() (+41 more)

### Community 64 - "test_clinical_form_templates.py"
Cohesion: 0.50
Nodes (3): parametrize, The three bundled APS templates load and match the structure this feature's…, test_bundled_template_shape()

### Community 74 - "House-style exemplar retrieval — design"
Cohesion: 0.18
Nodes (10): `app.py`, Architecture, `core/clinical_forms.py`, Follow-ups (not blocking), House-style exemplar retrieval — design, New module `core/exemplars.py`, Privacy, Problem (+2 more)

### Community 76 - "clinical_forms.py"
Cohesion: 0.20
Nodes (19): _biopsychosocial_spec(), build_prompt(), _form_grammar(), FormField, FormSpec, generate_form_document(), _grid_fields(), HeaderField (+11 more)

### Community 77 - "load_settings"
Cohesion: 0.25
Nodes (15): load_settings(), _path(), Persisted app settings — which generation backend/model/temperature to use.…, Read persisted settings. A missing or unreadable file yields defaults., Persist non-secret settings, creating the app data dir if needed., save_settings(), Settings, test_load_settings_coerces_stringy_temperature() (+7 more)

### Community 78 - "test_crisis_lines_preserved.py"
Cohesion: 0.33
Nodes (6): parametrize, Regression: public crisis-line names are not identifiers and must not be…, The allow-list entry is the helpline name only — a real name beside it still…, test_a_crisis_line_name_survives_deidentification(), test_a_person_named_near_a_crisis_line_is_still_redacted(), test_crisis_line_name_and_number_both_survive_in_context()

### Community 80 - "Cloud generation transport (`CloudBackend`) — design"
Cohesion: 0.20
Nodes (9): Architecture, Cloud generation transport (`CloudBackend`) — design, `core/backends.py`, Follow-ups (not blocking), New module `core/cloud_client.py`, Privacy properties (unchanged, inherited), Problem, Scope (+1 more)

### Community 81 - "app.py"
Cohesion: 0.12
Nodes (28): current(), _document_bytes(), documents(), ensure_engine_ready(), ingest_sources(), main(), _pipeline_step(), _privacy_state() (+20 more)

### Community 84 - "run_eval.py"
Cohesion: 0.05
Nodes (62): DraftScore, aggregate(), DraftScore, The four target metrics, scored per draft and reducible to a mean. Format,…, Mean of each metric over ``scores``., score_draft(), A regression set built from the repo's own corpus, not synthetic data.…, regressed() (+54 more)

### Community 87 - "Lightweight review UX for de-identification — design"
Cohesion: 0.14
Nodes (13): 1. Confidence tiering (drives what gets a click at all), 2. One primary review view, not three, 3. The click-to-redact component, 4. Attestation & audit trail, 5. Crash-risk fixes, Architecture, Current state (for reference), Goals (+5 more)

### Community 88 - "test_deid_pipeline.py"
Cohesion: 0.04
Nodes (46): parametrize, Regression suite for the layered de-identification pipeline. Two guarantees,…, With REDACT_INPROSE_DATES False, a procedure date is clinical, not identity., DOB and admission/discharge dates carry identity, so they go., spaCy labels "ECG" and "NSTEMI" as organisations; the filter must drop them., Layer 1 alone must still catch every purely structured identifier., A bare digit run is a lab value; only a labelled one is a record number., The layer that exists specifically to catch an unlabelled name in prose. (+38 more)

### Community 89 - "review_spans"
Cohesion: 0.32
Nodes (12): Every clickable span in ``redacted_text``, in reading order. ``confirmed`` is…, review_spans(), _entity(), action=Keep means the reviewer already decided — nothing to click on the…, test_a_confirmed_entity_produces_no_span(), test_a_kept_entity_produces_no_entity_span(), test_auto_confidence_entities_produce_no_span(), test_dismissed_residual_flags_are_excluded() (+4 more)

### Community 90 - "test_eld_vignettes_b.py"
Cohesion: 0.36
Nodes (7): parametrize, The two elderly care skeletons added by task 098 sample cleanly., test_every_gappable_field_can_be_blanked(), test_expands_without_gaps(), test_gappable_names_real_fields(), test_target_validates_for_every_form(), _vignette()

### Community 91 - "Clinical fine-tune v2 — honest evaluation, corpus rebuild, patient roll-up"
Cohesion: 0.07
Nodes (28): 10. Milestones, 1. Why there is a v2, 2. The placeholder-namespace problem, and the chosen resolution, 3.1 Hold out vignettes, not rows, 3.2 Report contamination rather than assuming its absence, 3.3 Break self-marking on faithfulness, 3.4 Delete `style_match`; re-earn it later, 3.5 Adversarial gap probe as a first-class metric (+20 more)

### Community 92 - "Patient records store — design"
Cohesion: 0.11
Nodes (17): 10. Rejected alternatives, 1. Goal, 2. Constraints inherited from CareScribe, 3. The one deliberate change to the privacy posture, 4. Storage layout, 5.1 `carescribe/core/desktop.py`, 5.2 `carescribe/core/patients.py` (new), 5.3 `carescribe/core/batch.py` (+9 more)

### Community 93 - "test_generator_backend.py"
Cohesion: 0.11
Nodes (19): GeneratorBackend, get_backend(), OllamaBackend, OpenAICompatibleBackend, TemplateBackend, Test that TemplateBackend properly renders facts in proforma style, Test that TemplateBackend properly renders facts in prose style, Test that TemplateBackend is deterministic - same input gives same output (+11 more)

### Community 94 - "NoEgress"
Cohesion: 0.14
Nodes (10): NoEgress, Fails the test if anything opens a non-loopback socket. Loopback is allowed:…, Re-identification is pure Python — it must not phone anywhere., test_reidentification_opens_no_socket(), The load that used to hang on a captive portal must not exist., Reset the cache so the guard covers a genuine first load., The reported hang: no model, so something tries to download it., test_a_missing_model_fails_loudly_instead_of_fetching() (+2 more)

### Community 95 - "test_backend_overrides.py"
Cohesion: 0.10
Nodes (25): Pick a backend. Returns ``(kind, backend, label)``. ``prefer`` lets the UI…, select_backend(), OllamaBackend, Local generation through the loopback-pinned Ollama daemon., _backend_with_fake_model(), _FakeModel, _raising_stream(), The happy path must keep working: finish_reason 'stop' yields the text with no… (+17 more)

### Community 96 - "load_documents"
Cohesion: 0.12
Nodes (20): analyze_document(), load_documents(), Extract text from uploads or paths. Returns ``(documents, errors)``. One…, Run the de-identification layers over one document, in place., FakeUpload, Stands in for a Streamlit UploadedFile., test_analyze_document_populates_state(), test_duplicate_filenames_are_reported() (+12 more)

### Community 97 - "test_generation_setup.py"
Cohesion: 0.06
Nodes (35): cache_data, generation_status(), Inspect what is available, cached for 5 seconds. Called unconditionally on…, _imported_names(), mapping_module(), _nothing_available(), First-run generation setup: never an empty panel, and the egress line held. The…, A second call within the TTL must not re-probe Ollama. (+27 more)

### Community 98 - "CareScribe clinical drafting model — model card"
Cohesion: 0.40
Nodes (4): CareScribe clinical drafting model — model card, Evaluation, Known limitations, Training data

### Community 99 - "users.py"
Cohesion: 0.11
Nodes (34): any_users(), _as_user(), change_password(), _check_password(), _clean_username(), _derive(), get_user(), _now() (+26 more)

### Community 100 - "test_patients_concurrent_sessions.py"
Cohesion: 0.14
Nodes (16): active_user(), _get_active_user(), The account the store is currently scoped to, or ``None``. Per session-thread:…, fixture, Two signed-in sessions must not see each other's account. Streamlit serves…, A thread that never signed in gets the flat pre-accounts layout., Run `body(user_id)` on two threads, interleaved at a barrier., Each session must read back the account it set, not the other one. (+8 more)

### Community 101 - "<id> — <title>"
Cohesion: 0.29
Nodes (6): Acceptance criteria, Do NOT touch, Files in scope, Goal, <id> — <title>, Notes

### Community 102 - "cloud_client.py"
Cohesion: 0.27
Nodes (11): CloudError, _config(), _post(), RuntimeError, Transport for the optional cloud generation backend. Reached only when a…, Yield the payload of each ``data:`` line in an SSE stream., A recoverable problem talking to the configured cloud provider., Return ``(api_key, base_url, model)`` from the environment, or raise. (+3 more)

### Community 103 - "generate"
Cohesion: 0.16
Nodes (19): generate(), Stream a completion from the local model, yielding text chunks. Low temperature…, FakeResponse, ndjson(), fixture, Tests for ollama_client.generate() — the streaming parser and its error paths., Daemon up with one model installed; records what generate() sends., The path the app actually uses: streaming, done, no tokens. Only an explicit… (+11 more)

### Community 104 - "LLM backend flexibility + realistic test corpus + full-pipeline validation"
Cohesion: 0.20
Nodes (9): A. Backend/settings flexibility, B. Realistic document corpus, C. Full-pipeline validation loop, Design, Goals, LLM backend flexibility + realistic test corpus + full-pipeline validation, Non-goals, Problem (+1 more)

### Community 105 - "Path"
Cohesion: 0.20
Nodes (15): _default_output_dir(), The raw bytes behind an upload or a path, without copying it to disk., Where approved output lands. In a source checkout that is…, _source_bytes(), bundled_app_py(), bundled_fonts(), _default_dist(), find_executable() (+7 more)

### Community 106 - "Per-field retrieval planner — design"
Cohesion: 0.17
Nodes (11): `app.py`, Architecture, `core/reference_library.py`, `core/retrieval_planner.py` (new), `core/text_search.py`, Decision, Follow-ups (not blocking), Per-field retrieval planner — design (+3 more)

### Community 108 - "pull_ollama_model"
Cohesion: 0.13
Nodes (23): Progress, pull_ollama_model(), Ask the local Ollama daemon to pull a model, yielding progress. The request…, One step of a download, for a progress bar., object, FakeResponse, ndjson(), Tests for model_setup.pull_ollama_model() — the streaming pull generator.… (+15 more)

### Community 109 - "is_up"
Cohesion: 0.11
Nodes (18): is_up(), list_models(), Open a request against the pinned loopback base URL., True if the local Ollama daemon answers. Never raises., Locally-installed model names, sorted. Empty list if the daemon is down., _request(), FakeResponse, fixture (+10 more)

### Community 111 - "compilerOptions"
Cohesion: 0.10
Nodes (19): node, vite.config.ts, compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection (+11 more)

### Community 112 - "batch.py"
Cohesion: 0.11
Nodes (30): approved_docx_path(), approved_path(), BatchError, _blanked_properties(), _document_property_text(), Batch input and approved-output handling. The module that writes **document-…, Reduce a filename to a safe output stem — no paths, no surprises., The folder a write lands in — an explicit override, or the default.… (+22 more)

### Community 113 - "test_docx_letterhead_leak.py"
Cohesion: 0.17
Nodes (22): _detected(), _document(), parametrize, A .docx letterhead, and a text box: what is redacted and what is refused.…, None of these was extracted at all before the header/footer read., The whole point: a letterhead is redacted, not a document you cannot use., python-docx's paragraph walk does not descend into a w:txbxContent., Before the fix this call succeeded and wrote the box's contents to disk. (+14 more)

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
Nodes (39): _approve_document(), _every_file(), Filed, AppTest, fixture, Path, The whole pipeline, end to end, through accounts.…, Two accounts sign up, each files documents under their own patient. (+31 more)

### Community 118 - "finetune/"
Cohesion: 0.40
Nodes (4): Environment, finetune/, Layout, Milestones

### Community 119 - "test_review_gate.py"
Cohesion: 0.08
Nodes (28): blocking_reason(), The approval gate. Only the **authoritative safety sweep** blocks approval. A…, Why Approve is disabled, in one short line. Empty string means it isn't.…, _flag_values(), fixture, parametrize, The reviewer gate: candidate highlighting, the adaptive checklist, and the no-…, Low-confidence redactions are already in place; the permissive flags are… (+20 more)

### Community 120 - "load_protected_terms"
Cohesion: 0.29
Nodes (7): _build_protected_pattern(), load_protected_terms(), Read the editable allow-list. Blank lines and ``#`` comments are ignored., Re-read the allow-list from disk (the file is meant to be edited by hand)., reload_protected_terms(), Pattern, test_the_allow_list_is_an_editable_file()

### Community 121 - "exemplars.py"
Cohesion: 0.14
Nodes (25): add_exemplar(), count(), _dir(), _load(), _path(), Path, House-style exemplar retrieval for clinical-form generation. A clinic…, Top-``k`` stored values for ``field_key``, ranked by BM25 against ``query``. (+17 more)

### Community 122 - "test_patient_pipeline.py"
Cohesion: 0.14
Nodes (27): filed_documents(), Approved artefacts filed for this patient, newest first., _approve_document(), filed(), FiledCase, fixture, parametrize, Path (+19 more)

### Community 123 - "set_active_user"
Cohesion: 0.11
Nodes (36): list_patients(), migrate_unscoped_into(), patients_root(), Root of the records store, before any per-account scoping.…, Scope every subsequent store call to one account, or to none. Passing ``None``…, Where the *current account's* patients live. With no active user this is…, Every readable patient, sorted by name (case-insensitive) then id. A folder…, Patient folders sitting in the base, from before accounts existed. These are… (+28 more)

### Community 126 - "carenotes.py"
Cohesion: 0.07
Nodes (35): assert_deidentified(), assert_no_residual_identifiers(), Backend, CareNoteError, CloudBackend (unwired seam), generate_care_note(), load_prompt(), Protocol (+27 more)

### Community 127 - "test_clinical_forms_generate.py"
Cohesion: 0.23
Nodes (9): Human-readable rendering for display only — the marker text in ``draft_state``…, render_preview(), Captures exactly what generation handed the model — mirrors the fixture in…, RecordingBackend, test_generate_form_document_refuses_a_real_identifier(), test_generate_form_document_sends_the_field_marker_prompt(), test_refine_form_document_preserves_markers_instruction(), test_render_preview_defaults_missing_value() (+1 more)

### Community 131 - "test_letterhead_address_leak.py"
Cohesion: 0.31
Nodes (8): _letterhead_line(), parametrize, Regression: an unlabelled letterhead street address leaks in the clear. Found…, The de-identified form of the address/phone letterhead line., The new letterhead rule must not fire on a street word in a sentence., test_a_letterhead_street_address_line_is_taken_whole(), test_street_words_in_prose_are_not_over_redacted(), test_the_sample_letterhead_address_is_fully_redacted()

### Community 132 - "test_download_model.py"
Cohesion: 0.11
Nodes (21): FakeResponse, _partial_path(), fixture, Tests for model_setup.download_model — the app's one non-loopback socket., A 403 and an unreachable server both surface as ModelSetupError., With no room, the download fails before a socket is ever opened., Models dir in tmp_path, with a size floor tests can actually reach., urlopen's return: a context manager with headers and a status. (+13 more)

### Community 133 - "model_setup.py"
Cohesion: 0.08
Nodes (38): clear_partial_download(), download_model(), _free_bytes(), model_destination(), ModelSetupError, Path, RuntimeError, The one outbound request CareScribe makes — fetching the model, on request.… (+30 more)

### Community 134 - "Defects this plan fixes"
Cohesion: 0.14
Nodes (13): Clinical fine-tune v2 — V1 honest evaluation harness, Defects this plan fixes, Global Constraints, Self-review, Task 1: Thread `vignette_id` through to pair metadata, Task 2: Persist what evaluation needs to reconstruct an item, Task 3: Split by vignette, not by row (fixes D1), Task 4: Evaluate the committed held-out split (fixes D4) (+5 more)

### Community 135 - "create_user"
Cohesion: 0.10
Nodes (40): authenticate(), create_user(), list_users(), Create an account. Raises :class:`UserError` if it cannot., The account for these credentials, or ``None``. One return value for every…, Every readable account, sorted by username (case-insensitive) then id., fixture, parametrize (+32 more)

### Community 137 - "backends.py"
Cohesion: 0.13
Nodes (20): privacy_indicator(), A persistent, honest statement of where data goes. It must change when cloud…, cloud_enabled(), cloud_key_present(), cloud_provider(), CloudBackend, describe_backends(), Generation backends, layered so the app works with nothing installed. Selection… (+12 more)

### Community 138 - "CareScribe site"
Cohesion: 0.50
Nodes (3): CareScribe site, Local, Notes

### Community 140 - "test_run_eval_wiring.py"
Cohesion: 0.24
Nodes (15): _confabulation_for(), _overlap_for(), Nearest-train-neighbour similarity for the evaluated targets. Reported so a…, Confabulation rate on adversarial "Not documented." probes., _args(), main() reads the held-out split, and reports overlap and confabulation., A resampled set has no committed train split to compare against., Writing "Not documented." never confabulates; inventing content does. Both… (+7 more)

### Community 141 - "build_messages"
Cohesion: 0.16
Nodes (16): build_messages(), Care note templates. Every template shares the same hard rule: the input is…, Return ``(system, user)`` for a template label and de-identified document., build_messages(), default_instruction(), The prompt construction shared by training and production. Training pairs MUST…, The system string for a form type., The instruction line paired with a form type when none is supplied. (+8 more)

### Community 143 - "EncounterFacts"
Cohesion: 0.17
Nodes (20): field_validator, _care_plan(), _field_content(), _handover(), _history_lines(), _med_line(), _objective_lines(), _plan_lines() (+12 more)

### Community 145 - "Generation backend selection order (Ollama > built-in GGUF > Cloud)"
Cohesion: 0.18
Nodes (11): core/model_setup.py (model download, isolated), packaging/build_macos.sh, packaging/build_windows.ps1, packaging/carescribe.iss (Inno Setup script), packaging/make_icon.py, The desktop app (PyInstaller packaging), Generation backend selection order (Ollama > built-in GGUF > Cloud), run_app.py entry point (+3 more)

### Community 146 - "test_labelled_line_columns.py"
Cohesion: 0.09
Nodes (30): parametrize, Labelled name fields separated from the next field by whitespace only. `Name:…, Four tokens is the cap `_trim_span` also enforces. Past it, take none.…, What real forms put in an identity field when there is no name. None of these…, `mapping.redact` replaces every occurrence of a matched value. So redacting…, A bare `Name` label is only safe because it is line-anchored., De-identify with the analyzer forced off., The DOB was never the problem — check the fix did not cost it. (+22 more)

### Community 147 - "Document"
Cohesion: 0.11
Nodes (34): active_output_dir(), active_patient_id(), document_flags(), entity_confirmed(), entity_frame(), flag_dismissals(), One click to approve every document that comes back clean. Each is re-run…, The selected patient's id, or "" for scratch mode. (+26 more)

### Community 148 - "parse_fields"
Cohesion: 0.44
Nodes (9): parse_fields(), Turn the model's marker-delimited output into ``{field_key: text}``. Any field…, _spec(), test_parse_fields_defaults_missing_field_to_not_documented(), test_parse_fields_first_occurrence_wins_on_duplicate_marker(), test_parse_fields_handles_empty_output(), test_parse_fields_happy_path(), test_parse_fields_ignores_unknown_marker_without_raising() (+1 more)

### Community 149 - "applog.py"
Cohesion: 0.11
Nodes (33): BaseException, The last line of defence: a calm message instead of a stack trace. A clinician…, render_unexpected_error(), exception(), get_logger(), log(), log_path(), Path (+25 more)

### Community 150 - "test_cardio_vignettes_b.py"
Cohesion: 0.36
Nodes (7): parametrize, The two cardiology skeletons added by task 095 sample cleanly., test_every_gappable_field_can_be_blanked(), test_expands_without_gaps(), test_gappable_names_real_fields(), test_target_validates_for_every_form(), _vignette()

### Community 151 - "render_generation_panel"
Cohesion: 0.17
Nodes (13): _as_docx(), _draft_state(), Which backend will be used, and the fix if none is available., A concrete "it works", rather than asking the clinician to trust a flag., Generate, refine, re-identify and export — for one approved document. Two…, The de-identified draft, refinement, re-identification, and exports., Opt-in, local-only substitution of placeholders back to real values., Render generated text to a .docx in memory — nothing touches disk. (+5 more)

### Community 152 - "desktop.py"
Cohesion: 0.11
Nodes (33): app_data_dir(), bundle_root(), ensure_dirs(), find_local_model(), is_frozen(), _model_search_dirs(), models_dir(), output_dir() (+25 more)

### Community 153 - "mapping.py"
Cohesion: 0.04
Nodes (66): assign_placeholders(), dedupe_entities(), _edit_distance(), expand_facility_variants(), find_known_as(), find_spans(), _form_pattern(), Issue (+58 more)

### Community 154 - "run_app.py"
Cohesion: 0.20
Nodes (13): close_splash(), _fatal(), free_port(), main(), _no_window_kwargs(), CareScribe desktop launcher — the app's entry point. Starts the Streamlit…, Poll the loopback port until Streamlit answers., Dismiss the bootloader splash, if this is a frozen build that has one.… (+5 more)

### Community 155 - "extract_text"
Cohesion: 0.25
Nodes (14): extract_text(), Extract plain text from an uploaded pdf/docx/txt file. Raises…, FakeUpload, parametrize, Document ingestion checks. No network, no temp copies of PHI., A Windows-authored .txt file must not leak its raw \\r into the pipeline. De-…, test_reads_a_file_path(), test_reads_the_encodings_clinical_exports_use() (+6 more)

### Community 156 - "test_sample_document_identifiers.py"
Cohesion: 0.43
Nodes (7): parametrize, Answer-key regression net for ``sample_documents/``. Unlike ``stress_corpus/``…, Whitfield" on its own (not just the full name) must not survive anywhere., _redacted(), test_patient_identifier_is_absent_from_redacted_text(), test_sample_document_residual_scan_is_clean(), test_the_patient_surname_alone_is_also_gone()

### Community 157 - "test_auth_gate.py"
Cohesion: 0.20
Nodes (21): isolated_store(), AppTest, fixture, The sign-in gate, end to end through the real app. Two things are being pinned…, Accounts and patients both land in tmp, never in the checkout., Everything the screen said, for coarse assertions., run(), test_a_new_account_sees_none_of_another_accounts_patients() (+13 more)

### Community 158 - "residual_scan"
Cohesion: 0.08
Nodes (32): Re-scan ALREADY-REDACTED text for anything that still looks identifying. Runs…, residual_scan(), main(), normalise(), Per-document pass/fail report for the stress corpus. python…, Placeholders are the point of the exercise, not leaks., A .txt file read off a Windows disk arrives with CRLF endings. NER tokenises…, test_crlf_and_lf_documents_behave_identically() (+24 more)

### Community 159 - "reference_library.py"
Cohesion: 0.22
Nodes (14): Add clinic reference files (formulary, pathways, protocols) to a local library.…, _render_reference_uploader(), _all_chunks(), _bounded(), Chunk, _dir(), _files(), _paragraphs() (+6 more)

### Community 160 - "search"
Cohesion: 0.15
Nodes (12): ExemplarError, RuntimeError, Raised when an exemplar cannot be stored — e.g. it still holds an identifier., RuntimeError, Top-``k`` reference passages for ``query`` at ``granularity``. BM25, ``score >…, Raised when a reference file cannot be stored., ReferenceError, ReferenceHit (+4 more)

### Community 161 - "make_pair"
Cohesion: 0.17
Nodes (20): make_pair(), _flatten_strings(), _numbers_in_facts(), _made(), A written pair must carry enough to rebuild an eval item from disk., test_earlier_meta_keys_are_untouched(), test_facts_survive_a_json_round_trip(), test_meta_carries_the_known_placeholders() (+12 more)

### Community 162 - "Pinned Dependencies"
Cohesion: 0.25
Nodes (8): pandas, pdfplumber, Pinned Dependencies, presidio-analyzer, python-docx, spaCy, spaCy Model Fallback Chain, streamlit

### Community 163 - "test_phone_number_leaks.py"
Cohesion: 0.14
Nodes (20): deid_rules_only(), Lab values, doses and dates are not phone numbers and pass through. "Seen on"…, +61 with spaced groups is caught, digits fully gone., +44 with spaced groups is caught, digits fully gone., A +61 number with no spaces is caught., A bracketed "(03)" area code is caught with its brackets., A two-digit area code with no brackets is caught., De-identify with no NER model — the supported no-spaCy machine. (+12 more)

### Community 164 - "test_overlap.py"
Cohesion: 0.17
Nodes (18): _grams(), max_similarity(), overlap_report(), Train/test contamination, measured rather than assumed. A held-out score means…, Jaccard over character 5-grams, 0..1., Similarity between ``text`` and its nearest neighbour in ``corpus``., Distribution of each test target's nearest-train-neighbour similarity. Returns…, similarity() (+10 more)

### Community 165 - "Evaluation report"
Cohesion: 0.50
Nodes (3): Confabulation (adversarial gap probes), Evaluation report, Train/test overlap

### Community 166 - "test_relative_line_trailing.py"
Cohesion: 0.14
Nodes (19): deid_rules_only(), RELATIVE_LINE must keep matching when a relationship, phone or age follows the…, De-identify with no NER model -- the supported no-spaCy machine., Lines that are not a labelled field naming a person pass through unchanged., This exact line appears in sample_documents/01_gp_referral_letter.docx and the…, The strengths-based phrasing names the same spouse with the same trailing…, A NOK line with a bracketed relationship still redacts the name., An emergency contact followed by a phone number (ASCII hyphen) still redacts. (+11 more)

### Community 167 - "test_ingest_read_and_encodings.py"
Cohesion: 0.13
Nodes (14): _extract_txt(), Any, Plain text, trying the encodings clinical exports actually use., Normalise a Streamlit UploadedFile (or a path string) to (name, bytes)., _read_bytes(), Ingest file-object handling, text encodings and line endings., A half-consumed stream must be rewound, or the document is silently truncated., ReadOnly (+6 more)

### Community 168 - "test_sample_document_labels.py"
Cohesion: 0.14
Nodes (19): deid_rules_only(), Regression tests for the sample-document field labels. Four different labels…, De-identify with no NER model — the supported no-spaCy machine., Worker:' names the injured person on a WorkCover certificate., Full name:' is the intake-form spelling of the patient field., A line-leading bare 'Name:' is a clinic letter's patient field., Claim number:' is the insurer's case identifier for the patient., Claim No:' is the abbreviated spelling of the same field. (+11 more)

### Community 169 - "test_docx_metadata_leak.py"
Cohesion: 0.20
Nodes (18): _document(), parametrize, Regression: the patient's name rode out in the .docx document properties. Word…, A note's authoring time is the same class of fact as a service date., The field list is a list, so it must not be the only thing standing here. With…, Only the two property parts are rewritten; everything else is copied., A .docx whose body is already clean and whose properties are not., Each of these used to ride out verbatim in the written .docx. (+10 more)

### Community 170 - "conftest.py"
Cohesion: 0.25
Nodes (10): deid(), ner_available(), fixture, Shared pytest fixtures. The spaCy model load costs several seconds, so the…, No test may inherit the account another one left scoped. The active account is…, The full pipeline's output for the fixture document., True when a spaCy model loaded — layer 2 tests skip without one., raw_text() (+2 more)

### Community 171 - "is_model_present"
Cohesion: 0.50
Nodes (4): is_model_present(), True if a usable model file is already on this computer. This is the marker…, Setup is one-time because the file itself is the state., test_model_presence_is_the_persisted_marker()

### Community 172 - "test_re_line_patient_name.py"
Cohesion: 0.15
Nodes (18): deid_rules_only(), Subject-line "Re:" values pass through unchanged., Re: Mr Jonathan Blake" redacts the name., Re: Jonathan Blake" with no title still redacts the name., The corpus line "RE: Ngozi Okafor" redacts the name., An apostrophe surname, "O'Brien", is redacted., A hyphenated forename, "Jean-Luc Bonnet", is redacted., Patient:" and "Client name:" lines keep redacting. (+10 more)

### Community 173 - "create_patient"
Cohesion: 0.13
Nodes (27): create_patient(), patient_output_dir(), Where this patient's approved de-identified artefacts are filed., Create a patient folder and roster entry. Returns the new record., test_filed_documents_are_scoped(), fixture, parametrize, The per-patient records store. `patients.py` owns no detection logic — it is… (+19 more)

### Community 174 - "auth.py"
Cohesion: 0.20
Nodes (16): apply_scope(), current_user_id(), _honesty_caption(), is_signed_in(), The sign-in gate, and the account panel in the sidebar. CareScribe now opens on…, Leave the account, and take every trace of the session's work with it. ``wipe``…, Re-assert the store scope for this rerun. ``patients`` keeps the active account…, Show the sign-in screen. ``True`` when the app may carry on. Called before… (+8 more)

### Community 175 - "judge_draft"
Cohesion: 0.17
Nodes (17): judge_draft(), JudgeVerdict, OllamaJudge, A second, independent grader for faithfulness. `assemble.validators` scores a…, Grade ``draft`` against ``source``. ``complete(system, user) -> str``., The default grader: a larger, different model on the local daemon., _canned(), The judge grades against the source note, never against EncounterFacts. (+9 more)

### Community 176 - "test_date_of_death_leak.py"
Cohesion: 0.17
Nodes (16): deid_rules_only(), Date of death' is an anchored date and must be redacted, not leaked., DOD:' is a death-of-date anchor and must not leave the date standing., Deceased:' is a death anchor and must not leave the date standing., died on' anchors the date that follows it as identity., D.O.D / D.O.B collision guard: 'DOB:' still yields [DOB], never [DATE]., Date of admission' was already anchored; this must be unchanged., Death labels without a date leave ordinary clinical prose untouched. (+8 more)

### Community 177 - "test_dob_facility_mislabel.py"
Cohesion: 0.14
Nodes (16): parametrize, Regression: a birth date whose label had no colon was redacted as a clinic.…, De-identification guarantee: every date digit is gone from the output., The regression: the label survives and the date becomes [DOB]., The thing that was broken: no birth-date case may yield a [CLINIC] span.…, The old FACILITY span captured "DOB 01/01/1970"; the map must hold only the…, A DOB and a plain date in one sentence must not collapse into one placeholder., Guard: a fix that deleted every facility span would pass the rows above. A… (+8 more)

### Community 178 - "test_hyphen_month_dates.py"
Cohesion: 0.17
Nodes (16): deid_rules_only(), Strings that merely look date-ish stay untouched., 15-Mar-2026" after a date label is redacted., An ALL-CAPS export form is caught too., A hyphen-month DOB is redacted., Slash separators work the same as hyphens., These three were inconsistent — the middle one leaked., The pre-existing date formats still redact. (+8 more)

### Community 179 - "test_address_line_labels.py"
Cohesion: 0.17
Nodes (15): deid_rules_only(), Tests for the widened ADDRESS_LINE qualifier list (task 063 finish). Before the…, De-identify with no NER model — the supported no-spaCy machine., The postcode was caught and the street was not, so the line read as redacted…, Practice address:' is now a recognised address field., Clinic address:' is now a recognised address field., The labels that worked before the widening are not regressed., Address words in prose are not fields and must come back unchanged. (+7 more)

### Community 180 - "test_ihi_passport_leaks.py"
Cohesion: 0.17
Nodes (15): deid_rules_only(), Regression tests: IHI and passport numbers were never anchored by the rules.…, De-identify with no NER model — the supported no-spaCy machine., A spaced IHI is fully replaced, leaving no digit groups behind., Hyphen separators and the spelled-out label are handled., An unseparated IHI with no colon is still anchored., A passport number is redacted via the Passport label., Bare "Passport:" with no No/Number word still anchors. (+7 more)

### Community 181 - "test_ollama_empty_response.py"
Cohesion: 0.19
Nodes (13): _patch(), An empty or errored Ollama response must raise, not yield an empty draft. The…, Enough of an HTTP response for ``generate`` to read once., The server's own explanation is more useful than our generic one., Only a genuinely empty string is a failure; whitespace is the model's., _Response, _run(), test_a_missing_response_field_raises() (+5 more)

### Community 182 - "test_patient_line_trailing.py"
Cohesion: 0.17
Nodes (15): deid_rules_only(), PATIENT_LINE must keep matching when DOB, Medicare or address details follow…, De-identify with no NER model -- the supported no-spaCy machine., A bare "Name" label must not swallow other fields' values., This exact line appears in sample_documents/07_case_conference_note.docx and…, This exact line appears in sample_documents/13_gp_progress_note.docx and the…, A trailing comma-separated age after the name still redacts., A WorkCover "Worker" line followed by the claim number still redacts the name. (+7 more)

### Community 183 - "test_ingest_binary_txt.py"
Cohesion: 0.21
Nodes (14): _looks_binary(), True when these bytes are not plausibly a text document. ``cp1252`` and…, _fake_docx_bytes(), A binary file renamed .txt must be refused, not decoded into gibberish. cp1252…, Windows exports are a real input; the sniff must not reject them., Emptiness is handled by extract_text's own guard, not this one., test_a_nul_byte_marks_the_file_binary(), test_a_renamed_docx_is_refused() (+6 more)

### Community 184 - "deid"
Cohesion: 0.20
Nodes (14): deid(), fixture, parametrize, Regression tests for the ISO / dotted / compact date fix. A de-identification…, The pipeline with the real analyzer, and with none installed. A machine with no…, The birth label decides the placeholder, whatever the date format., The placeholder maps back to the exact date as typed., A labelled event date redacts as [DATE] in both ISO forms. (+6 more)

### Community 185 - "query_tokens"
Cohesion: 0.20
Nodes (10): Protocol, Per-field retrieval planning for clinical-form generation. Roadmap item E…, Deterministic planner driven by a keyword taxonomy over field labels., RetrievalPlan, RetrievalPlanner, RuleBasedPlanner, query_tokens(), Okapi BM25 over a small in-memory document set — standard library only. Shared… (+2 more)

### Community 186 - "test_stress_corpus_rules_only.py"
Cohesion: 0.22
Nodes (12): normalise(), parametrize, The stress corpus run with the analyzer forced off. This is the same corpus and…, Every must_preserve value must still be present with the rules alone. Over-…, Every allowlisted value must in fact still leak rules-only. This is what stops…, Collapse every whitespace run to one space, so line breaks stop mattering., De-identify one corpus document with the analyzer forced off, once., No must_redact value may survive the rules alone, beyond the allowlist. The… (+4 more)

### Community 187 - "ollama_client.py"
Cohesion: 0.12
Nodes (21): default_model(), missing_model_message(), OllamaError, RuntimeError, Local Ollama client — pinned to the loopback interface. Generation is the first…, The best installed model to draft with, or ``None`` if none are installed.…, Everything the UI needs to describe the local generation backend., Raised for any recoverable problem talking to the local Ollama server. (+13 more)

### Community 188 - "test_bracketed_identifier_value.py"
Cohesion: 0.22
Nodes (12): deid_rules_only(), The claim number is reached when the value itself is bracketed., Hospital No (MRN): 4471982" must be unaffected by the new separator., The ordinary label forms are unchanged., A label with no digit-shaped value still takes nothing., Reference ranges must survive; redacting them destroys clinical meaning., De-identify with no NER model — the supported no-spaCy machine., test_bracketed_value_in_prose() (+4 more)

### Community 189 - "test_claim_number_label.py"
Cohesion: 0.22
Nodes (12): deid_rules_only(), The Cc-line form "(claim WC-2025-118342)" is anchored., The labelled form is unchanged., The abbreviated label is unchanged., Without a digit-shaped value there is nothing to take., Accession, Clinic file and UR No are untouched by this change., De-identify with no NER model — the supported no-spaCy machine., test_bare_claim_in_prose_is_not_an_anchor() (+4 more)

### Community 190 - "test_gp_vignettes_a.py"
Cohesion: 0.36
Nodes (7): parametrize, The two general-practice skeletons added by task 089 sample cleanly., test_every_gappable_field_can_be_blanked(), test_expands_without_gaps(), test_gappable_names_real_fields(), test_target_validates_for_every_form(), _vignette()

### Community 191 - "FormType"
Cohesion: 0.09
Nodes (41): build_target(), The ideal filled form for ``facts`` — deterministic, fact-placed only.…, check_faithfulness(), check_format(), _check_marker_format(), check_placeholders(), check_residual(), _field_is_empty() (+33 more)

### Community 192 - "test_build_dataset_wiring.py"
Cohesion: 0.22
Nodes (4): build_dataset must record placeholders and split by vignette., Previously always [], because build_dataset never passed them., test_every_pair_records_its_known_placeholders(), test_the_split_is_vignette_disjoint()

### Community 193 - "get_form_spec"
Cohesion: 0.17
Nodes (20): get_form_spec(), plan(), _load(), Generic table-row classification: which rows are fields, which are section…, test_biopsychosocial_spec_field_count_and_grid(), test_session_notes_field_walk_finds_nine_fields(), test_session_notes_signature_row_is_excluded(), test_session_notes_spec() (+12 more)

### Community 194 - "pairs.py"
Cohesion: 0.20
Nodes (15): build_manifest(), _carescribe_sha(), content_hash(), Provenance for a built dataset. A content hash over the pair list, plus how it…, SHA-256 over the sorted JSON lines — stable regardless of pair order., make_template_pair(), Pair, Path (+7 more)

### Community 195 - "fixtures.py"
Cohesion: 0.29
Nodes (6): Synthetic test data for the de-identification regression suite. EVERYTHING HERE…, Fully Fabricated Test Data, Synthetic Discharge Summary Fixture, Line-break-split Name Case, Precision Cases In Fixture, Recall Cases In Fixture

### Community 196 - "resolve_model_path"
Cohesion: 0.50
Nodes (5): available_models(), Where a spaCy model package actually lives, or ``None`` if absent. Resolved…, Every spaCy model importable in this environment., resolve_model_path(), test_model_paths_resolve_explicitly()

### Community 197 - "_NullBackend"
Cohesion: 0.40
Nodes (4): _NullBackend, The stub is gone; the contract it declared is still enforced., A backend that never runs — proves the guard fires before any call., test_generation_refuses_empty_text()

### Community 198 - "test_eld_vignettes_a.py"
Cohesion: 0.36
Nodes (7): parametrize, The two elderly care skeletons added by task 097 sample cleanly., test_every_gappable_field_can_be_blanked(), test_expands_without_gaps(), test_gappable_names_real_fields(), test_target_validates_for_every_form(), _vignette()

### Community 199 - "test_settings_panel_screen.py"
Cohesion: 0.60
Nodes (4): AppTest, _run(), test_saving_settings_persists_and_survives_reload(), test_settings_expander_renders_without_error()

### Community 200 - "test_cmht_vignettes_a.py"
Cohesion: 0.36
Nodes (7): parametrize, The two community mental health skeletons added by task 090 sample cleanly., test_every_gappable_field_can_be_blanked(), test_expands_without_gaps(), test_gappable_names_real_fields(), test_target_validates_for_every_form(), _vignette()

### Community 201 - "test_resp_vignettes_a.py"
Cohesion: 0.36
Nodes (7): parametrize, The two respiratory skeletons added by task 094 sample cleanly., test_every_gappable_field_can_be_blanked(), test_expands_without_gaps(), test_gappable_names_real_fields(), test_target_validates_for_every_form(), _vignette()

### Community 204 - "test_datagen_config_is_live.py"
Cohesion: 0.24
Nodes (10): _config(), Every key in datagen.yaml must actually change the corpus. Nine of the twelve…, End to end: the knob must move the corpus, not just be forwarded., Fail on a key that no longer corresponds to behaviour. If you are here because…, The bug that motivated this file: accepted upstream, never passed., test_form_types_are_real_form_names(), test_no_key_is_decorative(), test_specialty_weights_actually_reach_the_sampler() (+2 more)

### Community 205 - "test_cardio_vignettes_a.py"
Cohesion: 0.36
Nodes (7): parametrize, The two cardiology skeletons added by task 093 sample cleanly., test_every_gappable_field_can_be_blanked(), test_expands_without_gaps(), test_gappable_names_real_fields(), test_target_validates_for_every_form(), _vignette()

### Community 206 - "core/__init__.py"
Cohesion: 0.28
Nodes (7): Core logic: Ollama access, ingestion, de-identification, care notes, PHI…, _entity_spans(), Unifies the two things a reviewer might still need to act on in one document's…, One clickable span in a document's redacted text., Placeholder occurrences for low-confidence, not-yet-confirmed entities., _residual_spans(), ReviewSpan

### Community 208 - "test_manifest_split_mode.py"
Cohesion: 0.39
Nodes (8): _manifest(), The manifest records how the data was split, so a reader can check it., _splits(), test_counts_still_match_the_splits(), test_each_split_lists_its_vignettes(), test_existing_manifest_keys_are_untouched(), test_the_listed_vignettes_are_disjoint(), test_the_split_mode_is_recorded()

### Community 212 - "test_resp_vignettes_b.py"
Cohesion: 0.36
Nodes (7): parametrize, The two respiratory skeletons added by task 096 sample cleanly., test_every_gappable_field_can_be_blanked(), test_expands_without_gaps(), test_gappable_names_real_fields(), test_target_validates_for_every_form(), _vignette()

### Community 214 - "wipe_phi"
Cohesion: 0.67
Nodes (4): PHI_KEYS (session-state PHI registry), Drop every document, identifier table, and identity map from memory., wipe_phi(), Bug: form_drafts never registered with PHI_KEYS/wipe_phi

### Community 215 - "render_refinement"
Cohesion: 0.15
Nodes (17): _active_backend(), _invalidate_form_export(), Drop any previously re-identified/exportable content — called whenever the…, Resolve the backend to generate with, honouring saved settings. Centralises…, Render a stream token by token so a slow local model looks alive., First-pass generation. The model receives de-identified text only., Follow-up instructions, on de-identified text only., Verbatim reference passages, retrieved per field at the granularity the planner… (+9 more)

### Community 216 - "write_review_record"
Cohesion: 0.40
Nodes (5): Write the no-PHI audit sidecar for one approved document. Evidence that a…, write_review_record(), test_output_dir_override_redirects_the_audit_sidecar(), test_review_record_counts_auto_vs_reviewed_identifiers(), test_the_sidecar_records_the_attestation()

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
- **343 isolated node(s):** `Direction`, `Palette`, `Type`, `Space & shape`, `Components (`carescribe/ui/components.py`)` (+338 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **42 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

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
- **Why does `deidentify()` connect `deidentify` to `build_dataset.py`, `test_letterhead_address_leak.py`, `rebuild`, `test_labelled_line_columns.py`, `applog.py`, `mapping.py`, `test_sample_document_identifiers.py`, `deidentify.py`, `write_approved`, `residual_scan`, `test_stress_corpus.py`, `conftest.py`, `create_patient`, `available_forms`, `test_docx_revision_leak.py`, `test_dob_facility_mislabel.py`, `deid`, `test_stress_corpus_rules_only.py`, `test_pipeline_opens_no_socket`, `test_crisis_lines_preserved.py`, `write_review_record`, `test_deid_pipeline.py`, `NoEgress`, `load_documents`, `test_generation_setup.py`, `test_docx_letterhead_leak.py`, `test_full_pipeline_accounts.py`, `test_patient_pipeline.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `render_review()` connect `Document` to `review_spans`, `app.py`, `theme.py`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._