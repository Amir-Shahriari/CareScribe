# Graph Report - medgpt  (2026-09-01)

## Corpus Check
- 93 files · ~100,207 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1680 nodes · 3099 edges · 120 communities (104 shown, 16 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 50 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4e547124`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- residual_values
- clinical_forms.py
- deidentify
- _flag_values
- write_approved
- Reference: verified template structure
- template_ingest.py
- test_docx_roundtrip.py
- test_app.py
- load_protected_terms
- test_generation.py
- test_template_ingest.py
- Local clinical LLM fine-tune — design
- test_generation_setup.py
- reidentify_detailed
- test_mapping.py
- model_setup.py
- docx_redact.py
- backends.py
- fill_template
- carenotes.py
- get_form_spec
- test_cloud_client.py
- Clinic reference library — design
- deidentify.py
- Document
- generation_status
- mapping.py
- render_clinical_form_panel
- merge_spans
- refine_document
- test_app_clinical_forms.py
- Architecture
- test_stress_corpus.py
- combine_sources
- assert_deidentified
- query_tokens
- Cardiology Discharge Summary (doc02)
- make_icon.py
- add_manual_entity
- exemplars.py
- test_deid_regressions.py
- ollama_client.py
- README.md
- normalise_action
- canonical_person_key
- highlight_review
- test_review_gate.py
- candidate_residuals
- resolve_placeholder
- generate_form_document
- Installing CareScribe
- stress_report.py
- Clinic-uploaded clinical form templates — design
- render_draft
- Report templates (SOAP / GP letter / discharge / custom)
- Outpatient Respiratory Clinic Letter (doc03)
- app.py
- Reference: verified against the real codebase
- assign_placeholders
- carenotes_prompt.py
- Ward 7B Nursing Handover (doc04)
- select_backend
- conftest.py
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
- parse_fields
- desktop.py
- make_sample_docs.py
- Cloud generation transport (`CloudBackend`) — design
- test_reference_library.py
- GP Referral Letter (doc05)
- GLiNER Deliberately Uninstalled
- is_model_present
- Sample Source Documents README
- Recurring fictional staff roster (e.g. A. Whitfield) across documents
- Lightweight review UX for de-identification — design
- test_deid_pipeline.py
- test_desktop_packaging.py
- review_spans
- NoEgress
- analyze
- applog.py
- rebuild
- _span_is_plausible
- batch.py
- run_app.py
- test_batch.py
- structured_spans
- BM25
- <id> — <title>
- OllamaBackend
- wipe_phi
- BackendError
- core/__init__.py
- Per-field retrieval planner — design
- components/__init__.py
- The desktop app (PyInstaller packaging)
- Stress corpus
- answer_key.json
- test_a_date_entity_never_spans_a_line_break
- residual_scan
- write_approved_docx
- AGENTS.md — rules for automated coding agents in this repo
- Task board
- _RecordingBackend
- test_the_corpus_and_its_answer_key_agree
- reference_library.py
- extract_text

## God Nodes (most connected - your core abstractions)
1. `deidentify()` - 66 edges
2. `get_form_spec()` - 44 edges
3. `Document` - 38 edges
4. `residual_scan()` - 26 edges
5. `generate_document()` - 25 edges
6. `generation_status()` - 23 edges
7. `load_documents()` - 20 edges
8. `write_approved()` - 20 edges
9. `fill_template()` - 19 edges
10. `structured_spans()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `Stable per-entity placeholder scheme` --semantically_similar_to--> `build_prompt()`  [INFERRED] [semantically similar]
  README.md → carescribe/core/clinical_forms.py
- `presidio-analyzer` --references--> `_build_analyzer()`  [INFERRED]
  requirements.txt → carescribe/core/deidentify.py
- `spaCy Model Fallback Chain` --rationale_for--> `_build_analyzer()`  [INFERRED]
  requirements.txt → carescribe/core/deidentify.py
- `Section-path field key slug scheme` --rationale_for--> `slugify()`  [EXTRACTED]
  docs/superpowers/specs/2026-08-13-clinical-forms-design.md → carescribe/core/clinical_forms.py
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

## Communities (120 total, 16 thin omitted)

### Community 0 - "residual_values"
Cohesion: 0.25
Nodes (8): find_spans(), _form_pattern(), Pattern, Whitespace-tolerant, case-insensitive pattern for one surface form. Tokens are…, Find non-overlapping ``(start, end, placeholder)`` spans for every form. All…, Return surface forms that still appear in ``text`` after redaction. Used by the…, residual_values(), test_residual_values_reports_what_did_not_replace()

### Community 1 - "clinical_forms.py"
Cohesion: 0.21
Nodes (18): _biopsychosocial_spec(), build_prompt(), FormField, FormSpec, _grid_fields(), HeaderField, _paragraph_texts(), Fill the three bundled APS clinical form templates from approved, de-identified… (+10 more)

### Community 2 - "deidentify"
Cohesion: 0.12
Nodes (30): deidentify(), Run the full local pipeline over one document. CPU-only and offline: no model…, parametrize, Regression suite for the round-2 leaks (A1-A9). The corpus tests in…, Flattening the break made one span of the org and the next line's town., The dangerous direction: this used to fail open, leaking the whole name., Brother: David Chen\\nWei Chen" was one span covering two people., A sibling listed above must not drag the patient into being a relative. (+22 more)

### Community 3 - "_flag_values"
Cohesion: 0.40
Nodes (6): _flag_values(), parametrize, test_a_planted_residual_is_flagged(), test_clinical_and_legal_terms_are_not_flagged(), test_each_flag_carries_its_kind_and_reason(), test_the_sidecar_contains_no_identifier_value()

### Community 4 - "write_approved"
Cohesion: 0.12
Nodes (19): analyze_document(), Run the de-identification layers over one document, in place., Write approved de-identified text to the output folder. Re-runs the safety…, write_approved(), The guarantee must not depend on the UI having run the sweep first., test_a_dismissed_finding_lets_the_write_through(), test_analyze_document_populates_state(), test_write_approved_writes_deidentified_text() (+11 more)

### Community 5 - "Reference: verified template structure"
Cohesion: 0.10
Nodes (20): carescribe/core/clinical_forms.py (module), Refine prompt (clinical form, marker-preserving), Refine prompt (free-form draft revision), Clinical Form Generation (APS Templates) Implementation Plan, Global Constraints, Reference: verified template structure, Self-Review Notes (for the implementer), Task 10: End-to-end generation glue (`generate_form_document`, `refine_form_document`, `render_preview`) (+12 more)

### Community 6 - "template_ingest.py"
Cohesion: 0.13
Nodes (29): ClinicalFormError, RuntimeError, Raised when a clinical form can't be built or filled., slugify(), delete_template(), _find_grids(), _infer_header(), _is_blank_row() (+21 more)

### Community 7 - "test_docx_roundtrip.py"
Cohesion: 0.08
Nodes (32): approved_map(), document_has_text_boxes(), The reviewer-approved ``{literal: placeholder}`` map for the Word pass. This is…, True if a .docx holds text this redaction pass cannot reach., extract_text(), has_unreachable_text(), True if the document holds text this module cannot reach. Text boxes,…, Flatten a docx to text (body + tables + headers/footers) for a residual scan. (+24 more)

### Community 8 - "test_app.py"
Cohesion: 0.10
Nodes (39): AppTest, analysed_batch(), _clean_auto_doc(), data_editors(), loaded_batch(), _NullBackend, UI checks for the batch review app via Streamlit's AppTest. No server of any…, After the read-and-confirmed tick, a clean auto-confidence document has nothing… (+31 more)

### Community 9 - "load_protected_terms"
Cohesion: 0.29
Nodes (8): _build_protected_pattern(), load_protected_terms(), Path, Pattern, Read the editable allow-list. Blank lines and ``#`` comments are ignored., Re-read the allow-list from disk (the file is meant to be edited by hand)., reload_protected_terms(), test_the_allow_list_is_an_editable_file()

### Community 10 - "test_generation.py"
Cohesion: 0.09
Nodes (25): finalise(), Re-identify a draft locally and refuse to hand back a leaky document. Returns…, check_placeholder_integrity(), Issue, One placeholder problem found in a generated draft., Compare a draft's bracketed tokens against the placeholders it should use. An…, Local re-identification of a generated draft. Returns ``(text, unresolved)``.…, reidentify_document() (+17 more)

### Community 11 - "test_template_ingest.py"
Cohesion: 0.13
Nodes (21): available_forms(), (form_id, title) pairs — bundled forms first, then clinic-uploaded ones., fill_parsed_template(), Fill an in-memory copy of ``original_docx`` from ``spec``'s anchors. A thin…, _anchors(), _build_synthetic(), _merge_full_width(), fixture (+13 more)

### Community 12 - "Local clinical LLM fine-tune — design"
Cohesion: 0.06
Nodes (30): 10. Workstream E — integration, 11. What needs a human / external resource, 12. Milestones (testable deliverables), 13. Testing strategy, 1. Goal, 2. Constraints inherited from CareScribe, 3. Approach (selected), 4. Base model (+22 more)

### Community 13 - "test_generation_setup.py"
Cohesion: 0.07
Nodes (18): _cloud_off(), _fresh_generation_status_cache(), mapping_module(), fixture, First-run generation setup: never an empty panel, and the egress line held. The…, The one outbound path must not be reachable from the de-id flow., A captive portal returns HTML with a plausible size., generation_status() is now @st.cache_data(ttl=5) — a process-global cache keyed… (+10 more)

### Community 14 - "reidentify_detailed"
Cohesion: 0.33
Nodes (6): Outcome of a re-identification pass., Swap placeholders back to originals, repairing mangled tokens. Never raises on…, reidentify_detailed(), ReidentifyResult, test_invented_placeholder_is_left_alone(), test_mangled_placeholder_is_repaired()

### Community 15 - "test_mapping.py"
Cohesion: 0.13
Nodes (18): dedupe_entities(), Drop blank and duplicate entities, keeping first-seen order and casing.…, Swap placeholders back to their original values. Thin wrapper over…, reidentify(), parametrize, Mapping-layer checks: type normalisation, surface forms, and re-identification.…, If ANY occurrence of a value was low-confidence, the whole entity is., test_dedupe_carries_the_keep_action() (+10 more)

### Community 16 - "model_setup.py"
Cohesion: 0.16
Nodes (18): clear_partial_download(), download_model(), _free_bytes(), model_destination(), ModelSetupError, Progress, pull_ollama_model(), Path (+10 more)

### Community 17 - "docx_redact.py"
Cohesion: 0.23
Nodes (13): apply_redactions(), _delete_prefix(), _iter_groups(), _iter_paragraphs(), _norm(), Structure-preserving .docx redaction. apply_redactions(path_in, path_out,…, Redact a literal split across a paragraph boundary (wrapped name)., Delete the leading text of a paragraph matching normalized_prefix (ws-… (+5 more)

### Community 18 - "backends.py"
Cohesion: 0.14
Nodes (20): privacy_indicator(), A persistent, honest statement of where data goes. It must change when cloud…, cloud_enabled(), cloud_key_present(), cloud_provider(), CloudBackend, describe_backends(), Generation backends, layered so the app works with nothing installed. Selection… (+12 more)

### Community 19 - "fill_template"
Cohesion: 0.15
Nodes (20): _clear_cell(), _dedupe_row(), _fill_cell(), _fill_cell_after_label(), _fill_header_cell(), fill_template(), Remove every paragraph after the first, and every run in the first, leaving one…, Overwrite a dedicated value cell (label lives in a different cell). (+12 more)

### Community 20 - "carenotes.py"
Cohesion: 0.16
Nodes (15): assert_no_residual_identifiers(), CareNoteError, load_prompt(), RuntimeError, Care note generation — local, on approved de-identified text only. The contract…, Build the user prompt for one template with the source text embedded., Refuse to send text the residual sweep still flags. :func:`assert_deidentified`…, Raised when care note generation can't proceed. (+7 more)

### Community 21 - "get_form_spec"
Cohesion: 0.17
Nodes (21): get_form_spec(), plan(), _load(), Generic table-row classification: which rows are fields, which are section…, test_biopsychosocial_spec_field_count_and_grid(), test_no_field_key_collides_within_a_spec(), test_session_notes_field_walk_finds_nine_fields(), test_session_notes_signature_row_is_excluded() (+13 more)

### Community 22 - "test_cloud_client.py"
Cohesion: 0.10
Nodes (25): CloudError, _config(), _post(), RuntimeError, Transport for the optional cloud generation backend. Reached only when a…, Yield the payload of each ``data:`` line in an SSE stream., Stream a completion from the configured cloud provider, yielding text. Raises…, A recoverable problem talking to the configured cloud provider. (+17 more)

### Community 23 - "Clinic reference library — design"
Cohesion: 0.17
Nodes (11): `app.py`, Architecture, Clinic reference library — design, Decision, Follow-ups (not blocking), New `core/reference_library.py`, Privacy / safety, Problem (+3 more)

### Community 24 - "deidentify.py"
Cohesion: 0.08
Nodes (32): cache_resource, load_detection_engine(), Load the NER model once per session, not once per rerun. Streamlit re-runs the…, available_models(), _build_analyzer(), date_span_wanted(), engine_status(), get_analyzer() (+24 more)

### Community 25 - "Document"
Cohesion: 0.16
Nodes (22): document_flags(), entity_confirmed(), entity_frame(), flag_dismissals(), Re-derive the preview and map from an edited entity list., Redact the original .docx using the map the reviewer just approved. Detection…, Offer the redacted .docx, but only once it has cleared the sweep., Candidate residuals for this document, recomputed from current text. (+14 more)

### Community 26 - "generation_status"
Cohesion: 0.10
Nodes (23): cache_data, generation_status(), _llama_runtime_available(), missing_reason(), Is generation usable right now, and if not, what should the user do? Kept…, One plain sentence on why generation is not available yet., Which generation backends are usable at this moment., Which backend would actually be used, matching the backend ladder. (+15 more)

### Community 27 - "mapping.py"
Cohesion: 0.15
Nodes (17): expand_facility_variants(), expand_name_variants(), _initial_letters(), name_core(), normalise_type(), In-memory PII <-> placeholder mapping. This module is deliberately pure: it…, Coerce a model-supplied type string onto the canonical list., Split a name into its parts with any leading honorific removed. "Mrs Margaret… (+9 more)

### Community 28 - "render_clinical_form_panel"
Cohesion: 0.13
Nodes (18): _draft_state(), _form_draft_state(), Which backend will be used, and the fix if none is available., Shown instead of an empty panel when no model is available yet. An empty…, Option A. The only outbound request the app makes, on an explicit click., Option B. Ollama does the fetching; the request goes to loopback., Generate, refine, re-identify and export — for one approved document. Two…, Let a clinic add its own table-based .docx form to the selector. Parsing and… (+10 more)

### Community 29 - "merge_spans"
Cohesion: 0.14
Nodes (14): _collapse_facility_subsets(), _collapse_person_identities(), _collapse_person_subsets(), merge_spans(), protected_ranges(), Shrink a NER span to its identifying core. Drops leading titles ("Sister Fiona…, Drop a person entity whose name is contained in a longer one. NER returns…, True for a person row whose role is known (patient / relative / clinician). (+6 more)

### Community 30 - "refine_document"
Cohesion: 0.20
Nodes (11): Revise an existing draft against a follow-up instruction. Operates on the same…, The shared preamble — role, anti-fabrication rules, placeholder rules., refine_document(), system_prompt(), test_generate_document_default_behaviour_is_unchanged(), test_refine_document_accepts_a_system_and_refine_prompt_override(), test_refine_document_default_behaviour_is_unchanged(), test_refinement_carries_the_running_history() (+3 more)

### Community 31 - "test_app_clinical_forms.py"
Cohesion: 0.29
Nodes (7): _form_draft_key(), _header_values_complete(), Pure-logic pieces of the clinical-form UI: the session-state key used to key a…, test_form_draft_key_differs_by_form_or_selection(), test_form_draft_key_is_stable_for_the_same_selection(), test_header_values_complete_requires_every_non_reason_field(), test_invalidate_form_export_drops_stale_resolved_values()

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
Cohesion: 0.12
Nodes (17): assert_deidentified(), Backend, CloudBackend (unwired seam), Protocol, Refuse to send anything carrying a value from the identity mapping. A cheap,…, One method wide: the seam a different provider would be swapped in at., System prompt (anti-fabrication rules), Optional cloud generation path (off by default) (+9 more)

### Community 36 - "query_tokens"
Cohesion: 0.20
Nodes (10): Protocol, Per-field retrieval planning for clinical-form generation. Roadmap item E…, Deterministic planner driven by a keyword taxonomy over field labels., RetrievalPlan, RetrievalPlanner, RuleBasedPlanner, query_tokens(), Okapi BM25 over a small in-memory document set — standard library only. Shared… (+2 more)

### Community 37 - "Cardiology Discharge Summary (doc02)"
Cohesion: 0.22
Nodes (10): Community MH Discharge Letter (doc01), Mohammed Al-Rashid ('Mo'), Cardiology Discharge Summary (doc02), Mariam Aisha Rahman, Mental Health Act Assessment Record (doc10), Facility short forms, In-prose vs anchored dates, Initials-only patient reference (e.g. M.A.R.) (+2 more)

### Community 38 - "make_icon.py"
Cohesion: 0.29
Nodes (12): Image, _load_font(), main(), Path, Generate CareScribe's placeholder icon. A real icon is a design job; this…, The first usable bold face, or ``None`` if none of them load., A rounded square with "CS" centred on it., macOS only. Silently skipped elsewhere — the .app is built on a Mac. (+4 more)

### Community 39 - "add_manual_entity"
Cohesion: 0.15
Nodes (13): add_manual_entity(), DeidentificationError, DeidResult, RuntimeError, Add an identifier the tools missed and immediately re-redact. The new value…, Raised when de-identification can't run at all., Everything the de-identification stage produces for one document., A value the layers missed is expanded like a detected one. (+5 more)

### Community 40 - "exemplars.py"
Cohesion: 0.14
Nodes (25): add_exemplar(), count(), _dir(), _load(), _path(), Path, House-style exemplar retrieval for clinical-form generation. A clinic…, Top-``k`` stored values for ``field_key``, ranked by BM25 against ``query``. (+17 more)

### Community 41 - "test_deid_regressions.py"
Cohesion: 0.09
Nodes (29): _mrn_values(), parametrize, Regression suite for the five leaks found on a second, non-fixture document.…, A two-part capitalised phrase mid-document is not a letterhead., Layer 1 must carry this on its own — NER catching it is luck, not a guarantee., M.E.C.\\nFollow-up" must not become the name "M.E.C. Follow"., Regardless of REDACT_INPROSE_DATES, which stays False by default., The label shapes document #2 actually used, including the parenthetical. (+21 more)

### Community 42 - "ollama_client.py"
Cohesion: 0.14
Nodes (19): default_model(), generate(), is_up(), list_models(), missing_model_message(), OllamaError, RuntimeError, Local Ollama client — pinned to the loopback interface. Generation is the first… (+11 more)

### Community 43 - "README.md"
Cohesion: 0.22
Nodes (9): Margaret Elizabeth Chen ('Peggy'), Priya Venkataraman, Psychological Medicine Clinic Letter (doc06), CMHT Family Review Letter (doc07), Wei Chen, Crisis Team Contact Log (doc09), Tomasz Wisniewski, No real patient documents policy (+1 more)

### Community 44 - "normalise_action"
Cohesion: 0.40
Nodes (5): build_map(), normalise_action(), Build the placeholder -> original-value map used for re-identification. If two…, Coerce a table cell to :data:`REDACT` or :data:`KEEP`. Defaults to redact., test_kept_rows_are_absent_from_the_map()

### Community 45 - "canonical_person_key"
Cohesion: 0.25
Nodes (8): canonical_person_key(), keys_are_compatible(), A stable identity key for one person: full given name plus surname. This…, True if two canonical keys can denote the same person. Exact match, or one side…, test_canonical_key_separates_two_people_with_one_surname(), test_canonical_key_unifies_the_forms_of_one_person(), test_an_initial_can_stand_in_for_a_given_name(), test_one_person_keeps_one_identity_key()

### Community 46 - "highlight_review"
Cohesion: 0.24
Nodes (9): highlight_review(), Click-to-redact highlighted text. Renders already-redacted (or already-flagged)…, Render ``html`` and return the ``data-span-id`` of the last click. Returns…, _frontend_path(), Path, Offline-first: nothing in this file may fetch from a CDN., test_frontend_file_exists(), test_frontend_has_no_external_script_or_link_tags() (+1 more)

### Community 47 - "test_review_gate.py"
Cohesion: 0.11
Nodes (18): blocking_reason(), The approval gate. Only the **authoritative safety sweep** blocks approval. A…, Why Approve is disabled, in one short line. Empty string means it isn't.…, fixture, The reviewer gate: candidate highlighting, the adaptive checklist, and the no-…, Low-confidence redactions are already in place; the permissive flags are…, The streamlined gate: a permissive flag the reviewer left untouched does not…, The real test: nothing the corpus calls an identifier may appear. (+10 more)

### Community 48 - "candidate_residuals"
Cohesion: 0.12
Nodes (19): candidate_residuals(), Flag, _is_common(), outstanding(), _placeholder_ranges(), Residual-candidate highlighter — where the reviewer's eye should go first. This…, One span worth a second look, with its offsets in the redacted text., Identity for dismissal — per value, so one decision covers repeats. (+11 more)

### Community 49 - "resolve_placeholder"
Cohesion: 0.29
Nodes (7): _edit_distance(), Levenshtein distance, short-circuiting once it exceeds ``cap``., Map a possibly-corrupted placeholder onto a known one. Returns the exact token…, resolve_placeholder(), Guessing between [MRN_1] and [MRN_2] would attach the wrong identity., test_ambiguous_placeholder_is_refused_not_guessed(), test_edit_distance_caps_out()

### Community 50 - "generate_form_document"
Cohesion: 0.22
Nodes (10): generate_form_document(), Human-readable rendering for display only — the marker text in ``draft_state``…, render_preview(), Captures exactly what generation handed the model — mirrors the fixture in…, RecordingBackend, test_generate_form_document_refuses_a_real_identifier(), test_generate_form_document_sends_the_field_marker_prompt(), test_refine_form_document_preserves_markers_instruction() (+2 more)

### Community 51 - "Installing CareScribe"
Cohesion: 0.22
Nodes (8): Before you start, First launch, If it will not start, Installing CareScribe, macOS, Updating, Where your files go, Windows

### Community 52 - "stress_report.py"
Cohesion: 0.67
Nodes (3): main(), normalise(), Per-document pass/fail report for the stress corpus. python…

### Community 53 - "Clinic-uploaded clinical form templates — design"
Cohesion: 0.18
Nodes (10): Architecture, Clinic-uploaded clinical form templates — design, Follow-ups (not blocking), New module `core/template_ingest.py`, Persistence, Problem, Registry integration (`core/clinical_forms.py`), Scope (+2 more)

### Community 54 - "render_draft"
Cohesion: 0.40
Nodes (6): _as_docx(), The de-identified draft, refinement, re-identification, and exports., Opt-in, local-only substitution of placeholders back to real values., Render generated text to a .docx in memory — nothing touches disk., render_draft(), render_reidentification()

### Community 55 - "Report templates (SOAP / GP letter / discharge / custom)"
Cohesion: 0.40
Nodes (5): SOAP care note prompt template, GP clinic letter prompt template, Custom (clinician house format) prompt template, Discharge summary prompt template, Report templates (SOAP / GP letter / discharge / custom)

### Community 56 - "Outpatient Respiratory Clinic Letter (doc03)"
Cohesion: 0.40
Nodes (5): Ngozi Okafor, Outpatient Respiratory Clinic Letter (doc03), Attendee list pattern, Header town + county pattern, Record-number label shapes (three variants)

### Community 57 - "app.py"
Cohesion: 0.18
Nodes (19): current(), documents(), ingest_sources(), _inject_app_css(), main(), CareScribe — local, privacy-preserving de-identification and review. Run with:…, A missing model must stop loudly, never fall back to fetching one., CareScribe's visual identity, applied once per rerun. Streamlit's theming only… (+11 more)

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

### Community 62 - "select_backend"
Cohesion: 0.12
Nodes (21): _invalidate_form_export(), Drop any previously re-identified/exportable content — called whenever the…, A concrete "it works", rather than asking the clinician to trust a flag., Render a stream token by token so a slow local model looks alive., First-pass generation. The model receives de-identified text only., Follow-up instructions, on de-identified text only., Verbatim reference passages, retrieved per field at the granularity the planner…, render_form_draft() (+13 more)

### Community 63 - "conftest.py"
Cohesion: 0.15
Nodes (14): deid(), ner_available(), fixture, Shared pytest fixtures. The spaCy model load costs several seconds, so the…, The full pipeline's output for the fixture document., True when a spaCy model loaded — layer 2 tests skip without one., raw_text(), redacted() (+6 more)

### Community 64 - "test_clinical_form_templates.py"
Cohesion: 0.50
Nodes (3): parametrize, The three bundled APS templates load and match the structure this feature's…, test_bundled_template_shape()

### Community 73 - "generate_document"
Cohesion: 0.12
Nodes (20): generate_document(), Stream a drafted document from approved de-identified text. ``phi_values`` is…, parametrize, `acknowledged` carries the residual-sweep findings approval accepted (a town…, `phi_values` exists to assert absence, never to be forwarded., Spot-check the instruction is honoured, with the model mocked., Captures exactly what generation handed the model., A bug upstream must crash here, not send quietly. (+12 more)

### Community 74 - "House-style exemplar retrieval — design"
Cohesion: 0.18
Nodes (10): `app.py`, Architecture, `core/clinical_forms.py`, Follow-ups (not blocking), House-style exemplar retrieval — design, New module `core/exemplars.py`, Privacy, Problem (+2 more)

### Community 76 - "parse_fields"
Cohesion: 0.44
Nodes (9): parse_fields(), Turn the model's marker-delimited output into ``{field_key: text}``. Any field…, _spec(), test_parse_fields_defaults_missing_field_to_not_documented(), test_parse_fields_first_occurrence_wins_on_duplicate_marker(), test_parse_fields_handles_empty_output(), test_parse_fields_happy_path(), test_parse_fields_ignores_unknown_marker_without_raising() (+1 more)

### Community 77 - "desktop.py"
Cohesion: 0.14
Nodes (24): app_data_dir(), bundle_root(), ensure_dirs(), find_local_model(), is_frozen(), models_dir(), output_dir(), Path (+16 more)

### Community 78 - "make_sample_docs.py"
Cohesion: 0.20
Nodes (18): build_intake_notes(), build_referral_letter(), build_session_log(), build_treatment_review_source(), _grid_table(), _heading(), _para(), Generate synthetic, complex .docx source documents for manually testing the… (+10 more)

### Community 80 - "Cloud generation transport (`CloudBackend`) — design"
Cohesion: 0.20
Nodes (9): Architecture, Cloud generation transport (`CloudBackend`) — design, `core/backends.py`, Follow-ups (not blocking), New module `core/cloud_client.py`, Privacy properties (unchanged, inherited), Problem, Scope (+1 more)

### Community 81 - "test_reference_library.py"
Cohesion: 0.16
Nodes (22): add_file(), _all_chunks(), is_empty(), ``(filename, paragraph_count)`` per loaded reference file., Top-``k`` reference passages for ``query`` at ``granularity``. BM25, ``score >…, Store an uploaded reference file. Returns the stored filename., search(), sources() (+14 more)

### Community 82 - "GP Referral Letter (doc05)"
Cohesion: 0.25
Nodes (8): Elspeth Mackenzie-Ford ('Ellie'), GP Referral Letter (doc05), Oluwaseun Adeyinka, Resource Centre Referral (doc08), Hyphenated surname pattern, 'Known as' alias pattern, Two label styles pattern, Shared case number 990214 reused across fictional patients

### Community 84 - "is_model_present"
Cohesion: 0.50
Nodes (4): is_model_present(), True if a usable model file is already on this computer. This is the marker…, Setup is one-time because the file itself is the state., test_model_presence_is_the_persisted_marker()

### Community 87 - "Lightweight review UX for de-identification — design"
Cohesion: 0.14
Nodes (13): 1. Confidence tiering (drives what gets a click at all), 2. One primary review view, not three, 3. The click-to-redact component, 4. Attestation & audit trail, 5. Crash-risk fixes, Architecture, Current state (for reference), Goals (+5 more)

### Community 88 - "test_deid_pipeline.py"
Cohesion: 0.05
Nodes (41): parametrize, Regression suite for the layered de-identification pipeline. Two guarantees,…, With REDACT_INPROSE_DATES False, a procedure date is clinical, not identity., DOB and admission/discharge dates carry identity, so they go., spaCy labels "ECG" and "NSTEMI" as organisations; the filter must drop them., With no spaCy model, layer 1 must still protect the document., Dr" as a standalone form would redact every "Dr" in the document., Form tokens are joined with \\s+, so a name split across lines still matches. (+33 more)

### Community 89 - "test_desktop_packaging.py"
Cohesion: 0.11
Nodes (15): available_ram_gb(), ram_verdict(), Total system RAM in GB, or 0.0 if it cannot be determined., Whether this machine can run the bundled local model. Returns a verdict rather…, _cloud_off(), fixture, The packaging invariants: what the desktop app may and may not do. Packaging is…, No key may be committed, defaulted, or written anywhere. (+7 more)

### Community 90 - "review_spans"
Cohesion: 0.32
Nodes (12): Every clickable span in ``redacted_text``, in reading order. ``confirmed`` is…, review_spans(), _entity(), action=Keep means the reviewer already decided — nothing to click on the…, test_a_confirmed_entity_produces_no_span(), test_a_kept_entity_produces_no_entity_span(), test_auto_confidence_entities_produce_no_span(), test_dismissed_residual_flags_are_excluded() (+4 more)

### Community 91 - "NoEgress"
Cohesion: 0.14
Nodes (10): NoEgress, Fails the test if anything opens a non-loopback socket. Loopback is allowed:…, Re-identification is pure Python — it must not phone anywhere., test_reidentification_opens_no_socket(), The load that used to hang on a captive portal must not exist., Reset the cache so the guard covers a genuine first load., The reported hang: no model, so something tries to download it., test_a_missing_model_fails_loudly_instead_of_fetching() (+2 more)

### Community 92 - "analyze"
Cohesion: 0.10
Nodes (22): analyze(), flatten_lines(), gliner_spans(), ner_spans(), Layer 2: Presidio/spaCy detections, mapped onto CareScribe entity types.…, Layer 3: GLiNER detections, or an empty list when it isn't installed., Run every enabled layer over ``text`` and return reviewable entities. Each…, One detection, in character offsets over the source text. (+14 more)

### Community 93 - "applog.py"
Cohesion: 0.15
Nodes (18): BaseException, ensure_engine_ready(), Load the model at startup, behind a visible spinner. Deliberately not lazy. If…, The last line of defence: a calm message instead of a stack trace. A clinician…, render_unexpected_error(), exception(), get_logger(), log() (+10 more)

### Community 94 - "rebuild"
Cohesion: 0.22
Nodes (10): Re-derive redacted text and the PHI map from a reviewer-edited table. Called…, rebuild(), find_known_as(), Pull a patient's preferred name out of a "Known as:" field, if present., Replace every surface form of every entity with its placeholder. Replacement…, redact(), test_longest_match_wins_on_overlap(), test_matcher_does_not_fire_inside_a_longer_word() (+2 more)

### Community 95 - "_span_is_plausible"
Cohesion: 0.13
Nodes (17): classify_person(), _is_acronym(), _is_labelled_date_field(), _is_staff_context(), _line_bounds(), _location_is_address(), _looks_clinical(), True for a short all-caps token like "ECG" or "LS9" — never a name here. (+9 more)

### Community 96 - "batch.py"
Cohesion: 0.15
Nodes (19): approved_docx_path(), approved_path(), _default_output_dir(), Path, Batch input and approved-output handling. The single module in CareScribe that…, Reduce a filename to a safe output stem — no paths, no surprises., Where the approved de-identified text for ``name`` will be written., The raw bytes behind an upload or a path, without copying it to disk. (+11 more)

### Community 97 - "run_app.py"
Cohesion: 0.16
Nodes (17): Popen, close_splash(), _fatal(), free_port(), main(), _no_window_kwargs(), CareScribe desktop launcher — the app's entry point. Starts the Streamlit…, Dismiss the bootloader splash, if this is a frozen build that has one.… (+9 more)

### Community 98 - "test_batch.py"
Cohesion: 0.11
Nodes (24): list_folder(), load_documents(), Return the supported documents in ``folder``, sorted by name. Non-recursive on…, Extract text from uploads or paths. Returns ``(documents, errors)``. One…, Findings from the safety sweep, minus the ones the reviewer has cleared. A…, sweep(), FakeUpload, parametrize (+16 more)

### Community 99 - "structured_spans"
Cohesion: 0.12
Nodes (16): _header_footer_bounds(), _plausible_surname(), Character ranges of the document's opening and closing lines., True if the trailing token of an initial+surname reads like a real name.…, Layer 1: deterministic regex detections over ``text``., REDACT_INPROSE_DATES flag, structured_spans(), expand_org_variants (Layer 4 — variant expansion) (+8 more)

### Community 100 - "BM25"
Cohesion: 0.18
Nodes (9): ExemplarError, RuntimeError, Raised when an exemplar cannot be stored — e.g. it still holds an identifier., RuntimeError, Raised when a reference file cannot be stored., ReferenceError, BM25, Okapi BM25. ``documents`` is a list of token lists. (+1 more)

### Community 101 - "<id> — <title>"
Cohesion: 0.29
Nodes (6): Acceptance criteria, Do NOT touch, Files in scope, Goal, <id> — <title>, Notes

### Community 102 - "OllamaBackend"
Cohesion: 0.14
Nodes (12): generate_care_note(), OllamaBackend, Prepend the review banner, without duplicating one already there., Draft a care note from ALREADY DE-IDENTIFIED text, returning it whole. The…, Local generation through the loopback-pinned Ollama daemon., with_banner(), core/model_setup.py (model download, isolated), Generation backend selection order (Ollama > built-in GGUF > Cloud) (+4 more)

### Community 103 - "wipe_phi"
Cohesion: 0.67
Nodes (4): PHI_KEYS (session-state PHI registry), Drop every document, identifier table, and identity map from memory., wipe_phi(), Bug: form_drafts never registered with PHI_KEYS/wipe_phi

### Community 104 - "BackendError"
Cohesion: 0.19
Nodes (8): BackendError, LocalGGUFBackend, RuntimeError, Raised when a backend cannot be used, with the fix in the message., CPU-only generation from a bundled GGUF via ``llama-cpp-python``. The model is…, True if the runtime and a model file are both present., It fabricates otherwise — measured, not assumed., test_the_local_model_stays_pinned_at_temperature_zero()

### Community 105 - "core/__init__.py"
Cohesion: 0.24
Nodes (8): _review_span_style(), Core logic: Ollama access, ingestion, de-identification, care notes, PHI…, _entity_spans(), Unifies the two things a reviewer might still need to act on in one document's…, One clickable span in a document's redacted text., Placeholder occurrences for low-confidence, not-yet-confirmed entities., _residual_spans(), ReviewSpan

### Community 106 - "Per-field retrieval planner — design"
Cohesion: 0.17
Nodes (11): `app.py`, Architecture, `core/reference_library.py`, `core/retrieval_planner.py` (new), `core/text_search.py`, Decision, Follow-ups (not blocking), Per-field retrieval planner — design (+3 more)

### Community 108 - "The desktop app (PyInstaller packaging)"
Cohesion: 0.25
Nodes (8): packaging/build_macos.sh, packaging/build_windows.ps1, packaging/carescribe.iss (Inno Setup script), packaging/make_icon.py, The desktop app (PyInstaller packaging), run_app.py entry point, Path A — you have the built app, Path B — building from source

### Community 109 - "Stress corpus"
Cohesion: 0.50
Nodes (4): Running it, Stress corpus, The answer key, What each document covers

### Community 110 - "answer_key.json"
Cohesion: 0.67
Nodes (3): answer_key.json, must_preserve (answer key field), must_redact (answer key field)

### Community 112 - "residual_scan"
Cohesion: 0.20
Nodes (10): Re-scan ALREADY-REDACTED text for anything that still looks identifying. Runs…, residual_scan(), Placeholders are the point of the exercise, not leaks., A .txt file read off a Windows disk arrives with CRLF endings. NER tokenises…, test_crlf_and_lf_documents_behave_identically(), test_residual_scan_catches_a_leaked_name(), test_residual_scan_catches_a_leaked_structured_identifier(), test_residual_scan_does_not_flag_placeholders() (+2 more)

### Community 113 - "write_approved_docx"
Cohesion: 0.22
Nodes (9): BatchError, RuntimeError, Redact the original .docx into the output folder, structure preserved. The same…, Raised for input-folder and output-write problems., write_approved_docx(), The Word path must clear the same bar as the text path., test_write_approved_docx_needs_the_original(), test_write_approved_docx_refuses_when_the_map_misses_an_identifier() (+1 more)

### Community 114 - "AGENTS.md — rules for automated coding agents in this repo"
Cohesion: 0.40
Nodes (4): AGENTS.md — rules for automated coding agents in this repo, Do, Never, Task spec shape

### Community 121 - "reference_library.py"
Cohesion: 0.23
Nodes (12): _bounded(), Chunk, _dir(), _files(), _paragraphs(), Path, Clinic reference material — formularies, care pathways, local protocols — as a…, Chunk one file at the requested granularity, tracking Markdown headings. *… (+4 more)

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
- **172 isolated node(s):** `build_dmg.sh script`, `build_macos.sh script`, `Notes`, `Goal`, `Files in scope` (+167 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

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
- **Why does `deidentify()` connect `deidentify` to `test_stress_corpus.py`, `test_batch.py`, `write_approved`, `add_manual_entity`, `test_app.py`, `test_deid_regressions.py`, `NoEgress`, `normalise_action`, `test_generation_setup.py`, `test_a_date_entity_never_spans_a_line_break`, `residual_scan`, `stress_report.py`, `deidentify.py`, `test_deid_pipeline.py`, `analyze`, `applog.py`, `rebuild`, `conftest.py`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `Document` connect `Document` to `batch.py`, `test_batch.py`, `write_approved`, `test_docx_roundtrip.py`, `test_app.py`, `test_generation.py`, `make_sample_docs.py`, `docx_redact.py`, `render_draft`, `app.py`, `render_clinical_form_panel`, `select_backend`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._