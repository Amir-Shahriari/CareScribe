# Graph Report - medgpt  (2026-09-01)

## Corpus Check
- 118 files · ~107,295 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1836 nodes · 3396 edges · 120 communities (101 shown, 19 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 51 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `356369ab`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- mapping.py
- clinical_forms.py
- deidentify
- sampling.py
- batch.py
- Reference: verified template structure
- template_ingest.py
- test_docx_roundtrip.py
- test_app.py
- load_protected_terms
- test_generation.py
- test_template_ingest.py
- Local clinical LLM fine-tune — design
- test_generation_setup.py
- deidentify.py
- test_mapping.py
- model_setup.py
- sampler.py
- backends.py
- fill_template
- test_desktop_packaging.py
- plan
- test_cloud_client.py
- Clinic reference library — design
- schema.py
- Document
- generation_status
- get_analyzer
- refine_document
- expand_name_variants
- assert_deidentified
- ram_verdict
- Architecture
- test_stress_corpus.py
- combine_sources
- ._no_identifier_shapes
- query_tokens
- is_model_present
- make_icon.py
- rebuild
- exemplars.py
- test_deid_regressions.py
- ollama_client.py
- run_app.py
- test_buildinfo.py
- canonical_person_key
- highlight_review
- test_review_gate.py
- _RecordingBackend
- generate_form_document
- Installing CareScribe
- Clinic-uploaded clinical form templates — design
- [0.1.0] - 2026-09-01
- Report templates (SOAP / GP letter / discharge / custom)
- Outpatient Respiratory Clinic Letter (doc03)
- main
- Reference: verified against the real codebase
- swarm-pipeline.md
- EncounterType
- Ward 7B Nursing Handover (doc04)
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
- merge_spans
- GLiNER Deliberately Uninstalled
- get_form_spec
- Sample Source Documents README
- Recurring fictional staff roster (e.g. A. Whitfield) across documents
- Lightweight review UX for de-identification — design
- test_deid_pipeline.py
- app.py
- core/__init__.py
- NoEgress
- analyze
- render_draft
- test_batch.py
- redact
- structured_spans
- BM25
- <id> — <title>
- CareNoteError
- BackendError
- verify_frozen.py
- Per-field retrieval planner — design
- components/__init__.py
- Initials-only patient reference (e.g. M.A.R.)
- Cardiology Discharge Summary (doc02)
- OllamaBackend
- AGENTS.md — rules for automated coding agents in this repo
- Task board
- GP Referral Letter (doc05)
- generate_care_note
- finetune/
- stress_corpus/README.md
- stress_report.py
- reference_library.py
- extract_text
- finetune/__init__.py
- integrate/__init__.py
- test_a_date_entity_never_spans_a_line_break
- test_the_corpus_and_its_answer_key_agree
- medgpt-finetune

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

## Communities (120 total, 19 thin omitted)

### Community 0 - "mapping.py"
Cohesion: 0.11
Nodes (22): entity_frame(), Care note generation — local, on approved de-identified text only. The contract…, template_names(), expand_facility_variants(), find_spans(), _form_pattern(), normalise_action(), normalise_type() (+14 more)

### Community 1 - "clinical_forms.py"
Cohesion: 0.23
Nodes (14): _biopsychosocial_spec(), _fill_cell_after_label(), _fill_header_cell(), FormField, _grid_fields(), HeaderField, _paragraph_texts(), Fill the three bundled APS clinical form templates from approved, de-identified… (+6 more)

### Community 2 - "deidentify"
Cohesion: 0.13
Nodes (27): deidentify(), Run the full local pipeline over one document. CPU-only and offline: no model…, parametrize, Regression suite for the round-2 leaks (A1-A9). The corpus tests in…, Flattening the break made one span of the org and the next line's town., The dangerous direction: this used to fail open, leaking the whole name., Brother: David Chen\\nWei Chen" was one span covering two people., A sibling listed above must not drag the patient into being a relative. (+19 more)

### Community 3 - "sampling.py"
Cohesion: 0.13
Nodes (23): Choice, Any, Random, Range, Small seeded-sampling primitives shared by the vignette sampler. A vignette is…, Pick one of ``options`` uniformly., Pick one of ``options`` by matching ``weights``., An integer in ``[low, high]``, optionally rendered with ``unit``. (+15 more)

### Community 4 - "batch.py"
Cohesion: 0.16
Nodes (20): approved_docx_path(), approved_path(), _default_output_dir(), Path, Batch input and approved-output handling. The single module in CareScribe that…, Reduce a filename to a safe output stem — no paths, no surprises., Where the approved de-identified text for ``name`` will be written., The raw bytes behind an upload or a path, without copying it to disk. (+12 more)

### Community 5 - "Reference: verified template structure"
Cohesion: 0.10
Nodes (20): carescribe/core/clinical_forms.py (module), Refine prompt (clinical form, marker-preserving), Refine prompt (free-form draft revision), Clinical Form Generation (APS Templates) Implementation Plan, Global Constraints, Reference: verified template structure, Self-Review Notes (for the implementer), Task 10: End-to-end generation glue (`generate_form_document`, `refine_form_document`, `render_preview`) (+12 more)

### Community 6 - "template_ingest.py"
Cohesion: 0.13
Nodes (27): ClinicalFormError, FormSpec, RuntimeError, Raised when a clinical form can't be built or filled., slugify(), delete_template(), fill_parsed_template(), _find_grids() (+19 more)

### Community 7 - "test_docx_roundtrip.py"
Cohesion: 0.06
Nodes (47): approved_map(), document_has_text_boxes(), The reviewer-approved ``{literal: placeholder}`` map for the Word pass. This is…, True if a .docx holds text this redaction pass cannot reach., apply_redactions(), _delete_prefix(), extract_text(), has_unreachable_text() (+39 more)

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
Nodes (24): available_forms(), (form_id, title) pairs — bundled forms first, then clinic-uploaded ones., parse_template_bytes(), Validate an uploaded ``.docx``, store it, and return its new form id. Raises…, save_template(), _title_from(), user_form_options(), _anchors() (+16 more)

### Community 12 - "Local clinical LLM fine-tune — design"
Cohesion: 0.06
Nodes (30): 10. Workstream E — integration, 11. What needs a human / external resource, 12. Milestones (testable deliverables), 13. Testing strategy, 1. Goal, 2. Constraints inherited from CareScribe, 3. Approach (selected), 4. Base model (+22 more)

### Community 13 - "test_generation_setup.py"
Cohesion: 0.07
Nodes (18): _cloud_off(), _fresh_generation_status_cache(), mapping_module(), fixture, First-run generation setup: never an empty panel, and the egress line held. The…, The one outbound path must not be reachable from the de-id flow., A captive portal returns HTML with a plausible size., generation_status() is now @st.cache_data(ttl=5) — a process-global cache keyed… (+10 more)

### Community 14 - "deidentify.py"
Cohesion: 0.09
Nodes (34): available_models(), classify_person(), date_span_wanted(), _has_contact_anchor(), _has_identity_anchor(), _is_acronym(), _is_clinical_measurement(), _is_labelled_date_field() (+26 more)

### Community 15 - "test_mapping.py"
Cohesion: 0.06
Nodes (42): assign_placeholders(), build_map(), dedupe_entities(), _edit_distance(), Drop blank and duplicate entities, keeping first-seen order and casing.…, Attach a stable placeholder to each unique entity. A type with exactly one…, Build the placeholder -> original-value map used for re-identification. If two…, Levenshtein distance, short-circuiting once it exceeds ``cap``. (+34 more)

### Community 16 - "model_setup.py"
Cohesion: 0.15
Nodes (20): Option A. The only outbound request the app makes, on an explicit click., run_model_download(), clear_partial_download(), download_model(), _free_bytes(), model_destination(), ModelSetupError, Progress (+12 more)

### Community 17 - "sampler.py"
Cohesion: 0.16
Nodes (18): _blank_for(), expand(), Random, Turn vignettes into `EncounterFacts` instances with a seeded RNG. `expand`…, Yield ``n`` `EncounterFacts`, deterministic for a given ``seed``., Build one `EncounterFacts` from a vignette. With ``gap_probability`` > 0, each…, sample_encounters(), _weighted_pool() (+10 more)

### Community 18 - "backends.py"
Cohesion: 0.14
Nodes (20): privacy_indicator(), A persistent, honest statement of where data goes. It must change when cloud…, cloud_enabled(), cloud_key_present(), cloud_provider(), CloudBackend, describe_backends(), Generation backends, layered so the app works with nothing installed. Selection… (+12 more)

### Community 19 - "fill_template"
Cohesion: 0.18
Nodes (18): _clear_cell(), _dedupe_row(), _fill_cell(), fill_template(), Remove every paragraph after the first, and every run in the first, leaving one…, Overwrite a dedicated value cell (label lives in a different cell)., Fill a fresh in-memory copy of the template. Nothing touches disk., Deduplicate a row's cells by underlying XML element identity. python-docx… (+10 more)

### Community 20 - "test_desktop_packaging.py"
Cohesion: 0.11
Nodes (11): _cloud_off(), fixture, The packaging invariants: what the desktop app may and may not do. Packaging is…, No key may be committed, defaulted, or written anywhere., Even fully configured, cloud is last., A local build and a CI build must freeze the same model., test_cloud_selection_is_never_reached_while_off(), test_output_goes_under_the_user_profile() (+3 more)

### Community 21 - "plan"
Cohesion: 0.32
Nodes (10): plan(), _field(), Per-field retrieval planning (roadmap item E). The shipped planner is rule-…, test_diagnoses_field_wants_section_reference(), test_medication_field_wants_sentence_level_reference(), test_mood_field_wants_no_reference(), test_plan_covers_every_field_and_wants_exemplars_for_all(), test_planner_is_pluggable() (+2 more)

### Community 22 - "test_cloud_client.py"
Cohesion: 0.10
Nodes (25): CloudError, _config(), _post(), RuntimeError, Transport for the optional cloud generation backend. Reached only when a…, Yield the payload of each ``data:`` line in an SSE stream., Stream a completion from the configured cloud provider, yielding text. Raises…, A recoverable problem talking to the configured cloud provider. (+17 more)

### Community 23 - "Clinic reference library — design"
Cohesion: 0.17
Nodes (11): `app.py`, Architecture, Clinic reference library — design, Decision, Follow-ups (not blocking), New `core/reference_library.py`, Privacy / safety, Problem (+3 more)

### Community 24 - "schema.py"
Cohesion: 0.19
Nodes (17): BaseModel, _Base, Demographics, Finding, HistoryItem, Medication, PlanItem, `EncounterFacts` — the single source of truth for one synthetic clinical… (+9 more)

### Community 25 - "Document"
Cohesion: 0.15
Nodes (25): document_flags(), entity_confirmed(), flag_dismissals(), Re-derive the preview and map from an edited entity list., Redact the original .docx using the map the reviewer just approved. Detection…, Offer the redacted .docx, but only once it has cleared the sweep., Candidate residuals for this document, recomputed from current text., The primary review surface: the redacted text, second-look items marked.… (+17 more)

### Community 26 - "generation_status"
Cohesion: 0.11
Nodes (21): cache_data, generation_status(), _llama_runtime_available(), missing_reason(), Is generation usable right now, and if not, what should the user do? Kept…, One plain sentence on why generation is not available yet., Which generation backends are usable at this moment., Which backend would actually be used, matching the backend ladder. (+13 more)

### Community 27 - "get_analyzer"
Cohesion: 0.20
Nodes (11): cache_resource, load_detection_engine(), Load the NER model once per session, not once per rerun. Streamlit re-runs the…, engine_status(), get_analyzer(), get_gliner(), Return the shared Presidio analyzer, or ``None`` if it can't be built. First…, Return the shared GLiNER model, or ``None`` if it isn't available. Guarded end… (+3 more)

### Community 28 - "refine_document"
Cohesion: 0.20
Nodes (11): Revise an existing draft against a follow-up instruction. Operates on the same…, The shared preamble — role, anti-fabrication rules, placeholder rules., refine_document(), system_prompt(), test_generate_document_default_behaviour_is_unchanged(), test_refine_document_accepts_a_system_and_refine_prompt_override(), test_refine_document_default_behaviour_is_unchanged(), test_refinement_carries_the_running_history() (+3 more)

### Community 29 - "expand_name_variants"
Cohesion: 0.18
Nodes (11): expand_name_variants(), _initial_letters(), Initials for a name, with hyphenated components contributing each part.…, Return every plausible written form of one person's name. Covers: the full…, Dr" as a standalone form would redact every "Dr" in the document., St." must never become a bare "St" that matches clinical text., test_abbreviated_token_is_not_a_standalone_name_form(), test_expand_name_variants_covers_the_forms_the_document_uses() (+3 more)

### Community 30 - "assert_deidentified"
Cohesion: 0.16
Nodes (14): assert_deidentified(), CloudBackend (unwired seam), Refuse to send anything carrying a value from the identity mapping. A cheap,…, System prompt (anti-fabrication rules), Optional cloud generation path (off by default), Two required env vars (CARESCRIBE_CLOUD_PROVIDER / CARESCRIBE_CLOUD_API_KEY), CareScribe practitioner one-page guide, Existing _as_docx() nothing-touches-disk precedent (+6 more)

### Community 31 - "ram_verdict"
Cohesion: 0.33
Nodes (6): available_ram_gb(), ram_verdict(), Total system RAM in GB, or 0.0 if it cannot be determined., Whether this machine can run the bundled local model. Returns a verdict rather…, test_a_capable_laptop_gets_no_warning(), test_a_weak_laptop_gets_a_warning_not_a_crash()

### Community 32 - "Architecture"
Cohesion: 0.13
Nodes (14): 1. Template assets, 2. Form spec extraction, 3. Header fields (practitioner-entered), 4. Multi-document source combination, 5. Generation, 6. Review, 7. Export, 8. UI (`app.py`, Step 5) (+6 more)

### Community 33 - "test_stress_corpus.py"
Cohesion: 0.21
Nodes (12): _entities(), _normalise(), parametrize, Corpus-driven regression net. Every document in ``stress_corpus/`` is run…, Confidence tiering must never make the reviewer's job LESS safe. An "auto"…, Whatever the sweep still flags must not be a structured identifier. A surviving…, Collapse every whitespace run to one space, so line breaks stop mattering., _redacted() (+4 more)

### Community 34 - "combine_sources"
Cohesion: 0.21
Nodes (13): combine_sources(), Concatenate several documents' de-identified text into one source. ``sources``…, Regression test for Finding 3: raw filename must not leak into model-facing…, Regression test for Finding 1: cap at 26 documents (A-Z)., Regression test for Finding 1: prefixed placeholders must match PLACEHOLDER_RE.…, Regression test for Finding 2: text and map rewrites must be consistent. A…, test_combine_sources_no_filename_in_output(), test_combine_sources_non_standard_placeholder_consistency() (+5 more)

### Community 35 - "._no_identifier_shapes"
Cohesion: 0.40
Nodes (3): field_validator, _looks_like_identifier(), Return a reason string if ``value`` looks like a leaked identifier.

### Community 36 - "query_tokens"
Cohesion: 0.20
Nodes (10): Protocol, Per-field retrieval planning for clinical-form generation. Roadmap item E…, Deterministic planner driven by a keyword taxonomy over field labels., RetrievalPlan, RetrievalPlanner, RuleBasedPlanner, query_tokens(), Okapi BM25 over a small in-memory document set — standard library only. Shared… (+2 more)

### Community 37 - "is_model_present"
Cohesion: 0.50
Nodes (4): is_model_present(), True if a usable model file is already on this computer. This is the marker…, Setup is one-time because the file itself is the state., test_model_presence_is_the_persisted_marker()

### Community 38 - "make_icon.py"
Cohesion: 0.29
Nodes (12): Image, _load_font(), main(), Path, Generate CareScribe's placeholder icon. A real icon is a design job; this…, The first usable bold face, or ``None`` if none of them load., A rounded square with "CS" centred on it., macOS only. Silently skipped elsewhere — the .app is built on a Mac. (+4 more)

### Community 39 - "rebuild"
Cohesion: 0.11
Nodes (20): add_manual_entity(), DeidentificationError, DeidResult, RuntimeError, Re-derive redacted text and the PHI map from a reviewer-edited table. Called…, Add an identifier the tools missed and immediately re-redact. The new value…, Raised when de-identification can't run at all., Everything the de-identification stage produces for one document. (+12 more)

### Community 40 - "exemplars.py"
Cohesion: 0.15
Nodes (24): add_exemplar(), count(), _dir(), _load(), _path(), Path, House-style exemplar retrieval for clinical-form generation. A clinic…, Top-``k`` stored values for ``field_key``, ranked by BM25 against ``query``. (+16 more)

### Community 41 - "test_deid_regressions.py"
Cohesion: 0.09
Nodes (28): _mrn_values(), parametrize, Regression suite for the five leaks found on a second, non-fixture document.…, A two-part capitalised phrase mid-document is not a letterhead., Layer 1 must carry this on its own — NER catching it is luck, not a guarantee., M.E.C.\\nFollow-up" must not become the name "M.E.C. Follow"., Regardless of REDACT_INPROSE_DATES, which stays False by default., The label shapes document #2 actually used, including the parenthetical. (+20 more)

### Community 42 - "ollama_client.py"
Cohesion: 0.14
Nodes (19): default_model(), generate(), is_up(), list_models(), missing_model_message(), OllamaError, RuntimeError, Local Ollama client — pinned to the loopback interface. Generation is the first… (+11 more)

### Community 43 - "run_app.py"
Cohesion: 0.16
Nodes (17): Popen, close_splash(), _fatal(), free_port(), main(), _no_window_kwargs(), CareScribe desktop launcher — the app's entry point. Starts the Streamlit…, Dismiss the bootloader splash, if this is a frozen build that has one.… (+9 more)

### Community 44 - "test_buildinfo.py"
Cohesion: 0.24
Nodes (10): build_info(), Build information for CareScribe., Return standard HTTP User-Agent string., Return application identity and version., user_agent(), Tests for buildinfo module., Test that user_agent returns correct format., Test that build_info returns correct name and version. (+2 more)

### Community 45 - "canonical_person_key"
Cohesion: 0.15
Nodes (15): _collapse_person_identities(), True for a person row whose role is known (patient / relative / clinician)., Collapse every written form of one person onto a single entity row.…, _specific_person_type(), canonical_person_key(), keys_are_compatible(), name_core(), Split a name into its parts with any leading honorific removed. "Mrs Margaret… (+7 more)

### Community 46 - "highlight_review"
Cohesion: 0.24
Nodes (9): highlight_review(), Click-to-redact highlighted text. Renders already-redacted (or already-flagged)…, Render ``html`` and return the ``data-span-id`` of the last click. Returns…, _frontend_path(), Path, Offline-first: nothing in this file may fetch from a CDN., test_frontend_file_exists(), test_frontend_has_no_external_script_or_link_tags() (+1 more)

### Community 47 - "test_review_gate.py"
Cohesion: 0.06
Nodes (43): blocking_reason(), The approval gate. Only the **authoritative safety sweep** blocks approval. A…, Why Approve is disabled, in one short line. Empty string means it isn't.…, candidate_residuals(), Flag, _is_common(), outstanding(), _placeholder_ranges() (+35 more)

### Community 50 - "generate_form_document"
Cohesion: 0.20
Nodes (11): generate_form_document(), Human-readable rendering for display only — the marker text in ``draft_state``…, refine_form_document(), render_preview(), Captures exactly what generation handed the model — mirrors the fixture in…, RecordingBackend, test_generate_form_document_refuses_a_real_identifier(), test_generate_form_document_sends_the_field_marker_prompt() (+3 more)

### Community 51 - "Installing CareScribe"
Cohesion: 0.22
Nodes (8): Before you start, First launch, If it will not start, Installing CareScribe, macOS, Updating, Where your files go, Windows

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

### Community 57 - "main"
Cohesion: 0.15
Nodes (17): current(), documents(), ingest_sources(), _inject_app_css(), main(), PHI_KEYS (session-state PHI registry), A missing model must stop loudly, never fall back to fetching one., CareScribe's visual identity, applied once per rerun. Streamlit's theming only… (+9 more)

### Community 58 - "Reference: verified against the real codebase"
Cohesion: 0.15
Nodes (12): Global Constraints, Lightweight Review UX Redesign Implementation Plan, Reference: verified against the real codebase, Self-Review Notes, Task 1: Confidence tiering in the detection pipeline, Task 2: Unified review-span module, Task 3: Click-to-redact custom Streamlit component, Task 4: Simplify `review_checklist.py` to a two-input gate (+4 more)

### Community 60 - "EncounterType"
Cohesion: 0.13
Nodes (22): build_messages(), Care note templates. Every template shares the same hard rule: the input is…, Return ``(system, user)`` for a template label and de-identified document., Enum, EncounterType, FormType, The output form a training example asks the model to fill., The clinical shape of the encounter the source note describes. (+14 more)

### Community 61 - "Ward 7B Nursing Handover (doc04)"
Cohesion: 0.50
Nodes (4): Aiden Braithwaite, Ward 7B Nursing Handover (doc04), 'A. Surname' against full name in header, Labelled date fields

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
Cohesion: 0.15
Nodes (22): add_file(), is_empty(), ``(filename, paragraph_count)`` per loaded reference file., Top-``k`` reference passages for ``query`` at ``granularity``. BM25, ``score >…, Store an uploaded reference file. Returns the stored filename., ReferenceHit, search(), sources() (+14 more)

### Community 82 - "merge_spans"
Cohesion: 0.20
Nodes (10): _collapse_facility_subsets(), _collapse_person_subsets(), merge_spans(), protected_ranges(), Shrink a NER span to its identifying core. Drops leading titles ("Sister Fiona…, Drop a person entity whose name is contained in a longer one. NER returns…, Drop a facility whose name is a short form of a longer one. The letterhead…, Resolve every layer's spans into a de-duplicated entity list. Overlaps are… (+2 more)

### Community 84 - "get_form_spec"
Cohesion: 0.18
Nodes (16): build_prompt(), get_form_spec(), Build the (system, user) prompt pair. ``exemplars`` maps a field key to house-…, _load(), test_build_prompt_lists_every_field_marker_in_order(), test_build_prompt_never_echoes_a_real_identifier_pattern(), Generic table-row classification: which rows are fields, which are section…, test_biopsychosocial_spec_field_count_and_grid() (+8 more)

### Community 87 - "Lightweight review UX for de-identification — design"
Cohesion: 0.14
Nodes (13): 1. Confidence tiering (drives what gets a click at all), 2. One primary review view, not three, 3. The click-to-redact component, 4. Attestation & audit trail, 5. Crash-risk fixes, Architecture, Current state (for reference), Goals (+5 more)

### Community 88 - "test_deid_pipeline.py"
Cohesion: 0.05
Nodes (41): Re-scan ALREADY-REDACTED text for anything that still looks identifying. Runs…, residual_scan(), parametrize, Regression suite for the layered de-identification pipeline. Two guarantees,…, With REDACT_INPROSE_DATES False, a procedure date is clinical, not identity., DOB and admission/discharge dates carry identity, so they go., spaCy labels "ECG" and "NSTEMI" as organisations; the filter must drop them., Placeholders are the point of the exercise, not leaks. (+33 more)

### Community 89 - "app.py"
Cohesion: 0.08
Nodes (43): _draft_state(), _form_draft_key(), _form_draft_state(), _header_values_complete(), _invalidate_form_export(), CareScribe — local, privacy-preserving de-identification and review. Run with:…, Drop any previously re-identified/exportable content — called whenever the…, Which backend will be used, and the fix if none is available. (+35 more)

### Community 90 - "core/__init__.py"
Cohesion: 0.15
Nodes (21): _review_span_style(), Core logic: Ollama access, ingestion, de-identification, care notes, PHI…, Residual-candidate highlighter — where the reviewer's eye should go first. This…, _entity_spans(), Unifies the two things a reviewer might still need to act on in one document's…, Every clickable span in ``redacted_text``, in reading order. ``confirmed`` is…, One clickable span in a document's redacted text., Placeholder occurrences for low-confidence, not-yet-confirmed entities. (+13 more)

### Community 91 - "NoEgress"
Cohesion: 0.14
Nodes (10): NoEgress, Fails the test if anything opens a non-loopback socket. Loopback is allowed:…, Re-identification is pure Python — it must not phone anywhere., test_reidentification_opens_no_socket(), The load that used to hang on a captive portal must not exist., Reset the cache so the guard covers a genuine first load., The reported hang: no model, so something tries to download it., test_a_missing_model_fails_loudly_instead_of_fetching() (+2 more)

### Community 92 - "analyze"
Cohesion: 0.10
Nodes (22): analyze(), flatten_lines(), gliner_spans(), ner_spans(), Layer 2: Presidio/spaCy detections, mapped onto CareScribe entity types.…, Layer 3: GLiNER detections, or an empty list when it isn't installed., Run every enabled layer over ``text`` and return reviewable entities. Each…, One detection, in character offsets over the source text. (+14 more)

### Community 95 - "render_draft"
Cohesion: 0.40
Nodes (6): _as_docx(), The de-identified draft, refinement, re-identification, and exports., Opt-in, local-only substitution of placeholders back to real values., Render generated text to a .docx in memory — nothing touches disk., render_draft(), render_reidentification()

### Community 96 - "test_batch.py"
Cohesion: 0.06
Nodes (50): analyze_document(), BatchError, list_folder(), load_documents(), RuntimeError, Return the supported documents in ``folder``, sorted by name. Non-recursive on…, Extract text from uploads or paths. Returns ``(documents, errors)``. One…, Run the de-identification layers over one document, in place. (+42 more)

### Community 98 - "redact"
Cohesion: 0.22
Nodes (9): find_known_as(), Pull a patient's preferred name out of a "Known as:" field, if present., Replace every surface form of every entity with its placeholder. Replacement…, redact(), Form tokens are joined with \\s+, so a name split across lines still matches., test_longest_match_wins_on_overlap(), test_matcher_does_not_fire_inside_a_longer_word(), test_matcher_tolerates_a_line_break() (+1 more)

### Community 99 - "structured_spans"
Cohesion: 0.11
Nodes (18): _header_footer_bounds(), _plausible_surname(), Character ranges of the document's opening and closing lines., True if the trailing token of an initial+surname reads like a real name.…, Layer 1: deterministic regex detections over ``text``., REDACT_INPROSE_DATES flag, structured_spans(), expand_org_variants (Layer 4 — variant expansion) (+10 more)

### Community 100 - "BM25"
Cohesion: 0.18
Nodes (9): ExemplarError, RuntimeError, Raised when an exemplar cannot be stored — e.g. it still holds an identifier., RuntimeError, Raised when a reference file cannot be stored., ReferenceError, BM25, Okapi BM25. ``documents`` is a list of token lists. (+1 more)

### Community 101 - "<id> — <title>"
Cohesion: 0.29
Nodes (6): Acceptance criteria, Do NOT touch, Files in scope, Goal, <id> — <title>, Notes

### Community 102 - "CareNoteError"
Cohesion: 0.17
Nodes (13): assert_no_residual_identifiers(), CareNoteError, load_prompt(), RuntimeError, Build the user prompt for one template with the source text embedded., Refuse to send text the residual sweep still flags. :func:`assert_deidentified`…, Raised when care note generation can't proceed., Read one prompt file from ``carescribe/prompts``. (+5 more)

### Community 104 - "BackendError"
Cohesion: 0.19
Nodes (8): BackendError, LocalGGUFBackend, RuntimeError, Raised when a backend cannot be used, with the fix in the message., CPU-only generation from a bundled GGUF via ``llama-cpp-python``. The model is…, True if the runtime and a model file are both present., It fabricates otherwise — measured, not assumed., test_the_local_model_stays_pinned_at_temperature_zero()

### Community 105 - "verify_frozen.py"
Cohesion: 0.36
Nodes (9): bundled_app_py(), _default_dist(), find_executable(), free_port(), main(), Path, Post-build smoke check: does the frozen CareScribe binary actually start? A…, Locate the frozen entry-point inside a PyInstaller output directory. (+1 more)

### Community 106 - "Per-field retrieval planner — design"
Cohesion: 0.17
Nodes (11): `app.py`, Architecture, `core/reference_library.py`, `core/retrieval_planner.py` (new), `core/text_search.py`, Decision, Follow-ups (not blocking), Per-field retrieval planner — design (+3 more)

### Community 109 - "Initials-only patient reference (e.g. M.A.R.)"
Cohesion: 0.40
Nodes (6): Community MH Discharge Letter (doc01), Mohammed Al-Rashid ('Mo'), Mariam Aisha Rahman, Mental Health Act Assessment Record (doc10), Initials-only patient reference (e.g. M.A.R.), Permanent regression net for document #2 leaks

### Community 110 - "Cardiology Discharge Summary (doc02)"
Cohesion: 0.20
Nodes (10): Cardiology Discharge Summary (doc02), Margaret Elizabeth Chen ('Peggy'), Priya Venkataraman, Psychological Medicine Clinic Letter (doc06), Crisis Team Contact Log (doc09), Tomasz Wisniewski, Facility short forms, In-prose vs anchored dates (+2 more)

### Community 113 - "OllamaBackend"
Cohesion: 0.13
Nodes (13): OllamaBackend, Local generation through the loopback-pinned Ollama daemon., core/model_setup.py (model download, isolated), packaging/build_macos.sh, packaging/build_windows.ps1, packaging/carescribe.iss (Inno Setup script), packaging/make_icon.py, The desktop app (PyInstaller packaging) (+5 more)

### Community 114 - "AGENTS.md — rules for automated coding agents in this repo"
Cohesion: 0.40
Nodes (4): AGENTS.md — rules for automated coding agents in this repo, Do, Never, Task spec shape

### Community 115 - "Task board"
Cohesion: 0.17
Nodes (11): Fine-tune decisions locked (2026-09-01), Fine-tune hardware facts (2026-09-01), Fine-tune progress — cockpit-driven (uncommitted, on integration branch), Local clinical LLM fine-tune (started 2026-09-01), Pipeline incident 2026-09-01 (fixed), Task board, What shipped, Worker capability ceiling on the fine-tune workstream (2026-09-01) (+3 more)

### Community 116 - "GP Referral Letter (doc05)"
Cohesion: 0.25
Nodes (8): Elspeth Mackenzie-Ford ('Ellie'), GP Referral Letter (doc05), Oluwaseun Adeyinka, Resource Centre Referral (doc08), Hyphenated surname pattern, 'Known as' alias pattern, Two label styles pattern, Shared case number 990214 reused across fictional patients

### Community 117 - "generate_care_note"
Cohesion: 0.18
Nodes (10): Backend, generate_care_note(), Protocol, Prepend the review banner, without duplicating one already there., Draft a care note from ALREADY DE-IDENTIFIED text, returning it whole. The…, One method wide: the seam a different provider would be swapped in at., with_banner(), test_generated_output_keeps_the_review_banner() (+2 more)

### Community 118 - "finetune/"
Cohesion: 0.50
Nodes (3): finetune/, Isolated environment, Layout

### Community 119 - "stress_corpus/README.md"
Cohesion: 0.18
Nodes (10): answer_key.json, CMHT Family Review Letter (doc07), Wei Chen, must_preserve (answer key field), must_redact (answer key field), No real patient documents policy, Running it, Stress corpus (+2 more)

### Community 120 - "stress_report.py"
Cohesion: 0.67
Nodes (3): main(), normalise(), Per-document pass/fail report for the stress corpus. python…

### Community 121 - "reference_library.py"
Cohesion: 0.22
Nodes (14): Add clinic reference files (formulary, pathways, protocols) to a local library.…, _render_reference_uploader(), _all_chunks(), _bounded(), Chunk, _dir(), _files(), _paragraphs() (+6 more)

### Community 123 - "extract_text"
Cohesion: 0.05
Nodes (55): BaseException, ensure_engine_ready(), Load the model at startup, behind a visible spinner. Deliberately not lazy. If…, The last line of defence: a calm message instead of a stack trace. A clinician…, render_unexpected_error(), exception(), get_logger(), log() (+47 more)

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
- **185 isolated node(s):** `medgpt-finetune`, `build_dmg.sh script`, `build_macos.sh script`, `Worker capability ceiling on the fine-tune workstream (2026-09-01)`, `Fine-tune hardware facts (2026-09-01)` (+180 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

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
- **Why does `deidentify()` connect `deidentify` to `test_batch.py`, `test_stress_corpus.py`, `redact`, `rebuild`, `test_app.py`, `test_deid_pipeline.py`, `test_deid_regressions.py`, `NoEgress`, `test_generation_setup.py`, `deidentify.py`, `test_mapping.py`, `stress_report.py`, `extract_text`, `analyze`, `test_a_date_entity_never_spans_a_line_break`, `conftest.py`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Why does `Document` connect `Document` to `mapping.py`, `app.py`, `test_batch.py`, `batch.py`, `test_docx_roundtrip.py`, `test_app.py`, `test_generation.py`, `make_sample_docs.py`, `main`, `render_draft`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._