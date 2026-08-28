# Graph Report - medgpt  (2026-08-29)

## Corpus Check
- 88 files · ~93,096 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1612 nodes · 2984 edges · 119 communities (93 shown, 26 thin omitted)
- Extraction: 98% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 40 edges (avg confidence: 0.77)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `80732005`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- clinical_forms.py
- deidentify
- test_review_gate.py
- Generation backend selection order (Ollama > built-in GGUF > Cloud)
- Reference: verified template structure
- template_ingest.py
- test_docx_roundtrip.py
- test_app.py
- load_protected_terms
- test_generation.py
- test_template_ingest.py
- desktop.py
- test_generation_setup.py
- mapping.py
- test_mapping.py
- model_setup.py
- docx_redact.py
- backends.py
- fill_template
- carenotes.py
- _span_is_plausible
- test_cloud_client.py
- Clinic reference library — design
- add_manual_entity
- Document
- generation_status
- merge_spans
- analyze
- core/__init__.py
- generate_document
- select_backend
- Architecture
- test_stress_corpus.py
- combine_sources
- assert_deidentified
- Jordan Whitfield (fictional test client)
- test_desktop_packaging.py
- make_icon.py
- rebuild
- exemplars.py
- test_deid_regressions.py
- ollama_client.py
- render_form_draft
- test_a_date_entity_never_spans_a_line_break
- canonical_person_key
- highlight_review
- run_app.py
- get_form_spec
- resolve_placeholder
- fixture
- BackendError
- normalise_type
- Clinic-uploaded clinical form templates — design
- batch.py
- Report templates (SOAP / GP letter / discharge / custom)
- Outpatient Respiratory Clinic Letter (doc03)
- parse_fields
- Reference: verified against the real codebase
- assign_placeholders
- carenotes_prompt.py
- Ward 7B Nursing Handover (doc04)
- test_app_clinical_forms.py
- test_batch.py
- test_clinical_form_templates.py
- carescribe/__init__.py
- deid_prompt.py
- prompts/__init__.py
- build_dmg.sh
- build_macos.sh
- rthook_carescribe.py
- tests/__init__.py
- run_all.py
- residual_scan
- House-style exemplar retrieval — design
- render_draft
- Backend
- Document
- Cloud generation transport (`CloudBackend`) — design
- reference_library.py
- render_clinical_form_panel
- GLiNER Deliberately Uninstalled
- is_model_present
- Sample Source Documents README
- Recurring fictional staff roster (e.g. A. Whitfield) across documents
- Lightweight review UX for de-identification — design
- test_deid_pipeline.py
- test_a_patient_label_outranks_a_kinship_heading
- NoEgress
- redact
- Cardiology Discharge Summary (doc02)
- with_banner
- deidentify.py
- Path
- README.md
- load_documents
- structured_spans
- RuntimeError
- fixture
- RuntimeError
- reidentify
- GP Referral Letter (doc05)
- Per-field retrieval planner — design
- components/__init__.py
- Stress corpus
- RuntimeError
- Path
- fixture
- parametrize
- stress_report.py
- answer_key.json
- test_the_corpus_and_its_answer_key_agree
- Path
- conftest.py
- extract_text
- Protocol
- fixture

## God Nodes (most connected - your core abstractions)
1. `deidentify()` - 66 edges
2. `get_form_spec()` - 44 edges
3. `residual_scan()` - 25 edges
4. `generation_status()` - 23 edges
5. `generate_document()` - 22 edges
6. `load_documents()` - 20 edges
7. `fill_template()` - 19 edges
8. `write_approved()` - 19 edges
9. `structured_spans()` - 19 edges
10. `FormSpec` - 18 edges

## Surprising Connections (you probably didn't know these)
- `Stable per-entity placeholder scheme` --semantically_similar_to--> `build_prompt()`  [INFERRED] [semantically similar]
  README.md → carescribe/core/clinical_forms.py
- `presidio-analyzer` --references--> `_build_analyzer()`  [INFERRED]
  requirements.txt → carescribe/core/deidentify.py
- `spaCy Model Fallback Chain` --rationale_for--> `_build_analyzer()`  [INFERRED]
  requirements.txt → carescribe/core/deidentify.py
- `Bug: stale re-identified export race after refine/regenerate` --rationale_for--> `_invalidate_form_export()`  [EXTRACTED]
  docs/superpowers/plans/2026-08-13-clinical-forms.md → carescribe/app.py
- `Section-path field key slug scheme` --rationale_for--> `slugify()`  [EXTRACTED]
  docs/superpowers/specs/2026-08-13-clinical-forms-design.md → carescribe/core/clinical_forms.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **README report-templates table implemented by prompt files** — readme_report_templates, carescribe_prompts_care_notes_soap_template, carescribe_prompts_clinic_letter_template, carescribe_prompts_discharge_summary_template, carescribe_prompts_custom_template [INFERRED 0.85]
- **Privacy-invariant enforcement chain (assert, sweep, write, integrity)** — carescribe_core_carenotes_assert_deidentified, carescribe_core_deidentify_residual_scan, carescribe_core_batch_write_approved, carescribe_core_mapping_check_placeholder_integrity [EXTRACTED 1.00]
- **Clinical form generation pipeline (combine -> prompt -> generate -> parse -> fill)** — carescribe_core_clinical_forms_combine_sources, carescribe_core_clinical_forms_build_prompt, carescribe_core_clinical_forms_generate_form_document, carescribe_core_clinical_forms_parse_fields, carescribe_core_clinical_forms_fill_template [EXTRACTED 1.00]
- **Sample docs that combine into one fictional client's clinical-forms test flow** — sample_documents_readme_01_gp_referral_letter, sample_documents_readme_02_biopsychosocial_intake_notes, sample_documents_readme_03_session_log_progress_notes, sample_documents_readme_04_treatment_review_source, sample_documents_readme_jordan_whitfield [EXTRACTED 1.00]
- **Fictional patients sharing the same reused NHS number across documents** — stress_corpus_doc01_mohammed_al_rashid, stress_corpus_doc02_margaret_elizabeth_chen, stress_corpus_doc05_elspeth_mackenzie_ford, stress_corpus_doc06_priya_venkataraman, stress_corpus_doc09_tomasz_wisniewski, stress_corpus_shared_nhs_number [INFERRED 0.85]
- **Documents sharing the recurring fictional staff roster (e.g. A. Whitfield, R. Patel)** — stress_corpus_doc01_community_mh_letter, stress_corpus_doc02_cardiology_discharge, stress_corpus_doc04_ward_handover, stress_corpus_doc07_cmht_family_review, stress_corpus_doc10_mha_assessment, stress_corpus_recurring_staff_roster [INFERRED 0.75]

## Communities (119 total, 26 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.16
Nodes (20): current(), documents(), ingest_sources(), main(), PHI_KEYS (session-state PHI registry), CareScribe — local, privacy-preserving de-identification and review. Run with:…, A missing model must stop loudly, never fall back to fetching one., Extract text from uploads/paths into session state. (+12 more)

### Community 1 - "clinical_forms.py"
Cohesion: 0.19
Nodes (19): _biopsychosocial_spec(), build_prompt(), FormField, FormSpec, generate_form_document(), _grid_fields(), HeaderField, _paragraph_texts() (+11 more)

### Community 2 - "deidentify"
Cohesion: 0.14
Nodes (27): deidentify(), Run the full local pipeline over one document. CPU-only and offline: no model…, parametrize, Regression suite for the round-2 leaks (A1-A9). The corpus tests in…, Flattening the break made one span of the org and the next line's town., The dangerous direction: this used to fail open, leaking the whole name., Brother: David Chen\\nWei Chen" was one span covering two people., test_a_bare_number_without_a_case_label_is_left_alone() (+19 more)

### Community 3 - "test_review_gate.py"
Cohesion: 0.05
Nodes (59): blocking_reason(), The approval gate. Approval unlocks once nothing is outstanding: the blocking…, Why Approve is disabled, in one short line. Empty string means it isn't., candidate_residuals(), Flag, _is_common(), outstanding(), _placeholder_ranges() (+51 more)

### Community 4 - "Generation backend selection order (Ollama > built-in GGUF > Cloud)"
Cohesion: 0.18
Nodes (11): core/model_setup.py (model download, isolated), packaging/build_macos.sh, packaging/build_windows.ps1, packaging/carescribe.iss (Inno Setup script), packaging/make_icon.py, The desktop app (PyInstaller packaging), Generation backend selection order (Ollama > built-in GGUF > Cloud), run_app.py entry point (+3 more)

### Community 5 - "Reference: verified template structure"
Cohesion: 0.10
Nodes (20): carescribe/core/clinical_forms.py (module), Refine prompt (clinical form, marker-preserving), Refine prompt (free-form draft revision), Clinical Form Generation (APS Templates) Implementation Plan, Global Constraints, Reference: verified template structure, Self-Review Notes (for the implementer), Task 10: End-to-end generation glue (`generate_form_document`, `refine_form_document`, `render_preview`) (+12 more)

### Community 6 - "template_ingest.py"
Cohesion: 0.12
Nodes (31): Let a clinic add its own table-based .docx form to the selector. Parsing and…, _render_template_uploader(), ClinicalFormError, Raised when a clinical form can't be built or filled., slugify(), delete_template(), _find_grids(), _infer_header() (+23 more)

### Community 7 - "test_docx_roundtrip.py"
Cohesion: 0.08
Nodes (36): approved_map(), document_has_text_boxes(), The reviewer-approved ``{literal: placeholder}`` map for the Word pass. This is…, Redact the original .docx into the output folder, structure preserved. The same…, True if a .docx holds text this redaction pass cannot reach., write_approved_docx(), extract_text(), Flatten a docx to text (body + tables + headers/footers) for a residual scan. (+28 more)

### Community 8 - "test_app.py"
Cohesion: 0.12
Nodes (34): AppTest, analysed_batch(), data_editors(), loaded_batch(), _NullBackend, UI checks for the batch review app via Streamlit's AppTest. No server of any…, The core promise of this redesign: nothing outstanding, no ticks. Deliberately…, Generation must never run on text a human has not approved. (+26 more)

### Community 9 - "load_protected_terms"
Cohesion: 0.29
Nodes (8): _build_protected_pattern(), load_protected_terms(), Path, Pattern, Read the editable allow-list. Blank lines and ``#`` comments are ignored., Re-read the allow-list from disk (the file is meant to be edited by hand)., reload_protected_terms(), test_the_allow_list_is_an_editable_file()

### Community 10 - "test_generation.py"
Cohesion: 0.09
Nodes (26): finalise(), Re-identify a draft locally and refuse to hand back a leaky document. Returns…, check_placeholder_integrity(), Compare a draft's bracketed tokens against the placeholders it should use. An…, Local re-identification of a generated draft. Returns ``(text, unresolved)``.…, reidentify_document(), parametrize, Local generation: the privacy contract, placeholder integrity, and the gate. No… (+18 more)

### Community 11 - "test_template_ingest.py"
Cohesion: 0.16
Nodes (18): available_forms(), (form_id, title) pairs — bundled forms first, then clinic-uploaded ones., fill_parsed_template(), Fill an in-memory copy of ``original_docx`` from ``spec``'s anchors. A thin…, parametrize, _anchors(), _build_synthetic(), _merge_full_width() (+10 more)

### Community 12 - "desktop.py"
Cohesion: 0.14
Nodes (24): app_data_dir(), bundle_root(), ensure_dirs(), find_local_model(), is_frozen(), models_dir(), output_dir(), Path (+16 more)

### Community 13 - "test_generation_setup.py"
Cohesion: 0.07
Nodes (18): _cloud_off(), _fresh_generation_status_cache(), mapping_module(), fixture, First-run generation setup: never an empty panel, and the egress line held. The…, The one outbound path must not be reachable from the de-id flow., A captive portal returns HTML with a plausible size., generation_status() is now @st.cache_data(ttl=5) — a process-global cache keyed… (+10 more)

### Community 14 - "mapping.py"
Cohesion: 0.13
Nodes (19): expand_facility_variants(), expand_name_variants(), _initial_letters(), Issue, name_core(), normalise_action(), In-memory PII <-> placeholder mapping. This module is deliberately pure: it…, Split a name into its parts with any leading honorific removed. "Mrs Margaret… (+11 more)

### Community 15 - "test_mapping.py"
Cohesion: 0.20
Nodes (10): dedupe_entities(), Drop blank and duplicate entities, keeping first-seen order and casing.…, Mapping-layer checks: type normalisation, surface forms, and re-identification.…, If ANY occurrence of a value was low-confidence, the whole entity is., test_dedupe_carries_the_keep_action(), test_dedupe_drops_dangerously_short_values(), test_dedupe_entities_defaults_missing_confidence_to_review(), test_dedupe_entities_keeps_confidence() (+2 more)

### Community 16 - "model_setup.py"
Cohesion: 0.16
Nodes (18): clear_partial_download(), download_model(), _free_bytes(), model_destination(), ModelSetupError, Progress, pull_ollama_model(), Path (+10 more)

### Community 17 - "docx_redact.py"
Cohesion: 0.16
Nodes (17): apply_redactions(), _delete_prefix(), has_unreachable_text(), _iter_groups(), _iter_paragraphs(), _norm(), Structure-preserving .docx redaction. apply_redactions(path_in, path_out,…, Redact a literal split across a paragraph boundary (wrapped name). (+9 more)

### Community 18 - "backends.py"
Cohesion: 0.14
Nodes (20): privacy_indicator(), A persistent, honest statement of where data goes. It must change when cloud…, cloud_enabled(), cloud_key_present(), cloud_provider(), CloudBackend, describe_backends(), Generation backends, layered so the app works with nothing installed. Selection… (+12 more)

### Community 19 - "fill_template"
Cohesion: 0.14
Nodes (22): _clear_cell(), _dedupe_row(), _fill_cell(), _fill_cell_after_label(), _fill_header_cell(), fill_template(), Remove every paragraph after the first, and every run in the first, leaving one…, Overwrite a dedicated value cell (label lives in a different cell). (+14 more)

### Community 20 - "carenotes.py"
Cohesion: 0.14
Nodes (16): CareNoteError, generate_care_note(), load_prompt(), OllamaBackend, RuntimeError, Care note generation — local, on approved de-identified text only. The contract…, Build the user prompt for one template with the source text embedded., Draft a care note from ALREADY DE-IDENTIFIED text, returning it whole. The… (+8 more)

### Community 21 - "_span_is_plausible"
Cohesion: 0.13
Nodes (17): classify_person(), _is_acronym(), _is_labelled_date_field(), _is_staff_context(), _line_bounds(), _location_is_address(), _looks_clinical(), True for a short all-caps token like "ECG" or "LS9" — never a name here. (+9 more)

### Community 22 - "test_cloud_client.py"
Cohesion: 0.09
Nodes (28): CloudError, _config(), _post(), RuntimeError, Transport for the optional cloud generation backend. Reached only when a…, Yield the payload of each ``data:`` line in an SSE stream., Stream a completion from the configured cloud provider, yielding text. Raises…, A recoverable problem talking to the configured cloud provider. (+20 more)

### Community 23 - "Clinic reference library — design"
Cohesion: 0.17
Nodes (11): `app.py`, Architecture, Clinic reference library — design, Decision, Follow-ups (not blocking), New `core/reference_library.py`, Privacy / safety, Problem (+3 more)

### Community 24 - "add_manual_entity"
Cohesion: 0.15
Nodes (13): add_manual_entity(), DeidentificationError, DeidResult, RuntimeError, Add an identifier the tools missed and immediately re-redact. The new value…, Raised when de-identification can't run at all., Everything the de-identification stage produces for one document., A value the layers missed is expanded like a detected one. (+5 more)

### Community 25 - "Document"
Cohesion: 0.17
Nodes (20): document_flags(), entity_confirmed(), entity_frame(), flag_dismissals(), Re-derive the preview and map from an edited entity list., Redact the original .docx using the map the reviewer just approved. Detection…, Offer the redacted .docx, but only once it has cleared the sweep., Candidate residuals for this document, recomputed from current text. (+12 more)

### Community 26 - "generation_status"
Cohesion: 0.10
Nodes (23): cache_data, generation_status(), _llama_runtime_available(), missing_reason(), Is generation usable right now, and if not, what should the user do? Kept…, One plain sentence on why generation is not available yet., Which generation backends are usable at this moment., Which backend would actually be used, matching the backend ladder. (+15 more)

### Community 27 - "merge_spans"
Cohesion: 0.14
Nodes (14): _collapse_facility_subsets(), _collapse_person_identities(), _collapse_person_subsets(), merge_spans(), protected_ranges(), Shrink a NER span to its identifying core. Drops leading titles ("Sister Fiona…, Drop a person entity whose name is contained in a longer one. NER returns…, True for a person row whose role is known (patient / relative / clinician). (+6 more)

### Community 28 - "analyze"
Cohesion: 0.10
Nodes (22): analyze(), flatten_lines(), gliner_spans(), ner_spans(), Layer 2: Presidio/spaCy detections, mapped onto CareScribe entity types.…, Layer 3: GLiNER detections, or an empty list when it isn't installed., Run every enabled layer over ``text`` and return reviewable entities. Each…, One detection, in character offsets over the source text. (+14 more)

### Community 29 - "core/__init__.py"
Cohesion: 0.13
Nodes (19): BaseException, ensure_engine_ready(), Load the model at startup, behind a visible spinner. Deliberately not lazy. If…, The last line of defence: a calm message instead of a stack trace. A clinician…, render_unexpected_error(), exception(), get_logger(), log() (+11 more)

### Community 30 - "generate_document"
Cohesion: 0.12
Nodes (23): generate_document(), Stream a drafted document from approved de-identified text. ``phi_values`` is…, Revise an existing draft against a follow-up instruction. Operates on the same…, The shared preamble — role, anti-fabrication rules, placeholder rules., refine_document(), system_prompt(), Spot-check the instruction is honoured, with the model mocked., Captures exactly what generation handed the model. (+15 more)

### Community 31 - "select_backend"
Cohesion: 0.17
Nodes (16): _invalidate_form_export(), A concrete "it works", rather than asking the clinician to trust a flag., Render a stream token by token so a slow local model looks alive., First-pass generation. The model receives de-identified text only., Follow-up instructions, on de-identified text only., Drop any previously re-identified/exportable content — called whenever the…, render_form_refinement(), render_refinement() (+8 more)

### Community 32 - "Architecture"
Cohesion: 0.13
Nodes (14): 1. Template assets, 2. Form spec extraction, 3. Header fields (practitioner-entered), 4. Multi-document source combination, 5. Generation, 6. Review, 7. Export, 8. UI (`app.py`, Step 5) (+6 more)

### Community 33 - "test_stress_corpus.py"
Cohesion: 0.21
Nodes (12): _entities(), _normalise(), parametrize, Corpus-driven regression net. Every document in ``stress_corpus/`` is run…, Confidence tiering must never make the reviewer's job LESS safe. An "auto"…, Whatever the sweep still flags must not be a structured identifier. A surviving…, Collapse every whitespace run to one space, so line breaks stop mattering., _redacted() (+4 more)

### Community 34 - "combine_sources"
Cohesion: 0.21
Nodes (13): combine_sources(), Concatenate several documents' de-identified text into one source. ``sources``…, Regression test for Finding 3: raw filename must not leak into model-facing…, Regression test for Finding 1: cap at 26 documents (A-Z)., Regression test for Finding 1: prefixed placeholders must match PLACEHOLDER_RE.…, Regression test for Finding 2: text and map rewrites must be consistent. A…, test_combine_sources_no_filename_in_output(), test_combine_sources_non_standard_placeholder_consistency() (+5 more)

### Community 35 - "assert_deidentified"
Cohesion: 0.20
Nodes (12): assert_deidentified(), CloudBackend (unwired seam), Refuse to send anything carrying a value from the identity mapping. A cheap,…, System prompt (anti-fabrication rules), Optional cloud generation path (off by default), Two required env vars (CARESCRIBE_CLOUD_PROVIDER / CARESCRIBE_CLOUD_API_KEY), CareScribe practitioner one-page guide, CareScribe (the application) (+4 more)

### Community 36 - "Jordan Whitfield (fictional test client)"
Cohesion: 0.31
Nodes (9): 01_gp_referral_letter.docx, 02_biopsychosocial_intake_notes.docx, 03_session_log_progress_notes.docx, 04_treatment_review_source.docx, Biopsychosocial Assessment form, Client Session Notes form, Client Treatment Review form, Clinical-Forms Pipeline (upload -> de-identify -> approve -> combine sources -> generate form) (+1 more)

### Community 37 - "test_desktop_packaging.py"
Cohesion: 0.11
Nodes (15): available_ram_gb(), ram_verdict(), Total system RAM in GB, or 0.0 if it cannot be determined., Whether this machine can run the bundled local model. Returns a verdict rather…, _cloud_off(), fixture, The packaging invariants: what the desktop app may and may not do. Packaging is…, No key may be committed, defaulted, or written anywhere. (+7 more)

### Community 38 - "make_icon.py"
Cohesion: 0.29
Nodes (12): Image, _load_font(), main(), Path, Generate CareScribe's placeholder icon. A real icon is a design job; this…, The first usable bold face, or ``None`` if none of them load., A rounded square with "CS" centred on it., macOS only. Silently skipped elsewhere — the .app is built on a Mac. (+4 more)

### Community 39 - "rebuild"
Cohesion: 0.33
Nodes (6): Re-derive redacted text and the PHI map from a reviewer-edited table. Called…, rebuild(), build_map(), Build the placeholder -> original-value map used for re-identification. If two…, test_rebuild_preserves_a_reviewer_edited_placeholder(), test_kept_rows_are_absent_from_the_map()

### Community 40 - "exemplars.py"
Cohesion: 0.06
Nodes (47): add_exemplar(), count(), _dir(), ExemplarError, _load(), _path(), House-style exemplar retrieval for clinical-form generation. A clinic…, Top-``k`` stored values for ``field_key``, ranked by BM25 against ``query``. (+39 more)

### Community 41 - "test_deid_regressions.py"
Cohesion: 0.10
Nodes (27): _mrn_values(), parametrize, Regression suite for the five leaks found on a second, non-fixture document.…, A two-part capitalised phrase mid-document is not a letterhead., Layer 1 must carry this on its own — NER catching it is luck, not a guarantee., M.E.C.\\nFollow-up" must not become the name "M.E.C. Follow"., Regardless of REDACT_INPROSE_DATES, which stays False by default., The label shapes document #2 actually used, including the parenthetical. (+19 more)

### Community 42 - "ollama_client.py"
Cohesion: 0.14
Nodes (19): default_model(), generate(), is_up(), list_models(), missing_model_message(), OllamaError, RuntimeError, Local Ollama client — pinned to the loopback interface. Generation is the first… (+11 more)

### Community 43 - "render_form_draft"
Cohesion: 0.40
Nodes (5): Verbatim reference passages, retrieved per field at the granularity the planner…, render_form_draft(), render_form_reidentification(), _render_reference_panel(), Bug: stale re-identified export race after refine/regenerate

### Community 44 - "test_a_date_entity_never_spans_a_line_break"
Cohesion: 0.33
Nodes (4): 14 June 2026\\nDate" swallowed the next line's label and mangled the text., The precision guard that keeps clinical context intact., test_a_date_entity_never_spans_a_line_break(), test_place_of_care_in_prose_still_survives()

### Community 45 - "canonical_person_key"
Cohesion: 0.22
Nodes (9): canonical_person_key(), keys_are_compatible(), A stable identity key for one person: full given name plus surname. This…, True if two canonical keys can denote the same person. Exact match, or one side…, test_canonical_key_separates_two_people_with_one_surname(), test_canonical_key_unifies_the_forms_of_one_person(), test_a_shared_surname_is_not_a_shared_identity(), test_an_initial_can_stand_in_for_a_given_name() (+1 more)

### Community 46 - "highlight_review"
Cohesion: 0.24
Nodes (9): highlight_review(), Click-to-redact highlighted text. Renders already-redacted (or already-flagged)…, Render ``html`` and return the ``data-span-id`` of the last click. Returns…, _frontend_path(), Path, Offline-first: nothing in this file may fetch from a CDN., test_frontend_file_exists(), test_frontend_has_no_external_script_or_link_tags() (+1 more)

### Community 47 - "run_app.py"
Cohesion: 0.16
Nodes (17): Popen, close_splash(), _fatal(), free_port(), main(), _no_window_kwargs(), CareScribe desktop launcher — the app's entry point. Starts the Streamlit…, Dismiss the bootloader splash, if this is a frozen build that has one.… (+9 more)

### Community 48 - "get_form_spec"
Cohesion: 0.14
Nodes (20): get_form_spec(), Human-readable rendering for display only — the marker text in ``draft_state``…, render_preview(), Captures exactly what generation handed the model — mirrors the fixture in…, RecordingBackend, test_generate_form_document_refuses_a_real_identifier(), test_generate_form_document_sends_the_field_marker_prompt(), test_refine_form_document_preserves_markers_instruction() (+12 more)

### Community 49 - "resolve_placeholder"
Cohesion: 0.29
Nodes (7): _edit_distance(), Levenshtein distance, short-circuiting once it exceeds ``cap``., Map a possibly-corrupted placeholder onto a known one. Returns the exact token…, resolve_placeholder(), Guessing between [MRN_1] and [MRN_2] would attach the wrong identity., test_ambiguous_placeholder_is_refused_not_guessed(), test_edit_distance_caps_out()

### Community 51 - "BackendError"
Cohesion: 0.19
Nodes (8): BackendError, LocalGGUFBackend, RuntimeError, Raised when a backend cannot be used, with the fix in the message., CPU-only generation from a bundled GGUF via ``llama-cpp-python``. The model is…, True if the runtime and a model file are both present., It fabricates otherwise — measured, not assumed., test_the_local_model_stays_pinned_at_temperature_zero()

### Community 52 - "normalise_type"
Cohesion: 0.40
Nodes (5): normalise_type(), Coerce a model-supplied type string onto the canonical list., parametrize, test_normalise_type(), test_reidentify_never_crashes()

### Community 53 - "Clinic-uploaded clinical form templates — design"
Cohesion: 0.18
Nodes (10): Architecture, Clinic-uploaded clinical form templates — design, Follow-ups (not blocking), New module `core/template_ingest.py`, Persistence, Problem, Registry integration (`core/clinical_forms.py`), Scope (+2 more)

### Community 54 - "batch.py"
Cohesion: 0.14
Nodes (20): approved_docx_path(), approved_path(), _default_output_dir(), Path, Batch input and approved-output handling. The single module in CareScribe that…, Reduce a filename to a safe output stem — no paths, no surprises., Where the approved de-identified text for ``name`` will be written., The raw bytes behind an upload or a path, without copying it to disk. (+12 more)

### Community 55 - "Report templates (SOAP / GP letter / discharge / custom)"
Cohesion: 0.40
Nodes (5): SOAP care note prompt template, GP clinic letter prompt template, Custom (clinician house format) prompt template, Discharge summary prompt template, Report templates (SOAP / GP letter / discharge / custom)

### Community 56 - "Outpatient Respiratory Clinic Letter (doc03)"
Cohesion: 0.40
Nodes (5): Ngozi Okafor, Outpatient Respiratory Clinic Letter (doc03), Attendee list pattern, Header town + county pattern, Record-number label shapes (three variants)

### Community 57 - "parse_fields"
Cohesion: 0.44
Nodes (9): parse_fields(), Turn the model's marker-delimited output into ``{field_key: text}``. Any field…, _spec(), test_parse_fields_defaults_missing_field_to_not_documented(), test_parse_fields_first_occurrence_wins_on_duplicate_marker(), test_parse_fields_handles_empty_output(), test_parse_fields_happy_path(), test_parse_fields_ignores_unknown_marker_without_raising() (+1 more)

### Community 58 - "Reference: verified against the real codebase"
Cohesion: 0.15
Nodes (12): Global Constraints, Lightweight Review UX Redesign Implementation Plan, Reference: verified against the real codebase, Self-Review Notes, Task 1: Confidence tiering in the detection pipeline, Task 2: Unified review-span module, Task 3: Click-to-redact custom Streamlit component, Task 4: Simplify `review_checklist.py` to a two-input gate (+4 more)

### Community 59 - "assign_placeholders"
Cohesion: 0.29
Nodes (7): assign_placeholders(), Attach a stable placeholder to each unique entity. A type with exactly one…, assign_placeholders is analyze()'s last step — a silent drop here is permanent., test_assign_placeholders_keeps_confidence(), test_existing_placeholder_is_preserved(), test_multiple_values_get_numbered_placeholders(), test_single_value_gets_a_bare_placeholder()

### Community 60 - "carenotes_prompt.py"
Cohesion: 0.50
Nodes (3): build_messages(), Care note templates. Every template shares the same hard rule: the input is…, Return ``(system, user)`` for a template label and de-identified document.

### Community 61 - "Ward 7B Nursing Handover (doc04)"
Cohesion: 0.50
Nodes (4): Aiden Braithwaite, Ward 7B Nursing Handover (doc04), 'A. Surname' against full name in header, Labelled date fields

### Community 62 - "test_app_clinical_forms.py"
Cohesion: 0.29
Nodes (7): _form_draft_key(), _header_values_complete(), Pure-logic pieces of the clinical-form UI: the session-state key used to key a…, test_form_draft_key_differs_by_form_or_selection(), test_form_draft_key_is_stable_for_the_same_selection(), test_header_values_complete_requires_every_non_reason_field(), test_invalidate_form_export_drops_stale_resolved_values()

### Community 63 - "test_batch.py"
Cohesion: 0.11
Nodes (24): BatchError, list_folder(), RuntimeError, Return the supported documents in ``folder``, sorted by name. Non-recursive on…, Findings from the safety sweep, minus the ones the reviewer has cleared. A…, Write approved de-identified text to the output folder. Re-runs the safety…, Raised for input-folder and output-write problems., sweep() (+16 more)

### Community 64 - "test_clinical_form_templates.py"
Cohesion: 0.50
Nodes (3): parametrize, The three bundled APS templates load and match the structure this feature's…, test_bundled_template_shape()

### Community 73 - "residual_scan"
Cohesion: 0.20
Nodes (10): Re-scan ALREADY-REDACTED text for anything that still looks identifying. Runs…, residual_scan(), Placeholders are the point of the exercise, not leaks., A .txt file read off a Windows disk arrives with CRLF endings. NER tokenises…, test_crlf_and_lf_documents_behave_identically(), test_residual_scan_catches_a_leaked_name(), test_residual_scan_catches_a_leaked_structured_identifier(), test_residual_scan_does_not_flag_placeholders() (+2 more)

### Community 74 - "House-style exemplar retrieval — design"
Cohesion: 0.18
Nodes (10): `app.py`, Architecture, `core/clinical_forms.py`, Follow-ups (not blocking), House-style exemplar retrieval — design, New module `core/exemplars.py`, Privacy, Problem (+2 more)

### Community 76 - "render_draft"
Cohesion: 0.40
Nodes (6): _as_docx(), The de-identified draft, refinement, re-identification, and exports., Opt-in, local-only substitution of placeholders back to real values., Render generated text to a .docx in memory — nothing touches disk., render_draft(), render_reidentification()

### Community 77 - "Backend"
Cohesion: 0.50
Nodes (3): Backend, Protocol, One method wide: the seam a different provider would be swapped in at.

### Community 78 - "Document"
Cohesion: 0.32
Nodes (13): Document, One document's state for the whole review pass. Everything here except…, build_intake_notes(), build_referral_letter(), build_session_log(), build_treatment_review_source(), _grid_table(), _heading() (+5 more)

### Community 80 - "Cloud generation transport (`CloudBackend`) — design"
Cohesion: 0.20
Nodes (9): Architecture, Cloud generation transport (`CloudBackend`) — design, `core/backends.py`, Follow-ups (not blocking), New module `core/cloud_client.py`, Privacy properties (unchanged, inherited), Problem, Scope (+1 more)

### Community 81 - "reference_library.py"
Cohesion: 0.11
Nodes (34): add_file(), _all_chunks(), _bounded(), Chunk, _dir(), _files(), is_empty(), _paragraphs() (+26 more)

### Community 82 - "render_clinical_form_panel"
Cohesion: 0.15
Nodes (16): _draft_state(), _form_draft_state(), Option A. The only outbound request the app makes, on an explicit click., Option B. Ollama does the fetching; the request goes to loopback., Generate, refine, re-identify and export — for one approved document. Two…, Add clinic reference files (formulary, pathways, protocols) to a local library.…, Which backend will be used, and the fix if none is available., Shown instead of an empty panel when no model is available yet. An empty… (+8 more)

### Community 84 - "is_model_present"
Cohesion: 0.50
Nodes (4): is_model_present(), True if a usable model file is already on this computer. This is the marker…, Setup is one-time because the file itself is the state., test_model_presence_is_the_persisted_marker()

### Community 87 - "Lightweight review UX for de-identification — design"
Cohesion: 0.14
Nodes (13): 1. Confidence tiering (drives what gets a click at all), 2. One primary review view, not three, 3. The click-to-redact component, 4. Attestation & audit trail, 5. Crash-risk fixes, Architecture, Current state (for reference), Goals (+5 more)

### Community 88 - "test_deid_pipeline.py"
Cohesion: 0.05
Nodes (41): parametrize, Regression suite for the layered de-identification pipeline. Two guarantees,…, With REDACT_INPROSE_DATES False, a procedure date is clinical, not identity., DOB and admission/discharge dates carry identity, so they go., spaCy labels "ECG" and "NSTEMI" as organisations; the filter must drop them., With no spaCy model, layer 1 must still protect the document., Dr" as a standalone form would redact every "Dr" in the document., Form tokens are joined with \\s+, so a name split across lines still matches. (+33 more)

### Community 91 - "NoEgress"
Cohesion: 0.14
Nodes (10): NoEgress, Fails the test if anything opens a non-loopback socket. Loopback is allowed:…, Re-identification is pure Python — it must not phone anywhere., test_reidentification_opens_no_socket(), The load that used to hang on a captive portal must not exist., Reset the cache so the guard covers a genuine first load., The reported hang: no model, so something tries to download it., test_a_missing_model_fails_loudly_instead_of_fetching() (+2 more)

### Community 92 - "redact"
Cohesion: 0.14
Nodes (15): find_known_as(), find_spans(), _form_pattern(), Pattern, Pull a patient's preferred name out of a "Known as:" field, if present., Whitespace-tolerant, case-insensitive pattern for one surface form. Tokens are…, Find non-overlapping ``(start, end, placeholder)`` spans for every form. All…, Replace every surface form of every entity with its placeholder. Replacement… (+7 more)

### Community 93 - "Cardiology Discharge Summary (doc02)"
Cohesion: 0.22
Nodes (10): Community MH Discharge Letter (doc01), Mohammed Al-Rashid ('Mo'), Cardiology Discharge Summary (doc02), Mariam Aisha Rahman, Mental Health Act Assessment Record (doc10), Facility short forms, In-prose vs anchored dates, Initials-only patient reference (e.g. M.A.R.) (+2 more)

### Community 94 - "with_banner"
Cohesion: 0.40
Nodes (5): Prepend the review banner, without duplicating one already there., with_banner(), test_generated_output_keeps_the_review_banner(), test_every_draft_carries_the_review_banner(), test_the_banner_is_not_duplicated_on_refinement()

### Community 95 - "deidentify.py"
Cohesion: 0.08
Nodes (32): cache_resource, load_detection_engine(), Load the NER model once per session, not once per rerun. Streamlit re-runs the…, available_models(), _build_analyzer(), date_span_wanted(), engine_status(), get_analyzer() (+24 more)

### Community 97 - "README.md"
Cohesion: 0.22
Nodes (9): Margaret Elizabeth Chen ('Peggy'), Priya Venkataraman, Psychological Medicine Clinic Letter (doc06), CMHT Family Review Letter (doc07), Wei Chen, Crisis Team Contact Log (doc09), Tomasz Wisniewski, No real patient documents policy (+1 more)

### Community 98 - "load_documents"
Cohesion: 0.12
Nodes (20): analyze_document(), load_documents(), Extract text from uploads or paths. Returns ``(documents, errors)``. One…, Run the de-identification layers over one document, in place., FakeUpload, Stands in for a Streamlit UploadedFile., test_analyze_document_populates_state(), test_duplicate_filenames_are_reported() (+12 more)

### Community 99 - "structured_spans"
Cohesion: 0.12
Nodes (16): _header_footer_bounds(), _plausible_surname(), Character ranges of the document's opening and closing lines., True if the trailing token of an initial+surname reads like a real name.…, Layer 1: deterministic regex detections over ``text``., REDACT_INPROSE_DATES flag, structured_spans(), expand_org_variants (Layer 4 — variant expansion) (+8 more)

### Community 104 - "reidentify"
Cohesion: 0.18
Nodes (11): Outcome of a re-identification pass., Swap placeholders back to originals, repairing mangled tokens. Never raises on…, Swap placeholders back to their original values. Thin wrapper over…, reidentify(), reidentify_detailed(), ReidentifyResult, test_empty_map_is_a_no_op(), test_invented_placeholder_is_left_alone() (+3 more)

### Community 105 - "GP Referral Letter (doc05)"
Cohesion: 0.25
Nodes (8): Elspeth Mackenzie-Ford ('Ellie'), GP Referral Letter (doc05), Oluwaseun Adeyinka, Resource Centre Referral (doc08), Hyphenated surname pattern, 'Known as' alias pattern, Two label styles pattern, Shared case number 990214 reused across fictional patients

### Community 106 - "Per-field retrieval planner — design"
Cohesion: 0.17
Nodes (11): `app.py`, Architecture, `core/reference_library.py`, `core/retrieval_planner.py` (new), `core/text_search.py`, Decision, Follow-ups (not blocking), Per-field retrieval planner — design (+3 more)

### Community 111 - "Stress corpus"
Cohesion: 0.50
Nodes (4): Running it, Stress corpus, The answer key, What each document covers

### Community 116 - "stress_report.py"
Cohesion: 0.67
Nodes (3): main(), normalise(), Per-document pass/fail report for the stress corpus. python…

### Community 117 - "answer_key.json"
Cohesion: 0.67
Nodes (3): answer_key.json, must_preserve (answer key field), must_redact (answer key field)

### Community 122 - "conftest.py"
Cohesion: 0.15
Nodes (14): deid(), ner_available(), fixture, Shared pytest fixtures. The spaCy model load costs several seconds, so the…, The full pipeline's output for the fixture document., True when a spaCy model loaded — layer 2 tests skip without one., raw_text(), redacted() (+6 more)

### Community 123 - "extract_text"
Cohesion: 0.09
Nodes (33): Any, _extract_docx(), _extract_pdf(), extract_text(), _extract_txt(), IngestError, RuntimeError, Text extraction for uploaded documents (PDF / DOCX / TXT). Nothing here writes… (+25 more)

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
- **131 isolated node(s):** `Problem`, `Decision`, `Scope`, ``core/text_search.py``, ``core/reference_library.py`` (+126 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

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
- **Why does `deidentify()` connect `deidentify` to `test_app.py`, `test_generation_setup.py`, `add_manual_entity`, `analyze`, `core/__init__.py`, `test_stress_corpus.py`, `rebuild`, `test_deid_regressions.py`, `test_a_date_entity_never_spans_a_line_break`, `test_batch.py`, `residual_scan`, `test_deid_pipeline.py`, `test_a_patient_label_outranks_a_kinship_heading`, `NoEgress`, `redact`, `deidentify.py`, `load_documents`, `stress_report.py`, `conftest.py`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `render_review()` connect `Document` to `app.py`, `test_review_gate.py`, `highlight_review`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._