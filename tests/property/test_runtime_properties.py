from __future__ import annotations

import random
from typing import Any

import pytest

from tests.acceptance.runtime import expand_executions
from tests.property.support import draw_choice, draw_text, for_each_trial

_KEYWORDS = ["Given", "When", "Then", "And", "But"]


def _random_step(rng: random.Random) -> dict[str, str]:
    return {"keyword": draw_choice(rng, _KEYWORDS), "text": draw_text(rng)}


def _random_ir(rng: random.Random) -> dict[str, Any]:
    background = [_random_step(rng) for _ in range(rng.randint(0, 3))]
    scenario_steps = [_random_step(rng) for _ in range(rng.randint(1, 5))]
    raw_examples = [{"value": draw_text(rng)} for _ in range(rng.randint(0, 3))]
    return {
        "name": draw_text(rng),
        "background": background,
        "scenarios": [
            {
                "name": draw_text(rng),
                "steps": scenario_steps,
                "examples": raw_examples or None,
            }
        ],
    }


@pytest.mark.property
def test_expand_executions_conserves_steps_and_normalizes_keywords() -> None:
    def check(rng: random.Random) -> None:
        ir = _random_ir(rng)
        background = ir["background"]
        scenario = ir["scenarios"][0]
        raw_examples = scenario["examples"]
        expected_texts = [step["text"] for step in background] + [
            step["text"] for step in scenario["steps"]
        ]

        executions = expand_executions(ir)

        assert len(executions) == (len(raw_examples) if raw_examples else 1)
        for execution in executions:
            assert len(execution.steps) == len(expected_texts)
            assert [step.text for step in execution.steps] == expected_texts
            assert all(step.keyword in ("given", "when", "then") for step in execution.steps)

    for_each_trial(check)
