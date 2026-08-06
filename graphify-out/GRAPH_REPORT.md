# Graph Report - .  (2026-08-05)

## Corpus Check
- Corpus is ~19,886 words - fits in a single context window. You may not need a graph.

## Summary
- 429 nodes · 754 edges · 40 communities (21 shown, 19 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 19 edges (avg confidence: 0.88)
- Token cost: 21,400 input · 6,800 output

## Community Hubs (Navigation)
- Layered Detection Engine
- Batch Loading and Write Path
- Design Rationale and Caveats
- Generation Handoff and UI Tests
- Streamlit Review UI
- Document Ingestion
- Ollama Client (Dormant)
- Reviewer Edits and Rebuild
- Surface Form Matching
- Re-identification Round Trip
- Pipeline Regression Suite
- Residual Safety Sweep
- Placeholder Mapping Core
- Entity Dedupe and Map Build
- Privacy Invariants
- Placeholder Assignment
- Mangled Placeholder Repair
- Name Variant Expansion
- Precision Preservation Cases
- Detailed Re-identification
- Care Note Prompt Templates
- Package Entry Point
- De-identification Prompts
- Prompts Package
- Test Suite Package
- Test Runner
- Identity-anchored Date Rule
- Clinical Acronym Filter
- Standalone Regex Layer
- Record Number Label Anchor
- Mid-paragraph Name Capture
- Optional Layer Degradation
- No-NER Fallback Path
- Line-break Tolerant Match
- Placeholder Stability
- Pipeline Determinism
- Identity Map Not Stored
- NHS Number Spacing Variants
- Split Name Collapse
- Medication Block Integrity

## God Nodes (most connected - your core abstractions)
1. `deidentify()` - 22 edges
2. `residual_scan()` - 18 edges
3. `extract_text()` - 18 edges
4. `run_app()` - 16 edges
5. `write_approved()` - 15 edges
6. `rebuild()` - 15 edges
7. `Document` - 14 edges
8. `analysed_batch()` - 14 edges
9. `surface_forms()` - 12 edges
10. `merge_spans()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `pdfplumber` --references--> `extract_text()`  [INFERRED]
  requirements.txt → carescribe/core/ingest.py
- `python-docx` --references--> `extract_text()`  [INFERRED]
  requirements.txt → carescribe/core/ingest.py
- `Shared-surname Binding Collision` --rationale_for--> `surface_forms()`  [INFERRED]
  README.md → carescribe/core/mapping.py
- `presidio-analyzer` --references--> `_build_analyzer()`  [INFERRED]
  requirements.txt → carescribe/core/deidentify.py
- `spaCy Model Fallback Chain` --rationale_for--> `_build_analyzer()`  [INFERRED]
  requirements.txt → carescribe/core/deidentify.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **The Five-layer De-identification Stack** — readme_layer1_structured_regex, readme_layer2_presidio_spacy, readme_layer3_gliner, readme_layer4_variant_expansion, readme_layer5_linebreak_matching [EXTRACTED 1.00]
- **PHI Containment Guarantees** — readme_no_network_calls, readme_mapping_never_on_disk, readme_single_write_path, readme_human_review_gate, readme_cpu_only_local [EXTRACTED 1.00]
- **Approve-time Write Flow** — readme_safety_sweep, carescribe_core_deidentify_residual_scan, carescribe_core_batch_write_approved, readme_dismissal_mechanism [EXTRACTED 1.00]

## Communities (40 total, 19 thin omitted)

### Community 0 - "Layered Detection Engine"
Cohesion: 0.06
Nodes (48): analyze(), classify_person(), _collapse_facility_subsets(), _collapse_person_subsets(), date_span_wanted(), engine_status(), get_analyzer(), get_gliner() (+40 more)

### Community 1 - "Batch Loading and Write Path"
Cohesion: 0.08
Nodes (43): approved_path(), BatchError, list_folder(), load_documents(), RuntimeError, Batch input and approved-output handling. The single place in CareScribe that…, Findings from the safety sweep, minus the ones the reviewer has cleared. A…, Write approved de-identified text to the output folder. Re-runs the safety… (+35 more)

### Community 2 - "Design Rationale and Caveats"
Cohesion: 0.06
Nodes (44): _build_analyzer(), Build a Presidio ``AnalyzerEngine`` over spaCy. Returns (engine, model, error)., fixture, Bare Forename Detection Gap, Batch Review Workflow, CareScribe, Clinical-term Denylist and Drug-suffix Heuristic, Per-document Finding Dismissal (+36 more)

### Community 3 - "Generation Handoff and UI Tests"
Cohesion: 0.12
Nodes (33): AppTest, CareNoteError, generate_care_note(), RuntimeError, Care note generation — NOT WIRED UP. This is the handoff point. De-…, Raised when care note generation can't proceed., Draft a care note from ALREADY DE-IDENTIFIED text. :param deidentified_text:…, # TODO: provider TBD. Whatever is chosen, it must be handed (+25 more)

### Community 4 - "Streamlit Review UI"
Cohesion: 0.15
Nodes (27): current(), documents(), entity_frame(), ingest_sources(), main(), CareScribe — local, privacy-preserving de-identification and review. Run with:…, Extract text from uploads/paths into session state., Drop every document, identifier table, and identity map from memory. (+19 more)

### Community 5 - "Document Ingestion"
Cohesion: 0.13
Nodes (25): _extract_docx(), _extract_pdf(), extract_text(), _extract_txt(), IngestError, Any, RuntimeError, Text extraction for uploaded documents (PDF / DOCX / TXT). Nothing here writes… (+17 more)

### Community 6 - "Ollama Client (Dormant)"
Cohesion: 0.13
Nodes (20): chat(), _client(), _extract_content(), _friendly_error(), is_available(), list_models(), _model_name(), OllamaError (+12 more)

### Community 7 - "Reviewer Edits and Rebuild"
Cohesion: 0.12
Nodes (18): add_manual_entity(), DeidentificationError, DeidResult, RuntimeError, Add an identifier the tools missed and immediately re-redact. The new value…, Raised when de-identification can't run at all., Everything the de-identification stage produces for one document., Re-derive redacted text and the PHI map from a reviewer-edited table. Called… (+10 more)

### Community 8 - "Surface Form Matching"
Cohesion: 0.14
Nodes (15): find_known_as(), find_spans(), _form_pattern(), Pull a patient's preferred name out of a "Known as:" field, if present., Whitespace-tolerant, case-insensitive pattern for one surface form. Tokens are…, Find non-overlapping ``(start, end, placeholder)`` spans for every form. All…, Replace every surface form of every entity with its placeholder. Replacement…, Return surface forms that still appear in ``text`` after redaction. Used by the… (+7 more)

### Community 9 - "Re-identification Round Trip"
Cohesion: 0.21
Nodes (9): Swap placeholders back to their original values. Thin wrapper over…, reidentify(), parametrize, Mapping-layer checks: type normalisation, surface forms, and re-identification.…, test_empty_map_is_a_no_op(), test_non_regex_placeholder_still_substitutes(), test_normalise_type(), test_reidentify_never_crashes() (+1 more)

### Community 10 - "Pipeline Regression Suite"
Cohesion: 0.15
Nodes (6): Regression suite for the layered de-identification pipeline. Two guarantees,…, With REDACT_INPROSE_DATES False, a procedure date is clinical, not identity., Dr Patel", "Dr Raj Patel" and a bare "Patel" are one person, one placeholder., test_analyze_returns_nothing_for_empty_text(), test_every_surname_form_maps_to_one_clinician(), test_in_prose_clinical_date_survives_by_default()

### Community 11 - "Residual Safety Sweep"
Cohesion: 0.20
Nodes (10): Re-scan ALREADY-REDACTED text for anything that still looks identifying. Runs…, residual_scan(), Placeholders are the point of the exercise, not leaks., A .txt file read off a Windows disk arrives with CRLF endings. NER tokenises…, test_crlf_and_lf_documents_behave_identically(), test_residual_scan_catches_a_leaked_name(), test_residual_scan_catches_a_leaked_structured_identifier(), test_residual_scan_does_not_flag_placeholders() (+2 more)

### Community 12 - "Placeholder Mapping Core"
Cohesion: 0.27
Nodes (9): expand_facility_variants(), normalise_type(), In-memory PII <-> placeholder mapping. This module is deliberately pure: it…, Coerce a model-supplied type string onto the canonical list., Return the full organisation name plus short forms. "St. Aidan's General…, All strings that redact to a placeholder, plus collisions worth flagging., Expand entities into every surface form that should be redacted. Entity values…, surface_forms() (+1 more)

### Community 13 - "Entity Dedupe and Map Build"
Cohesion: 0.20
Nodes (10): build_map(), dedupe_entities(), normalise_action(), Drop blank and duplicate entities, keeping first-seen order and casing.…, Build the placeholder -> original-value map used for re-identification. If two…, Coerce a table cell to :data:`REDACT` or :data:`KEEP`. Defaults to redact., test_dedupe_carries_the_keep_action(), test_dedupe_drops_dangerously_short_values() (+2 more)

### Community 14 - "Privacy Invariants"
Cohesion: 0.25
Nodes (9): CPU-only Local Execution, Generation Handoff Contract, Identity Mapping Never Reaches Disk, No Network Calls Invariant, Privacy Invariants, Single Write Path, ollama Commented Out As A Guarantee, A hard assertion that this stage is offline. (+1 more)

### Community 15 - "Placeholder Assignment"
Cohesion: 0.29
Nodes (7): assign_placeholders(), Attach a stable placeholder to each unique entity. A type with exactly one…, Person Typing From Context, Stable Per-entity Placeholders, test_existing_placeholder_is_preserved(), test_multiple_values_get_numbered_placeholders(), test_single_value_gets_a_bare_placeholder()

### Community 16 - "Mangled Placeholder Repair"
Cohesion: 0.29
Nodes (7): _edit_distance(), Levenshtein distance, short-circuiting once it exceeds ``cap``., Map a possibly-corrupted placeholder onto a known one. Returns the exact token…, resolve_placeholder(), Guessing between [MRN_1] and [MRN_2] would attach the wrong identity., test_ambiguous_placeholder_is_refused_not_guessed(), test_edit_distance_caps_out()

### Community 17 - "Name Variant Expansion"
Cohesion: 0.29
Nodes (7): expand_name_variants(), Return every plausible written form of one person's name. Covers: the full…, Dr" as a standalone form would redact every "Dr" in the document., St." must never become a bare "St" that matches clinical text., test_abbreviated_token_is_not_a_standalone_name_form(), test_expand_name_variants_covers_the_forms_the_document_uses(), test_expand_name_variants_never_emits_a_bare_title()

### Community 18 - "Precision Preservation Cases"
Cohesion: 0.29
Nodes (7): parametrize, A bare city name used as context, not as an address, is not an identifier. "She…, test_additional_identifier_does_not_survive(), test_clinical_term_survives(), test_dosage_survives(), test_identifier_does_not_survive(), test_place_of_care_survives()

### Community 19 - "Detailed Re-identification"
Cohesion: 0.33
Nodes (6): Outcome of a re-identification pass., Swap placeholders back to originals, repairing mangled tokens. Never raises on…, reidentify_detailed(), ReidentifyResult, test_invented_placeholder_is_left_alone(), test_mangled_placeholder_is_repaired()

### Community 20 - "Care Note Prompt Templates"
Cohesion: 0.50
Nodes (3): build_messages(), Care note templates. Every template shares the same hard rule: the input is…, Return ``(system, user)`` for a template label and de-identified document.

## Knowledge Gaps
- **2 isolated node(s):** `Longest-match-wins Overlap Resolution`, `Person Typing From Context`
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `residual_scan()` connect `Residual Safety Sweep` to `Layered Detection Engine`, `Batch Loading and Write Path`, `Design Rationale and Caveats`, `Privacy Invariants`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `ollama Commented Out As A Guarantee` connect `Privacy Invariants` to `Ollama Client (Dormant)`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Why does `Generation Handoff Contract` connect `Privacy Invariants` to `Residual Safety Sweep`, `Generation Handoff and UI Tests`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `extract_text()` (e.g. with `pdfplumber` and `python-docx`) actually correct?**
  _`extract_text()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Longest-match-wins Overlap Resolution`, `Person Typing From Context` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Layered Detection Engine` be split into smaller, more focused modules?**
  _Cohesion score 0.06448979591836734 - nodes in this community are weakly interconnected._
- **Should `Batch Loading and Write Path` be split into smaller, more focused modules?**
  _Cohesion score 0.07729468599033816 - nodes in this community are weakly interconnected._