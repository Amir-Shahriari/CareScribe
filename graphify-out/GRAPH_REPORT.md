# Graph Report - medgpt  (2026-09-09)

## Corpus Check
- 244 files · ~192,767 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3174 nodes · 6225 edges · 182 communities (148 shown, 34 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 94 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b8813819`
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
- test_validators.py
- model_setup.py
- test_train_and_grammar.py
- test_reasoning_strip.py
- fill_template
- test_desktop_packaging.py
- plan
- test_cloud_client.py
- Clinic reference library — design
- generation_status
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
- make_gap_probes
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
- write_review_record
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
- patient_output_dir
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
- Clinical fine-tune v2 — honest evaluation, corpus rebuild, patient roll-up
- Patient records store — design
- test_generator_backend.py
- test_review_gate.py
- test_backend_overrides.py
- load_documents
- test_generation_setup.py
- CareScribe clinical drafting model — model card
- _build_analyzer
- BM25
- <id> — <title>
- FormType
- generate
- LLM backend flexibility + realistic test corpus + full-pipeline validation
- verify_frozen.py
- Per-field retrieval planner — design
- components/__init__.py
- test_run_eval_wiring.py
- batch.py
- Evaluation report
- compilerOptions
- users.py
- test_docx_letterhead_leak.py
- AGENTS.md — rules for automated coding agents in this repo
- Task board
- Global Constraints
- test_full_pipeline_accounts.py
- finetune/
- test_filed_document_drafting.py
- load_protected_terms
- test_reference_library.py
- test_patient_pipeline.py
- set_active_user
- finetune/__init__.py
- integrate/__init__.py
- carenotes.py
- get_form_spec
- medgpt-finetune
- test_letterhead_address_leak.py
- Path
- Pattern
- Defects this plan fixes
- create_user
- eval/__init__.py
- describe_backends
- CareScribe site
- assemble/__init__.py
- test_auth_gate.py
- render_approval
- tsconfig.json
- Jordan Whitfield (fictional test client)
- Generation backend selection order (Ollama > built-in GGUF > Cloud)
- NoEgress
- app.py
- parse_fields
- applog.py
- test_ollama_empty_response.py
- backends.py
- desktop.py
- mapping.py
- run_app.py
- extract_text
- test_sample_document_identifiers.py
- test_medicare_number_leak.py
- residual_scan
- authenticate
- document_from_deidentified
- core/__init__.py
- Pinned Dependencies
- RuntimeError
- DeidentificationError
- username_taken
- missing_model_message
- Any
- OllamaError
- test_app_clinical_forms.py
- _fresh_generation_status_cache
- is_model_present
- isolated_store
- create_patient
- FormType
- _RecordingBackend
- Path
- Protocol
- test_nothing_downloads_on_import_or_launch
- test_the_draft_state_and_backend_state_are_not_confused
- test_the_draft_state_carries_the_expected_keys
- Path

## God Nodes (most connected - your core abstractions)
1. `deidentify()` - 92 edges
2. `Document` - 55 edges
3. `create_user()` - 52 edges
4. `get_form_spec()` - 47 edges
5. `create_patient()` - 43 edges
6. `EncounterFacts` - 40 edges
7. `residual_scan()` - 39 edges
8. `extract_text()` - 35 edges
9. `set_active_user()` - 35 edges
10. `FormType` - 31 edges

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

## Communities (182 total, 34 thin omitted)

### Community 0 - "candidate_residuals"
Cohesion: 0.12
Nodes (19): candidate_residuals(), Flag, _is_common(), outstanding(), _placeholder_ranges(), Residual-candidate highlighter — where the reviewer's eye should go first. This…, One span worth a second look, with its offsets in the redacted text., Identity for dismissal — per value, so one decision covers repeats. (+11 more)

### Community 1 - "ingest.py"
Cohesion: 0.13
Nodes (19): Any, _block_text(), _extract_docx(), _extract_pdf(), _extract_txt(), _header_footer_parts(), IngestError, normalise_line_endings() (+11 more)

### Community 2 - "build_dataset.py"
Cohesion: 0.07
Nodes (54): build(), _fallback_inject(), _load_datagen_config(), main(), Path, End-to-end: sampled encounters -> validated SFT pairs + manifest. python -m…, Return ``{"pairs": [...], "kept": k, "dropped": d, "reasons": {...}}``.…, Fill ``[[TOKEN]]`` slots with simple fake values. Used only until… (+46 more)

### Community 3 - "render_refinement"
Cohesion: 0.10
Nodes (27): _active_backend(), _as_docx(), _invalidate_form_export(), Drop any previously re-identified/exportable content — called whenever the…, Resolve the backend to generate with, honouring saved settings. Centralises…, A concrete "it works", rather than asking the clinician to trust a flag., Render a stream token by token so a slow local model looks alive., First-pass generation. The model receives de-identified text only. (+19 more)

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
Nodes (35): approved_map(), document_has_text_boxes(), The reviewer-approved ``{literal: placeholder}`` map for the Word pass. This is…, True if a .docx holds text this redaction pass cannot reach., extract_text(), Flatten a docx to text (body + tables + headers/footers) for a residual scan., _build(), fixture (+27 more)

### Community 8 - "test_app.py"
Cohesion: 0.05
Nodes (72): deid(), ner_available(), fixture, Shared pytest fixtures. The spaCy model load costs several seconds, so the…, The full pipeline's output for the fixture document., True when a spaCy model loaded — layer 2 tests skip without one., raw_text(), redacted() (+64 more)

### Community 9 - "schema.py"
Cohesion: 0.09
Nodes (36): BaseModel, field_validator, _blank_for(), expand(), Random, Turn vignettes into `EncounterFacts` instances with a seeded RNG. `expand`…, Yield ``n`` `EncounterFacts`, deterministic for a given ``seed``., Build one `EncounterFacts` from a vignette. With ``gap_probability`` > 0, each… (+28 more)

### Community 10 - "generate_document"
Cohesion: 0.08
Nodes (38): assert_no_residual_identifiers(), CareNoteError, generate_document(), load_prompt(), RuntimeError, The shared preamble — role, anti-fabrication rules, placeholder rules., Refuse to send text the residual sweep still flags. :func:`assert_deidentified`…, Stream a drafted document from approved de-identified text. ``phi_values`` is… (+30 more)

### Community 11 - "test_template_ingest.py"
Cohesion: 0.13
Nodes (21): available_forms(), (form_id, title) pairs — bundled forms first, then clinic-uploaded ones., fill_parsed_template(), Fill an in-memory copy of ``original_docx`` from ``spec``'s anchors. A thin…, _anchors(), _build_synthetic(), _merge_full_width(), fixture (+13 more)

### Community 12 - "Local clinical LLM fine-tune — design"
Cohesion: 0.06
Nodes (30): 10. Workstream E — integration, 11. What needs a human / external resource, 12. Milestones (testable deliverables), 13. Testing strategy, 1. Goal, 2. Constraints inherited from CareScribe, 3. Approach (selected), 4. Base model (+22 more)

### Community 13 - "patients.py"
Cohesion: 0.10
Nodes (32): active_user(), _clean_name(), delete_patient(), get_patient(), _now(), patient_dir(), PatientError, patients_root() (+24 more)

### Community 14 - "devDependencies"
Cohesion: 0.06
Nodes (35): lucide-react, oxlint, react, react-dom, dependencies, lucide-react, react, react-dom (+27 more)

### Community 15 - "test_validators.py"
Cohesion: 0.13
Nodes (22): check_format(), _check_marker_format(), check_placeholders(), check_residual(), Every ``<<FIELD:key>>`` marker present, in the spec's order, nothing before the…, Fail on a mangled or invented bracket token; ignore ``missing``. A filled form…, A regression set built from the repo's own corpus, not synthetic data.…, regressed() (+14 more)

### Community 16 - "model_setup.py"
Cohesion: 0.13
Nodes (22): Option A. The only outbound request the app makes, on an explicit click., run_model_download(), clear_partial_download(), download_model(), _free_bytes(), model_destination(), ModelSetupError, Progress (+14 more)

### Community 17 - "test_train_and_grammar.py"
Cohesion: 0.05
Nodes (54): _body_rules(), compile_grammar(), field_grammar(), _lit(), note_grammar(), _placeholder_rule(), GBNF grammars for constrained local decoding — a structural guarantee on top of…, Compile a GBNF string with llama-cpp-python, or return ``None``. Never raises:… (+46 more)

### Community 18 - "test_reasoning_strip.py"
Cohesion: 0.12
Nodes (25): Remove a model's reasoning monologue from a finished draft. Idempotent. Text…, strip_reasoning(), _drain(), Generation must hand the clinician the finished document, not the model's…, A backend that prefixes its answer with a planning monologue., ReasoningBackend, test_a_bare_closing_tag_takes_everything_before_it(), test_a_wellformed_think_block_is_removed() (+17 more)

### Community 19 - "fill_template"
Cohesion: 0.15
Nodes (20): _clear_cell(), _dedupe_row(), _fill_cell(), _fill_cell_after_label(), _fill_header_cell(), fill_template(), Remove every paragraph after the first, and every run in the first, leaving one…, Overwrite a dedicated value cell (label lives in a different cell). (+12 more)

### Community 20 - "test_desktop_packaging.py"
Cohesion: 0.10
Nodes (14): available_ram_gb(), ram_verdict(), Total system RAM in GB, or 0.0 if it cannot be determined., Whether this machine can run the bundled local model. Returns a verdict rather…, _cloud_off(), fixture, The packaging invariants: what the desktop app may and may not do. Packaging is…, No key may be committed, defaulted, or written anywhere. (+6 more)

### Community 21 - "plan"
Cohesion: 0.16
Nodes (16): plan(), Protocol, Per-field retrieval planning for clinical-form generation. Roadmap item E…, Deterministic planner driven by a keyword taxonomy over field labels., RetrievalPlan, RetrievalPlanner, RuleBasedPlanner, _field() (+8 more)

### Community 22 - "test_cloud_client.py"
Cohesion: 0.10
Nodes (25): CloudError, _config(), _post(), RuntimeError, Transport for the optional cloud generation backend. Reached only when a…, Yield the payload of each ``data:`` line in an SSE stream., Stream a completion from the configured cloud provider, yielding text. Raises…, A recoverable problem talking to the configured cloud provider. (+17 more)

### Community 23 - "Clinic reference library — design"
Cohesion: 0.17
Nodes (11): `app.py`, Architecture, Clinic reference library — design, Decision, Follow-ups (not blocking), New `core/reference_library.py`, Privacy / safety, Problem (+3 more)

### Community 24 - "generation_status"
Cohesion: 0.10
Nodes (25): cache_data, _draft_state(), _form_draft_state(), Which backend will be used, and the fix if none is available., Shown instead of an empty panel when no model is available yet. An empty…, Option B. Ollama does the fetching; the request goes to loopback., Generate, refine, re-identify and export — for one approved document. Two…, Let a clinic add its own table-based .docx form to the selector. Parsing and… (+17 more)

### Community 25 - "deidentify"
Cohesion: 0.05
Nodes (66): deidentify(), Run the full local pipeline over one document. CPU-only and offline: no model…, _mrn_values(), parametrize, Regression suite for the five leaks found on a second, non-fixture document.…, The precision guard that keeps clinical context intact., A two-part capitalised phrase mid-document is not a letterhead., Layer 1 must carry this on its own — NER catching it is luck, not a guarantee. (+58 more)

### Community 26 - "render_sidebar"
Cohesion: 0.09
Nodes (36): _model_card_dialog(), PHI_KEYS (session-state PHI registry), Drop every document, identifier table, and identity map from memory., Name the generation model with a readable label; the card opens in a dialog…, _render_generation_model(), render_sidebar(), wipe_phi(), chip() (+28 more)

### Community 27 - "compilerOptions"
Cohesion: 0.08
Nodes (23): DOM, src, vite/client, compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx (+15 more)

### Community 28 - "test_generation.py"
Cohesion: 0.06
Nodes (38): finalise(), Build the user prompt for one template with the source text embedded., Re-identify a draft locally and refuse to hand back a leaky document. Returns…, render_prompt(), check_placeholder_integrity(), Compare a draft's bracketed tokens against the placeholders it should use. An…, Local re-identification of a generated draft. Returns ``(text, unresolved)``.…, reidentify_document() (+30 more)

### Community 29 - "deidentify.py"
Cohesion: 0.05
Nodes (71): cache_resource, load_detection_engine(), Load the NER model once per session, not once per rerun. Streamlit re-runs the…, analyze(), classify_person(), _collapse_facility_subsets(), _collapse_person_subsets(), _crosses_paragraph_break() (+63 more)

### Community 30 - "assert_deidentified"
Cohesion: 0.16
Nodes (14): assert_deidentified(), CloudBackend (unwired seam), True only when ``needle`` occurs in ``haystack`` as a whole token run. Both are…, Refuse to send anything carrying a value from the identity mapping. A cheap,…, _value_present(), System prompt (anti-fabrication rules), Optional cloud generation path (off by default), Two required env vars (CARESCRIBE_CLOUD_PROVIDER / CARESCRIBE_CLOUD_API_KEY) (+6 more)

### Community 31 - "test_patient_browser.py"
Cohesion: 0.07
Nodes (50): _document_bytes(), One filed artefact: preview what can be shown, download what cannot., Browse this account's patients and read what has been filed for each. Separate…, render_document_viewer(), render_patient_browser(), FiledDocument, Patient, document_label() (+42 more)

### Community 32 - "Architecture"
Cohesion: 0.13
Nodes (14): 1. Template assets, 2. Form spec extraction, 3. Header fields (practitioner-entered), 4. Multi-document source combination, 5. Generation, 6. Review, 7. Export, 8. UI (`app.py`, Step 5) (+6 more)

### Community 33 - "test_stress_corpus.py"
Cohesion: 0.05
Nodes (48): answer_key.json, Community MH Discharge Letter (doc01), Mohammed Al-Rashid ('Mo'), Cardiology Discharge Summary (doc02), Margaret Elizabeth Chen ('Peggy'), Elspeth Mackenzie-Ford ('Ellie'), GP Referral Letter (doc05), Priya Venkataraman (+40 more)

### Community 34 - "combine_sources"
Cohesion: 0.16
Nodes (16): ClinicalFormError, combine_sources(), RuntimeError, Raised when a clinical form can't be built or filled., Concatenate several documents' de-identified text into one source. ``sources``…, Regression test for Finding 3: raw filename must not leak into model-facing…, Regression test for Finding 1: cap at 26 documents (A-Z)., Regression test for Finding 1: prefixed placeholders must match PLACEHOLDER_RE.… (+8 more)

### Community 35 - "write_approved"
Cohesion: 0.11
Nodes (25): list_folder(), Return the supported documents in ``folder``, sorted by name. Non-recursive on…, Findings from the safety sweep, minus the ones the reviewer has cleared. A…, Write approved de-identified text to the output folder. Re-runs the safety…, sweep(), write_approved(), parametrize, Batch loading and the approved-write path. The privacy invariant under test:… (+17 more)

### Community 36 - "make_gap_probes"
Cohesion: 0.16
Nodes (25): EvalItem, confabulated(), confabulation_rate(), gapped_headings(), make_gap_probes(), _norm(), Adversarial probes for the "Not documented." behaviour. Every probe is an…, Fraction of probes that invented content. ``None`` when uncomputable. (+17 more)

### Community 37 - "CareScribe — design system"
Cohesion: 0.20
Nodes (9): Browser surfaces, CareScribe — design system, Components (`carescribe/ui/components.py`), Direction, Palette, Sidebar order, Space & shape, Type (+1 more)

### Community 38 - "make_icon.py"
Cohesion: 0.29
Nodes (12): Image, _load_font(), main(), Path, Generate CareScribe's placeholder icon. A real icon is a design job; this…, The first usable bold face, or ``None`` if none of them load., A rounded square with "CS" centred on it., macOS only. Silently skipped elsewhere — the .app is built on a Mac. (+4 more)

### Community 39 - "expand_name_variants"
Cohesion: 0.07
Nodes (30): _collapse_person_identities(), True for a person row whose role is known (patient / relative / clinician)., Collapse every written form of one person onto a single entity row.…, REDACT_INPROSE_DATES flag, _specific_person_type(), canonical_person_key(), expand_name_variants(), expand_org_variants (Layer 4 — variant expansion) (+22 more)

### Community 40 - "exemplars.py"
Cohesion: 0.16
Nodes (23): add_exemplar(), count(), _dir(), _load(), _path(), Path, House-style exemplar retrieval for clinical-form generation. A clinic…, Top-``k`` stored values for ``field_key``, ranked by BM25 against ``query``. (+15 more)

### Community 41 - "theme.py"
Cohesion: 0.33
Nodes (4): CareScribe UI layer — the visual identity, applied over Streamlit. `theme.CSS`…, inject(), CareScribe visual identity — one stylesheet, injected once per rerun. DIRECTION…, Apply the stylesheet. Import Streamlit lazily so the module stays cheap.

### Community 42 - "ollama_client.py"
Cohesion: 0.23
Nodes (12): default_model(), is_up(), list_models(), Local Ollama client — pinned to the loopback interface. Generation is the first…, The best installed model to draft with, or ``None`` if none are installed.…, Everything the UI needs to describe the local generation backend., Open a request against the pinned loopback base URL., True if the local Ollama daemon answers. Never raises. (+4 more)

### Community 43 - "auth.py"
Cohesion: 0.08
Nodes (43): apply_scope(), current_user_id(), _honesty_caption(), is_signed_in(), normalise_username(), password_confirmation_error(), password_error(), The sign-in gate, and the account panel in the sidebar. CareScribe now opens on… (+35 more)

### Community 44 - "test_buildinfo.py"
Cohesion: 0.24
Nodes (10): build_info(), Build information for CareScribe., Return standard HTTP User-Agent string., Return application identity and version., user_agent(), Tests for buildinfo module., Test that user_agent returns correct format., Test that build_info returns correct name and version. (+2 more)

### Community 45 - "docx_redact.py"
Cohesion: 0.16
Nodes (17): apply_redactions(), _delete_prefix(), has_unreachable_text(), _iter_groups(), _iter_paragraphs(), _norm(), Structure-preserving .docx redaction. apply_redactions(path_in, path_out,…, Redact a literal split across a paragraph boundary (wrapped name). (+9 more)

### Community 46 - "highlight_review"
Cohesion: 0.24
Nodes (9): highlight_review(), Click-to-redact highlighted text. Renders already-redacted (or already-flagged)…, Render ``html`` and return the ``data-span-id`` of the last click. Returns…, _frontend_path(), Path, Offline-first: nothing in this file may fetch from a CDN., test_frontend_file_exists(), test_frontend_has_no_external_script_or_link_tags() (+1 more)

### Community 47 - "test_combined_sources_generate_every_form_type_with_a_stub_backend"
Cohesion: 0.32
Nodes (6): skipif, parametrize, Deterministic stand-in for a real generation backend., _StubBackend, test_combined_sources_generate_every_form_type_with_a_stub_backend(), test_ingest_and_deidentify_every_sample_document()

### Community 48 - "test_docx_revision_leak.py"
Cohesion: 0.19
Nodes (18): _document(), Regression: text deleted with track changes on rode out in the approved file.…, Why the sweep has to be what catches it: nothing else can see it., Before the fix this wrote a file with the deleted name still inside it., w:author carries a clinician's name in an attribute, not a text node., Comments are a separate part of the package that no other pass loads., A deletion is not itself a finding -- only an identifier inside one is., A .docx whose body is ordinary and whose revision history is not. (+10 more)

### Community 49 - "write_review_record"
Cohesion: 0.13
Nodes (21): approved_docx_path(), approved_path(), _default_output_dir(), The folder a write lands in — an explicit override, or the default.…, Where the approved de-identified text for ``name`` will be written., The raw bytes behind an upload or a path, without copying it to disk., Where the review audit sidecar for ``name`` will be written., Write the no-PHI audit sidecar for one approved document. Evidence that a… (+13 more)

### Community 50 - "Model Card for phi35-v1"
Cohesion: 0.33
Nodes (5): Citations, Framework versions, Model Card for phi35-v1, Quick start, Training procedure

### Community 51 - "Installing CareScribe"
Cohesion: 0.22
Nodes (8): Before you start, First launch, If it will not start, Installing CareScribe, macOS, Updating, Where your files go, Windows

### Community 52 - "EncounterFacts"
Cohesion: 0.11
Nodes (36): build_target(), _care_plan(), _field_content(), _handover(), _history_lines(), _med_line(), _objective_lines(), _plan_lines() (+28 more)

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

### Community 73 - "patient_output_dir"
Cohesion: 0.22
Nodes (13): Read-only list of what has been filed for this patient., Load a filed de-identified document back into the pipeline for drafting. The…, render_filed_documents(), use_filed_document(), filed_documents(), patient_output_dir(), Where this patient's approved de-identified artefacts are filed., Approved artefacts filed for this patient, newest first. (+5 more)

### Community 74 - "House-style exemplar retrieval — design"
Cohesion: 0.18
Nodes (10): `app.py`, Architecture, `core/clinical_forms.py`, Follow-ups (not blocking), House-style exemplar retrieval — design, New module `core/exemplars.py`, Privacy, Problem (+2 more)

### Community 76 - "clinical_forms.py"
Cohesion: 0.16
Nodes (23): _biopsychosocial_spec(), build_prompt(), _form_grammar(), FormField, FormSpec, generate_form_document(), _grid_fields(), HeaderField (+15 more)

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
Cohesion: 0.09
Nodes (31): EncounterFacts, aggregate(), DraftScore, FormType, The four target metrics, scored per draft and reducible to a mean. Format,…, Mean of each metric over ``scores``., score_draft(), build_report() (+23 more)

### Community 87 - "Lightweight review UX for de-identification — design"
Cohesion: 0.14
Nodes (13): 1. Confidence tiering (drives what gets a click at all), 2. One primary review view, not three, 3. The click-to-redact component, 4. Attestation & audit trail, 5. Crash-risk fixes, Architecture, Current state (for reference), Goals (+5 more)

### Community 88 - "test_deid_pipeline.py"
Cohesion: 0.03
Nodes (67): DeidResult, Re-derive redacted text and the PHI map from a reviewer-edited table. Called…, Everything the de-identification stage produces for one document., rebuild(), Replace every surface form of every entity with its placeholder. Replacement…, redact(), parametrize, Regression suite for the layered de-identification pipeline. Two guarantees,… (+59 more)

### Community 89 - "review_spans"
Cohesion: 0.32
Nodes (12): Every clickable span in ``redacted_text``, in reading order. ``confirmed`` is…, review_spans(), _entity(), action=Keep means the reviewer already decided — nothing to click on the…, test_a_confirmed_entity_produces_no_span(), test_a_kept_entity_produces_no_entity_span(), test_auto_confidence_entities_produce_no_span(), test_dismissed_residual_flags_are_excluded() (+4 more)

### Community 90 - "query_tokens"
Cohesion: 0.50
Nodes (4): query_tokens(), Okapi BM25 over a small in-memory document set — standard library only. Shared…, Tokens for the *query* side — content words only., tokenize()

### Community 91 - "Clinical fine-tune v2 — honest evaluation, corpus rebuild, patient roll-up"
Cohesion: 0.07
Nodes (28): 10. Milestones, 1. Why there is a v2, 2. The placeholder-namespace problem, and the chosen resolution, 3.1 Hold out vignettes, not rows, 3.2 Report contamination rather than assuming its absence, 3.3 Break self-marking on faithfulness, 3.4 Delete `style_match`; re-earn it later, 3.5 Adversarial gap probe as a first-class metric (+20 more)

### Community 92 - "Patient records store — design"
Cohesion: 0.11
Nodes (17): 10. Rejected alternatives, 1. Goal, 2. Constraints inherited from CareScribe, 3. The one deliberate change to the privacy posture, 4. Storage layout, 5.1 `carescribe/core/desktop.py`, 5.2 `carescribe/core/patients.py` (new), 5.3 `carescribe/core/batch.py` (+9 more)

### Community 93 - "test_generator_backend.py"
Cohesion: 0.11
Nodes (19): GeneratorBackend, get_backend(), OllamaBackend, OpenAICompatibleBackend, TemplateBackend, Test that TemplateBackend properly renders facts in proforma style, Test that TemplateBackend properly renders facts in prose style, Test that TemplateBackend is deterministic - same input gives same output (+11 more)

### Community 94 - "test_review_gate.py"
Cohesion: 0.10
Nodes (24): blocking_reason(), The approval gate. Only the **authoritative safety sweep** blocks approval. A…, Why Approve is disabled, in one short line. Empty string means it isn't.…, _flag_values(), fixture, parametrize, The reviewer gate: candidate highlighting, the adaptive checklist, and the no-…, Low-confidence redactions are already in place; the permissive flags are… (+16 more)

### Community 95 - "test_backend_overrides.py"
Cohesion: 0.10
Nodes (26): Pick a backend. Returns ``(kind, backend, label)``. ``prefer`` lets the UI…, select_backend(), OllamaBackend, Local generation through the loopback-pinned Ollama daemon., _backend_with_fake_model(), _FakeModel, _raising_stream(), The happy path must keep working: finish_reason 'stop' yields the text with no… (+18 more)

### Community 96 - "load_documents"
Cohesion: 0.11
Nodes (22): analyze_document(), load_documents(), Extract text from uploads or paths. Returns ``(documents, errors)``. One…, Run the de-identification layers over one document, in place., FakeUpload, Stands in for a Streamlit UploadedFile., test_analyze_document_populates_state(), test_duplicate_filenames_are_reported() (+14 more)

### Community 97 - "test_generation_setup.py"
Cohesion: 0.09
Nodes (16): mapping_module(), _nothing_available(), First-run generation setup: never an empty panel, and the egress line held. The…, A second call within the TTL must not re-probe Ollama., The one outbound path must not be reachable from the de-id flow., Renamed from `state` so the collision cannot recur., A fresh PC: no Ollama, no model file, no cloud., test_a_fresh_pc_is_not_ready_and_says_what_to_do() (+8 more)

### Community 98 - "CareScribe clinical drafting model — model card"
Cohesion: 0.40
Nodes (4): CareScribe clinical drafting model — model card, Evaluation, Known limitations, Training data

### Community 99 - "_build_analyzer"
Cohesion: 0.25
Nodes (9): available_models(), _build_analyzer(), is_frozen_build(), Where a spaCy model package actually lives, or ``None`` if absent. Resolved…, Every spaCy model importable in this environment., Build a Presidio ``AnalyzerEngine`` over spaCy. Returns (engine, model, error)., resolve_model_path(), test_a_missing_model_in_a_frozen_build_says_so() (+1 more)

### Community 100 - "BM25"
Cohesion: 0.18
Nodes (9): ExemplarError, RuntimeError, Raised when an exemplar cannot be stored — e.g. it still holds an identifier., RuntimeError, Raised when a reference file cannot be stored., ReferenceError, BM25, Okapi BM25. ``documents`` is a list of token lists. (+1 more)

### Community 101 - "<id> — <title>"
Cohesion: 0.29
Nodes (6): Acceptance criteria, Do NOT touch, Files in scope, Goal, <id> — <title>, Notes

### Community 102 - "FormType"
Cohesion: 0.14
Nodes (20): build_messages(), Care note templates. Every template shares the same hard rule: the input is…, Return ``(system, user)`` for a template label and de-identified document., Enum, FormType, The output form a training example asks the model to fill., build_messages(), default_instruction() (+12 more)

### Community 103 - "generate"
Cohesion: 0.21
Nodes (12): generate(), Stream a completion from the local model, yielding text chunks. Low temperature…, FakeResponse, ndjson(), Tests for ollama_client.generate() — the streaming parser and its error paths., test_daemon_down_and_missing_model(), test_done_stops_and_error_fails(), test_generate_is_a_generator_and_defers_the_network() (+4 more)

### Community 104 - "LLM backend flexibility + realistic test corpus + full-pipeline validation"
Cohesion: 0.20
Nodes (9): A. Backend/settings flexibility, B. Realistic document corpus, C. Full-pipeline validation loop, Design, Goals, LLM backend flexibility + realistic test corpus + full-pipeline validation, Non-goals, Problem (+1 more)

### Community 105 - "verify_frozen.py"
Cohesion: 0.36
Nodes (9): bundled_app_py(), _default_dist(), find_executable(), free_port(), main(), Path, Post-build smoke check: does the frozen CareScribe binary actually start? A…, Locate the frozen entry-point inside a PyInstaller output directory. (+1 more)

### Community 106 - "Per-field retrieval planner — design"
Cohesion: 0.17
Nodes (11): `app.py`, Architecture, `core/reference_library.py`, `core/retrieval_planner.py` (new), `core/text_search.py`, Decision, Follow-ups (not blocking), Per-field retrieval planner — design (+3 more)

### Community 108 - "test_run_eval_wiring.py"
Cohesion: 0.15
Nodes (21): _confabulation_for(), GgufCompleter, load_eval_items(), main(), _overlap_for(), Adapter over a local GGUF via llama-cpp-python. Greedy, temperature 0., Nearest-train-neighbour similarity for the evaluated targets. Reported so a…, Confabulation rate on adversarial "Not documented." probes. (+13 more)

### Community 109 - "batch.py"
Cohesion: 0.18
Nodes (16): BatchError, _blanked_properties(), _document_property_text(), Batch input and approved-output handling. The single module in CareScribe that…, Blank the .docx metadata fields that carry names, places and dates. Rewrites…, Every scrap of text in the .docx property parts, for the residual sweep. Read…, Text in a .docx that no other pass reads: deletions, comments, notes. All of it…, Header, footer and text-box content -- what ``_extract_docx`` never reads.… (+8 more)

### Community 111 - "compilerOptions"
Cohesion: 0.10
Nodes (19): node, vite.config.ts, compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection (+11 more)

### Community 112 - "users.py"
Cohesion: 0.16
Nodes (23): change_password(), _check_password(), _clean_username(), _derive(), get_user(), _now(), Path, RuntimeError (+15 more)

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
Cohesion: 0.11
Nodes (36): _approve_document(), _every_file(), Filed, AppTest, fixture, Path, The whole pipeline, end to end, through accounts.…, Two accounts sign up, each files documents under their own patient. (+28 more)

### Community 118 - "finetune/"
Cohesion: 0.40
Nodes (4): Environment, finetune/, Layout, Milestones

### Community 119 - "test_filed_document_drafting.py"
Cohesion: 0.12
Nodes (11): Filed patient documents can be drafted from again. A filed ``.deid.txt`` was…, Generation refuses text a human has not approved. This text was approved before…, The map was never written to disk. Nothing can resolve these tokens., The re-identify control is gated on phi_map, so an empty map disables it. A…, raw_text is where a reviewer expects the source document. Filling it with the…, It has not been filed *again*; it is a fresh working copy., test_it_carries_no_identity_map(), test_it_is_already_approved_so_generation_accepts_it() (+3 more)

### Community 120 - "load_protected_terms"
Cohesion: 0.29
Nodes (7): _build_protected_pattern(), load_protected_terms(), Read the editable allow-list. Blank lines and ``#`` comments are ignored., Re-read the allow-list from disk (the file is meant to be edited by hand)., reload_protected_terms(), Pattern, test_the_allow_list_is_an_editable_file()

### Community 121 - "test_reference_library.py"
Cohesion: 0.15
Nodes (22): add_file(), is_empty(), ``(filename, paragraph_count)`` per loaded reference file., Top-``k`` reference passages for ``query`` at ``granularity``. BM25, ``score >…, Store an uploaded reference file. Returns the stored filename., ReferenceHit, search(), sources() (+14 more)

### Community 122 - "test_patient_pipeline.py"
Cohesion: 0.16
Nodes (24): _approve_document(), filed(), FiledCase, fixture, parametrize, Path, End-to-end evaluation of the patient records pipeline, one stage of the user…, Drive the whole pipeline once: two patients, 15 documents filed under one. (+16 more)

### Community 123 - "set_active_user"
Cohesion: 0.14
Nodes (29): list_patients(), migrate_unscoped_into(), Scope every subsequent store call to one account, or to none. Passing ``None``…, Every readable patient, sorted by name (case-insensitive) then id. A folder…, Patient folders sitting in the base, from before accounts existed. These are…, Move pre-accounts patients into ``user_id``'s scope. Returns the count. Called…, set_active_user(), unscoped_patient_ids() (+21 more)

### Community 126 - "carenotes.py"
Cohesion: 0.12
Nodes (17): Backend, _ends_mid_tag(), generate_care_note(), Protocol, Care note generation — local, on approved de-identified text only. The contract…, True if ``text`` ends part-way through what could be a reasoning tag., Filter a token stream so a reasoning prefix never reaches the consumer. Buffers…, Prepend the review banner, without duplicating one already there. (+9 more)

### Community 127 - "get_form_spec"
Cohesion: 0.13
Nodes (21): get_form_spec(), Human-readable rendering for display only — the marker text in ``draft_state``…, render_preview(), Captures exactly what generation handed the model — mirrors the fixture in…, RecordingBackend, test_generate_form_document_refuses_a_real_identifier(), test_generate_form_document_sends_the_field_marker_prompt(), test_refine_form_document_preserves_markers_instruction() (+13 more)

### Community 131 - "test_letterhead_address_leak.py"
Cohesion: 0.31
Nodes (8): _letterhead_line(), parametrize, Regression: an unlabelled letterhead street address leaks in the clear. Found…, The de-identified form of the address/phone letterhead line., The new letterhead rule must not fire on a street word in a sentence., test_a_letterhead_street_address_line_is_taken_whole(), test_street_words_in_prose_are_not_over_redacted(), test_the_sample_letterhead_address_is_fully_redacted()

### Community 134 - "Defects this plan fixes"
Cohesion: 0.14
Nodes (13): Clinical fine-tune v2 — V1 honest evaluation harness, Defects this plan fixes, Global Constraints, Self-review, Task 1: Thread `vignette_id` through to pair metadata, Task 2: Persist what evaluation needs to reconstruct an item, Task 3: Split by vignette, not by row (fixes D1), Task 4: Evaluate the committed held-out split (fixes D4) (+5 more)

### Community 135 - "create_user"
Cohesion: 0.11
Nodes (30): create_user(), Create an account. Raises :class:`UserError` if it cannot., fixture, The local account store. These accounts are workspace separation on a desktop…, A username is arbitrary text. Only the opaque id may name a folder., Nothing trims a password. Only the username is normalised., store(), test_a_file_masquerading_as_a_user_folder_is_ignored() (+22 more)

### Community 137 - "describe_backends"
Cohesion: 0.10
Nodes (22): privacy_indicator(), A persistent, honest statement of where data goes. It must change when cloud…, cloud_enabled(), cloud_key_present(), cloud_provider(), CloudBackend, describe_backends(), True if the runtime and a model file are both present. (+14 more)

### Community 138 - "CareScribe site"
Cohesion: 0.50
Nodes (3): CareScribe site, Local, Notes

### Community 140 - "test_auth_gate.py"
Cohesion: 0.25
Nodes (18): AppTest, The sign-in gate, end to end through the real app. Two things are being pinned…, Everything the screen said, for coarse assertions., run(), test_a_new_account_sees_none_of_another_accounts_patients(), test_a_signed_in_session_reaches_the_app(), test_a_visitor_who_is_not_signed_in_sees_the_sign_in_screen(), test_an_account_sees_its_own_patients_in_the_browser() (+10 more)

### Community 141 - "render_approval"
Cohesion: 0.18
Nodes (15): active_output_dir(), active_patient_id(), document_flags(), _model_card_path(), Path, One click to approve every document that comes back clean. Each is re-run…, The selected patient's id, or "" for scratch mode., Where approved output for the current selection is filed. ``None`` means the… (+7 more)

### Community 143 - "Jordan Whitfield (fictional test client)"
Cohesion: 0.31
Nodes (9): 01_gp_referral_letter.docx, 02_biopsychosocial_intake_notes.docx, 03_session_log_progress_notes.docx, 04_treatment_review_source.docx, Biopsychosocial Assessment form, Client Session Notes form, Client Treatment Review form, Clinical-Forms Pipeline (upload -> de-identify -> approve -> combine sources -> generate form) (+1 more)

### Community 145 - "Generation backend selection order (Ollama > built-in GGUF > Cloud)"
Cohesion: 0.18
Nodes (11): core/model_setup.py (model download, isolated), packaging/build_macos.sh, packaging/build_windows.ps1, packaging/carescribe.iss (Inno Setup script), packaging/make_icon.py, The desktop app (PyInstaller packaging), Generation backend selection order (Ollama > built-in GGUF > Cloud), run_app.py entry point (+3 more)

### Community 146 - "NoEgress"
Cohesion: 0.14
Nodes (10): NoEgress, Fails the test if anything opens a non-loopback socket. Loopback is allowed:…, Re-identification is pure Python — it must not phone anywhere., test_reidentification_opens_no_socket(), The load that used to hang on a captive portal must not exist., Reset the cache so the guard covers a genuine first load., The reported hang: no model, so something tries to download it., test_a_missing_model_fails_loudly_instead_of_fetching() (+2 more)

### Community 147 - "app.py"
Cohesion: 0.09
Nodes (40): current(), documents(), ensure_engine_ready(), entity_confirmed(), entity_frame(), flag_dismissals(), ingest_sources(), main() (+32 more)

### Community 148 - "parse_fields"
Cohesion: 0.44
Nodes (9): parse_fields(), Turn the model's marker-delimited output into ``{field_key: text}``. Any field…, _spec(), test_parse_fields_defaults_missing_field_to_not_documented(), test_parse_fields_first_occurrence_wins_on_duplicate_marker(), test_parse_fields_handles_empty_output(), test_parse_fields_happy_path(), test_parse_fields_ignores_unknown_marker_without_raising() (+1 more)

### Community 149 - "applog.py"
Cohesion: 0.12
Nodes (31): BaseException, The last line of defence: a calm message instead of a stack trace. A clinician…, render_unexpected_error(), exception(), get_logger(), log(), log_path(), Path (+23 more)

### Community 150 - "test_ollama_empty_response.py"
Cohesion: 0.19
Nodes (13): _patch(), An empty or errored Ollama response must raise, not yield an empty draft. The…, Enough of an HTTP response for ``generate`` to read once., The server's own explanation is more useful than our generic one., Only a genuinely empty string is a failure; whitespace is the model's., _Response, _run(), test_a_missing_response_field_raises() (+5 more)

### Community 151 - "backends.py"
Cohesion: 0.20
Nodes (10): BackendError, LocalGGUFBackend, RuntimeError, Generation backends, layered so the app works with nothing installed. Selection…, Raised when a backend cannot be used, with the fix in the message., Shared message for a completion cut off by the token/context budget. A half-…, CPU-only generation from a bundled GGUF via ``llama-cpp-python``. The model is…, _truncation_error() (+2 more)

### Community 152 - "desktop.py"
Cohesion: 0.12
Nodes (30): app_data_dir(), bundle_root(), ensure_dirs(), find_local_model(), is_frozen(), _model_search_dirs(), models_dir(), output_dir() (+22 more)

### Community 153 - "mapping.py"
Cohesion: 0.04
Nodes (63): assign_placeholders(), build_map(), dedupe_entities(), _edit_distance(), expand_facility_variants(), find_known_as(), find_spans(), _form_pattern() (+55 more)

### Community 154 - "run_app.py"
Cohesion: 0.16
Nodes (17): Popen, close_splash(), _fatal(), free_port(), main(), _no_window_kwargs(), CareScribe desktop launcher — the app's entry point. Starts the Streamlit…, Poll the loopback port until Streamlit answers. (+9 more)

### Community 155 - "extract_text"
Cohesion: 0.25
Nodes (14): extract_text(), Extract plain text from an uploaded pdf/docx/txt file. Raises…, FakeUpload, parametrize, Document ingestion checks. No network, no temp copies of PHI., A Windows-authored .txt file must not leak its raw \\r into the pipeline. De-…, test_reads_a_file_path(), test_reads_the_encodings_clinical_exports_use() (+6 more)

### Community 156 - "test_sample_document_identifiers.py"
Cohesion: 0.43
Nodes (7): parametrize, Answer-key regression net for ``sample_documents/``. Unlike ``stress_corpus/``…, Whitfield" on its own (not just the full name) must not survive anywhere., _redacted(), test_patient_identifier_is_absent_from_redacted_text(), test_sample_document_residual_scan_is_clean(), test_the_patient_surname_alone_is_also_gone()

### Community 157 - "test_medicare_number_leak.py"
Cohesion: 0.25
Nodes (10): _mrn_values(), parametrize, Regression: an Australian Medicare number left in the clear. Found by a cockpit…, The number after a Medicare label is taken, like any other MRN., A Medicare mention with no number attached is not a record-number hit., Safety-net: if a Medicare number ever reaches redacted text, approval blocks., test_a_medicare_labelled_number_is_detected_as_a_record_number(), test_residual_scan_catches_a_leaked_medicare_number() (+2 more)

### Community 158 - "residual_scan"
Cohesion: 0.11
Nodes (22): Re-scan ALREADY-REDACTED text for anything that still looks identifying. Runs…, residual_scan(), main(), normalise(), Per-document pass/fail report for the stress corpus. python…, Placeholders are the point of the exercise, not leaks., A .txt file read off a Windows disk arrives with CRLF endings. NER tokenises…, test_crlf_and_lf_documents_behave_identically() (+14 more)

### Community 159 - "authenticate"
Cohesion: 0.18
Nodes (17): any_users(), _as_user(), authenticate(), list_users(), Every readable account record. A damaged one is skipped, never raised. One…, The account for these credentials, or ``None``. One return value for every…, Every readable account, sorted by username (case-insensitive) then id., Is there at least one account? Decides signup-first vs login-first. (+9 more)

### Community 160 - "document_from_deidentified"
Cohesion: 0.20
Nodes (10): document_from_deidentified(), A :class:`Document` standing for text de-identified in an earlier session. This…, fixture, isolated_logger(), Keep the process-wide 'carescribe' logger out of the rest of the suite.…, filed_doc(), What the UI actually does: read the filed bytes, rebuild the document., test_a_filed_document_round_trips_from_disk() (+2 more)

### Community 161 - "core/__init__.py"
Cohesion: 0.28
Nodes (7): Core logic: Ollama access, ingestion, de-identification, care notes, PHI…, _entity_spans(), Unifies the two things a reviewer might still need to act on in one document's…, One clickable span in a document's redacted text., Placeholder occurrences for low-confidence, not-yet-confirmed entities., _residual_spans(), ReviewSpan

### Community 162 - "Pinned Dependencies"
Cohesion: 0.25
Nodes (8): pandas, pdfplumber, Pinned Dependencies, presidio-analyzer, python-docx, spaCy, spaCy Model Fallback Chain, streamlit

### Community 164 - "DeidentificationError"
Cohesion: 0.67
Nodes (3): DeidentificationError, RuntimeError, Raised when de-identification can't run at all.

### Community 165 - "username_taken"
Cohesion: 0.50
Nodes (4): The comparison form: whitespace-collapsed and casefolded. ``casefold`` rather…, Case-insensitively, is this username already in use?, _username_key(), username_taken()

### Community 166 - "missing_model_message"
Cohesion: 0.67
Nodes (3): missing_model_message(), The exact command to fix a missing model, plus what is installed., test_a_missing_model_names_the_pull_command()

### Community 168 - "OllamaError"
Cohesion: 0.67
Nodes (3): OllamaError, RuntimeError, Raised for any recoverable problem talking to the local Ollama server.

### Community 169 - "test_app_clinical_forms.py"
Cohesion: 0.29
Nodes (7): _form_draft_key(), _header_values_complete(), Pure-logic pieces of the clinical-form UI: the session-state key used to key a…, test_form_draft_key_differs_by_form_or_selection(), test_form_draft_key_is_stable_for_the_same_selection(), test_header_values_complete_requires_every_non_reason_field(), test_invalidate_form_export_drops_stale_resolved_values()

### Community 170 - "_fresh_generation_status_cache"
Cohesion: 0.50
Nodes (4): _cloud_off(), _fresh_generation_status_cache(), fixture, generation_status() is now @st.cache_data(ttl=5) — a process-global cache keyed…

### Community 171 - "is_model_present"
Cohesion: 0.50
Nodes (4): is_model_present(), True if a usable model file is already on this computer. This is the marker…, Setup is one-time because the file itself is the state., test_model_presence_is_the_persisted_marker()

### Community 172 - "isolated_store"
Cohesion: 0.67
Nodes (3): isolated_store(), fixture, Accounts and patients both land in tmp, never in the checkout.

### Community 173 - "create_patient"
Cohesion: 0.13
Nodes (23): create_patient(), Create a patient folder and roster entry. Returns the new record., fixture, parametrize, The per-patient records store. `patients.py` owns no detection logic — it is…, Point the store at a scratch dir for every test., _store(), test_a_malformed_id_never_becomes_a_path() (+15 more)

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
- **339 isolated node(s):** `Global Constraints`, `Task 1: Thread `vignette_id` through to pair metadata`, `Task 2: Persist what evaluation needs to reconstruct an item`, `Task 3: Split by vignette, not by row (fixes D1)`, `Task 4: Evaluate the committed held-out split (fixes D4)` (+334 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

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
- **Why does `deidentify()` connect `deidentify` to `build_dataset.py`, `test_letterhead_address_leak.py`, `test_app.py`, `NoEgress`, `applog.py`, `mapping.py`, `test_sample_document_identifiers.py`, `deidentify.py`, `residual_scan`, `test_medicare_number_leak.py`, `test_stress_corpus.py`, `write_approved`, `DeidentificationError`, `create_patient`, `test_combined_sources_generate_every_form_type_with_a_stub_backend`, `test_docx_revision_leak.py`, `write_review_record`, `test_crisis_lines_preserved.py`, `test_deid_pipeline.py`, `load_documents`, `test_generation_setup.py`, `_build_analyzer`, `test_docx_letterhead_leak.py`, `test_full_pipeline_accounts.py`, `test_patient_pipeline.py`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `FormType` connect `FormType` to `build_dataset.py`, `schema.py`, `test_validators.py`, `test_train_and_grammar.py`, `EncounterFacts`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._