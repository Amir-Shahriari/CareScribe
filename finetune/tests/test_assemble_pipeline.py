"""deidentify_notes + pairs + manifest — the assembly plumbing."""

from __future__ import annotations

import json
import socket

import pytest

from finetune.assemble.deidentify_notes import deidentify_note, leaked_values
from finetune.assemble.manifest import build_manifest, content_hash
from finetune.assemble.pairs import make_pair, stratified_split, write_jsonl
from finetune.datagen.sampler import sample_encounters
from finetune.datagen.schema import FormType

NOTE = (
    "Patient Jane Okafor, NHS 943 476 5919, DOB 3 April 1971. "
    "Seen by Dr H. Okonkwo in the community clinic. Plan: routine review."
)


def test_deidentify_note_replaces_identifiers_with_placeholders():
    note = deidentify_note(NOTE)
    assert "Jane Okafor" not in note.placeholdered_text
    assert "943 476 5919" not in note.placeholdered_text
    assert "[" in note.placeholdered_text
    assert note.phi_map
    assert leaked_values(note, ["Jane Okafor", "943 476 5919"]) == []


def test_deidentify_notes_opens_no_socket():
    real_connect = socket.socket.connect
    calls: list = []

    def spy(self, address, *a, **k):
        calls.append(address)
        return real_connect(self, address, *a, **k)

    socket.socket.connect = spy
    try:
        deidentify_note(NOTE)
    finally:
        socket.socket.connect = real_connect
    assert calls == []


def test_make_pair_uses_real_prompts_and_appends_the_target():
    facts = next(sample_encounters(1, seed=3))
    pair = make_pair(facts, FormType.SOAP, "[PATIENT] seen.", "**S — Subjective**\n- x")
    roles = [m["role"] for m in pair.messages]
    assert roles == ["system", "user", "assistant"]
    assert pair.messages[-1]["content"].startswith("**S — Subjective**")
    assert pair.meta["form_type"] == "soap"
    assert pair.meta["specialty"] == facts.specialty
    # round-trips as one JSON line
    obj = json.loads(pair.to_json_line())
    assert obj["meta"]["styled"] is False


def test_stratified_split_is_deterministic_and_partitions():
    facts = list(sample_encounters(60, seed=8))
    forms = [FormType.SOAP, FormType.PROGRESS_NOTE]
    pairs = [
        make_pair(f, forms[i % 2], "[PATIENT] seen.", "**x**\n- y")
        for i, f in enumerate(facts)
    ]
    a = stratified_split(pairs, seed=1)
    b = stratified_split(pairs, seed=1)
    assert [p.to_json_line() for p in a["train"]] == [p.to_json_line() for p in b["train"]]
    total = sum(len(v) for v in a.values())
    assert total == len(pairs)
    # no pair in two splits
    ids = [id(p) for v in a.values() for p in v]
    assert len(ids) == len(set(ids))


def test_manifest_hash_is_order_independent(tmp_path):
    facts = list(sample_encounters(10, seed=2))
    pairs = [make_pair(f, FormType.SOAP, "[PATIENT] seen.", "**x**\n- y") for f in facts]
    assert content_hash(pairs) == content_hash(list(reversed(pairs)))
    splits = stratified_split(pairs, seed=0)
    manifest = build_manifest(
        splits, generator_backend="template", generator_model=None, seed=0
    )
    assert manifest["total"] == len(pairs)
    assert len(manifest["content_sha256"]) == 64

    out = tmp_path / "pairs.jsonl"
    n = write_jsonl(pairs, out)
    assert n == len(pairs)
    assert len(out.read_text(encoding="utf-8").splitlines()) == n
