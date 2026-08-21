from carescribe.core import mapping, review_spans


def _entity(value, entity_type="PERSON", confidence="review", placeholder=None, action=mapping.REDACT):
    return {
        "type": entity_type,
        "value": value,
        "confidence": confidence,
        "action": action,
        "placeholder": placeholder or f"[{entity_type}]",
    }


def test_auto_confidence_entities_produce_no_span():
    text = "Seen by [PROVIDER_1] today."
    spans = review_spans.review_spans(
        text, [_entity("Dr Ng", "PROVIDER_1", confidence="auto", placeholder="[PROVIDER_1]")], set(),
    )
    assert spans == []


def test_review_confidence_entity_produces_an_entity_span_at_its_placeholder():
    text = "Seen by [PATIENT] today."
    spans = review_spans.review_spans(
        text, [_entity("Jo Bloggs", "PATIENT", confidence="review", placeholder="[PATIENT]")], set(),
    )
    assert len(spans) == 1
    span = spans[0]
    assert span.kind == review_spans.KIND_ENTITY
    assert text[span.char_start:span.char_end] == "[PATIENT]"
    assert span.id == "entity:jo bloggs"


def test_a_confirmed_entity_produces_no_span():
    text = "Seen by [PATIENT] today."
    entity = _entity("Jo Bloggs", "PATIENT", confidence="review", placeholder="[PATIENT]")
    spans = review_spans.review_spans(text, [entity], {"jo bloggs"})
    assert spans == []


def test_every_occurrence_of_a_repeated_placeholder_is_a_span():
    text = "[PATIENT] was seen. [PATIENT] improved."
    entity = _entity("Jo Bloggs", "PATIENT", confidence="review", placeholder="[PATIENT]")
    spans = review_spans.review_spans(text, [entity], set())
    assert len(spans) == 2
    assert all(s.id == "entity:jo bloggs" for s in spans)


def test_a_kept_entity_produces_no_entity_span():
    """action=Keep means the reviewer already decided — nothing to click on the entity.

    The text is deliberately mid-sentence lowercase before "Bolton" — the
    permissive residual scanner is a separate, entity-unaware mechanism that
    pattern-matches capitalised words regardless of any entity's action, so
    this only asserts no *entity* span exists, not that no span of any kind
    does.
    """
    text = "the town of Bolton was mentioned."
    entity = _entity("Bolton", "LOCATION", confidence="review", placeholder="[LOCATION]", action=mapping.KEEP)
    spans = review_spans.review_spans(text, [entity], set())
    assert not any(s.kind == review_spans.KIND_ENTITY for s in spans)


def test_residual_flags_appear_as_residual_spans():
    text = "please contact Adeyinka on arrival."
    spans = review_spans.review_spans(text, [], set())
    assert any(s.kind == review_spans.KIND_RESIDUAL and s.text == "Adeyinka" for s in spans)


def test_dismissed_residual_flags_are_excluded():
    text = "please contact Adeyinka on arrival."
    from carescribe.core import review_flags
    flag = review_flags.candidate_residuals(text)[0]
    spans = review_spans.review_spans(text, [], set(), dismissed=[flag.key])
    assert spans == []


def test_spans_are_sorted_by_position():
    text = "[PATIENT] met Adeyinka."
    entity = _entity("Jo Bloggs", "PATIENT", confidence="review", placeholder="[PATIENT]")
    spans = review_spans.review_spans(text, [entity], set())
    assert [s.char_start for s in spans] == sorted(s.char_start for s in spans)
