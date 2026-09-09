"""A second, independent grader for faithfulness.

`assemble.validators` scores a draft by aligning it back to the same
`EncounterFacts` that `build_target` rendered the target from — model, target
and grader all derive from one artefact, so a perfect score is consistent with
"reproduced the scaffold".

This grader sees the SOURCE NOTE and the DRAFT only. It never receives
`EncounterFacts`, and `judge_draft` has no parameter through which they could be
passed. Disagreement between the two graders is the signal worth reporting.

Evaluation-only: this module opens a socket to the local Ollama daemon and must
never be importable from `carescribe/`.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Callable

JUDGE_SYSTEM = (
    "You grade clinical documents for faithfulness. You are given a SOURCE note "
    "and a DRAFT written from it. Decide whether every clinical claim in the "
    "DRAFT is supported by the SOURCE.\n"
    "Bracketed placeholders such as [PATIENT] or [DATE_2] are redacted "
    "identifiers, not claims — ignore them.\n"
    'Reply with JSON only: {"supported": true|false, "unsupported_claims": [...]}'
)

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


@dataclass(frozen=True)
class JudgeVerdict:
    supported: bool | None      # None => the judge's reply could not be parsed
    unsupported_claims: list[str]
    raw: str


def judge_draft(
    source: str, draft: str, *, complete: Callable[[str, str], str]
) -> JudgeVerdict:
    """Grade ``draft`` against ``source``. ``complete(system, user) -> str``."""
    user = f"SOURCE:\n{source}\n\nDRAFT:\n{draft}"
    raw = complete(JUDGE_SYSTEM, user)
    match = _JSON_RE.search(raw or "")
    if not match:
        return JudgeVerdict(None, [], raw)
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        return JudgeVerdict(None, [], raw)
    supported = payload.get("supported")
    return JudgeVerdict(
        supported if isinstance(supported, bool) else None,
        [str(c) for c in payload.get("unsupported_claims", [])],
        raw,
    )


class OllamaJudge:
    """The default grader: a larger, different model on the local daemon."""

    def __init__(
        self, model: str = "qwen3.8:27b", host: str = "http://127.0.0.1:11434"
    ) -> None:
        self.model, self.host = model, host

    def complete(self, system: str, user: str) -> str:
        import urllib.request

        body = json.dumps(
            {
                "model": self.model,
                "prompt": f"{system}\n\n{user}",
                "stream": False,
                "think": False,
                "options": {"temperature": 0.0},
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{self.host}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read().decode("utf-8")).get("response", "")


__all__ = ["JUDGE_SYSTEM", "JudgeVerdict", "OllamaJudge", "judge_draft"]
