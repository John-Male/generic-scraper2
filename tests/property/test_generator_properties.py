from __future__ import annotations

import ast
import json
import random
import string
from pathlib import Path
from typing import Any

import pytest

from tests.acceptance import generator
from tests.property.support import draw_text, for_each_trial

_NAME_ALPHABET = string.ascii_letters + string.digits + " -_!?./"


def _random_ir(rng: random.Random) -> dict[str, Any]:
    scenarios = []
    for index in range(rng.randint(1, 3)):
        raw_examples = [{"value": draw_text(rng)} for _ in range(rng.randint(0, 3))]
        scenarios.append(
            {
                "name": f"{draw_text(rng, alphabet=_NAME_ALPHABET, max_size=20)}-{index}",
                "steps": [{"keyword": "Given", "text": draw_text(rng)}],
                "examples": raw_examples or None,
            }
        )
    return {"name": draw_text(rng), "scenarios": scenarios}


@pytest.mark.property
def test_generate_always_writes_parseable_python_with_unique_function_names(
    tmp_path: Path,
) -> None:
    def check(rng: random.Random) -> None:
        ir = _random_ir(rng)
        draw = rng.randint(0, 1_000_000)
        ir_path = tmp_path / f"ir_{draw}.json"
        ir_path.write_text(json.dumps(ir))
        output_dir = tmp_path / f"generated_{draw}"

        test_file = generator.generate(ir_path, output_dir)
        source = test_file.read_text()

        tree = ast.parse(source)
        test_function_names = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        ]
        assert len(test_function_names) == len(set(test_function_names))

    for_each_trial(check, trials=30)
