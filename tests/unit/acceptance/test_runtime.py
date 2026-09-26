from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tests.acceptance.registry import StepRegistry
from tests.acceptance.runtime import IR_OVERRIDE_ENV, expand_executions, resolve_ir, run_execution

SAMPLE_IR: dict[str, Any] = {
    "name": "Sample feature",
    "background": [
        {"keyword": "Given", "text": "a background is set"},
    ],
    "scenarios": [
        {
            "name": "sample-1",
            "steps": [
                {"keyword": "Given", "text": "a value of \"<value>\"", "parameters": ["value"]},
                {"keyword": "When", "text": "the action happens"},
                {"keyword": "Then", "text": "the result is \"<value>\"", "parameters": ["value"]},
                {"keyword": "And", "text": "a second assertion holds"},
            ],
            "examples": [{"value": "one"}, {"value": "two"}],
        }
    ],
}


def test_expand_executions_creates_one_execution_per_example_row() -> None:
    executions = expand_executions(SAMPLE_IR)

    assert [e.execution_name for e in executions] == [
        "sample-1/example_1",
        "sample-1/example_2",
    ]
    assert executions[0].example == {"value": "one"}
    assert executions[1].example == {"value": "two"}


def test_expand_executions_prepends_background_steps() -> None:
    executions = expand_executions(SAMPLE_IR)

    assert executions[0].steps[0].text == "a background is set"
    assert executions[0].steps[0].keyword == "given"


def test_expand_executions_resolves_and_to_the_preceding_keyword() -> None:
    executions = expand_executions(SAMPLE_IR)

    # steps: background given, given, when, then, and(-> then)
    keywords = [step.keyword for step in executions[0].steps]
    assert keywords == ["given", "given", "when", "then", "then"]


def test_expand_executions_runs_scenarios_without_examples_once() -> None:
    ir: dict[str, Any] = {
        "name": "No examples",
        "scenarios": [
            {"name": "no-examples-1", "steps": [{"keyword": "Given", "text": "a plain step"}]}
        ],
    }

    executions = expand_executions(ir)

    assert len(executions) == 1
    assert executions[0].execution_name == "no-examples-1/example_1"
    assert executions[0].example == {}


def test_run_execution_dispatches_every_step_in_order() -> None:
    registry = StepRegistry()
    calls: list[str] = []

    @registry.given(r"a background is set")
    def _background(ctx: object) -> None:
        calls.append("background")

    @registry.given(r'a value of "<(?P<placeholder>[a-z]+)>"')
    def _given(ctx: Any) -> None:
        calls.append(f"given:{ctx.example[ctx.match.group('placeholder')]}")

    @registry.when(r"the action happens")
    def _when(ctx: object) -> None:
        calls.append("when")

    @registry.then(r'the result is "<(?P<placeholder>[a-z]+)>"')
    def _then(ctx: Any) -> None:
        calls.append(f"then:{ctx.example[ctx.match.group('placeholder')]}")

    @registry.then(r"a second assertion holds")
    def _then2(ctx: object) -> None:
        calls.append("then2")

    execution = expand_executions(SAMPLE_IR)[0]
    run_execution(execution, registry=registry)

    assert calls == ["background", "given:one", "when", "then:one", "then2"]


def test_resolve_ir_returns_the_embedded_ir_without_an_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(IR_OVERRIDE_ENV, raising=False)

    assert resolve_ir(SAMPLE_IR) is SAMPLE_IR


def test_resolve_ir_loads_from_the_override_path_when_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mutated_ir = {"name": "Mutated feature", "scenarios": []}
    override_path = tmp_path / "mutated.json"
    override_path.write_text(json.dumps(mutated_ir))
    monkeypatch.setenv(IR_OVERRIDE_ENV, str(override_path))

    assert resolve_ir(SAMPLE_IR) == mutated_ir


def test_run_execution_fails_on_unmatched_step() -> None:
    empty_registry = StepRegistry()
    execution = expand_executions(SAMPLE_IR)[0]

    try:
        run_execution(execution, registry=empty_registry)
    except AssertionError as exc:
        assert "no 'given' step handler matched" in str(exc)
    else:
        raise AssertionError("expected run_execution to raise AssertionError")
