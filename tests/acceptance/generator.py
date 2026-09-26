"""acceptance-entrypoint-generator: turns parser JSON IR into generated pytest files.

Command contract (see Acceptance-Pipeline-Specification/acceptance-generator.md):

    acceptance-entrypoint-generator <json-ir> <generated-test-output>

Exit codes: 0 success, 1 input/output/generation error, 2 wrong usage.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from tests.acceptance.runtime import ScenarioExecution, expand_executions

_EXIT_OK = 0
_EXIT_ERROR = 1
_EXIT_USAGE = 2


def _sanitize(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()
    return slug or "unnamed"


def _metadata_slug(feature_path: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", feature_path.lower()).strip("-")
    return f"{slug}.json"


def _function_name(execution: ScenarioExecution) -> str:
    example_suffix = execution.execution_name.rsplit("/", 1)[-1]
    return f"test_{_sanitize(execution.scenario_name)}__{example_suffix}"


def _render(ir: dict[str, Any], ir_path: str) -> tuple[str, list[str]]:
    executions = expand_executions(ir)
    ir_json = json.dumps(ir, indent=2, sort_keys=True)

    lines = [
        '"""Generated acceptance tests. Do not edit by hand.',
        "",
        f"Source IR: {ir_path}",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "import json",
        "",
        "from tests.acceptance import steps  # noqa: F401  (registers step handlers)",
        "from tests.acceptance.runtime import expand_executions, resolve_ir, run_execution",
        "",
        f"IR = json.loads({ir_json!r})",
        "",
        "",
        "def _run(execution_name: str) -> None:",
        "    ir = resolve_ir(IR)",
        "    executions = {e.execution_name: e for e in expand_executions(ir)}",
        "    run_execution(executions[execution_name])",
        "",
    ]

    function_names: list[str] = []
    for execution in executions:
        func_name = _function_name(execution)
        function_names.append(func_name)
        lines.append("")
        lines.append(f"def {func_name}() -> None:")
        lines.append(f"    _run({execution.execution_name!r})")

    return "\n".join(lines) + "\n", function_names


def generate(ir_path: Path, output_dir: Path) -> Path:
    ir = json.loads(ir_path.read_text())
    output_dir.mkdir(parents=True, exist_ok=True)
    init_file = output_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("")

    source, _function_names = _render(ir, str(ir_path))
    stem = ir_path.stem
    test_file = output_dir / f"test_{stem}.py"
    test_file.write_text(source)

    feature_path = f"features/{stem}.feature"
    metadata_dir = output_dir / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    metadata = {
        "schema_version": 1,
        "feature_path": feature_path,
        "ir_path": str(ir_path),
        "implementation_hash": f"sha256:{digest}",
        "hash_scope": "generated_files",
        "generated_files": [str(test_file)],
    }
    metadata_file = metadata_dir / _metadata_slug(feature_path)
    metadata_file.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")

    return test_file


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(
            "usage: acceptance-entrypoint-generator <json-ir> <generated-test-output>",
            file=sys.stderr,
        )
        return _EXIT_USAGE

    ir_path, output_dir = Path(argv[0]), Path(argv[1])
    try:
        generate(ir_path, output_dir)
    except Exception as exc:  # noqa: BLE001 - report any generation failure, exit 1
        print(f"error: {exc}", file=sys.stderr)
        return _EXIT_ERROR
    return _EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
