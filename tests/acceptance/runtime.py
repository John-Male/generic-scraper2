from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tests.acceptance.registry import StepRegistry
from tests.acceptance.registry import registry as default_registry

IR_OVERRIDE_ENV = "GENERIC_SCRAPER_ACCEPTANCE_IR"


def resolve_ir(embedded_ir: dict[str, Any]) -> dict[str, Any]:
    """Return the IR a generated test should run against.

    Generated tests embed their IR at generation time (see generator.py),
    but gherkin-mutator's runner adapter must run the same generated entry
    points against many mutated IR variants without regenerating them
    (Acceptance-Pipeline-Specification mutator-spec.md, "Generator and
    Runtime Assumption"). The runner adapter does this by pointing
    IR_OVERRIDE_ENV at a mutated IR file for the duration of one run; a
    normal `pytest` run leaves it unset and gets the embedded IR.
    """
    override_path = os.environ.get(IR_OVERRIDE_ENV)
    if not override_path:
        return embedded_ir
    result: dict[str, Any] = json.loads(Path(override_path).read_text())
    return result


@dataclass(frozen=True)
class Step:
    keyword: str
    text: str


@dataclass(frozen=True)
class ScenarioExecution:
    scenario_name: str
    execution_name: str
    steps: tuple[Step, ...]
    example: dict[str, str]


def _resolve_keywords(raw_steps: list[dict[str, Any]]) -> list[Step]:
    resolved: list[Step] = []
    current = "given"
    for raw in raw_steps:
        keyword = raw["keyword"].lower()
        if keyword in ("and", "but"):
            keyword = current
        else:
            current = keyword
        resolved.append(Step(keyword=keyword, text=raw["text"]))
    return resolved


def expand_executions(ir: dict[str, Any]) -> list[ScenarioExecution]:
    """Expand parser IR into one execution per scenario/example row.

    Background steps are resolved and prepended to every execution. A
    scenario with no examples runs once, with an empty example row.
    """
    background = _resolve_keywords(ir.get("background", []))
    executions: list[ScenarioExecution] = []
    for scenario in ir["scenarios"]:
        scenario_steps = _resolve_keywords(scenario["steps"])
        examples = scenario.get("examples") or [{}]
        for index, example in enumerate(examples, start=1):
            executions.append(
                ScenarioExecution(
                    scenario_name=scenario["name"],
                    execution_name=f"{scenario['name']}/example_{index}",
                    steps=tuple(background) + tuple(scenario_steps),
                    example=example,
                )
            )
    return executions


def run_execution(execution: ScenarioExecution, registry: StepRegistry = default_registry) -> None:
    world: dict[str, Any] = {}
    for step in execution.steps:
        registry.dispatch(step.keyword, step.text, world, execution.example)
