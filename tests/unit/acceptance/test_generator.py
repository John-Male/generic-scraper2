from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tests.acceptance import generator

SAMPLE_IR: dict[str, Any] = {
    "name": "Sample feature",
    "scenarios": [
        {
            "name": "sample-1",
            "steps": [{"keyword": "Given", "text": "a plain step"}],
            "examples": [{"value": "one"}, {"value": "two"}],
        }
    ],
}


def _write_ir(tmp_path: Path) -> Path:
    ir_path = tmp_path / "sample_feature.json"
    ir_path.write_text(json.dumps(SAMPLE_IR))
    return ir_path


def test_generate_writes_one_test_function_per_execution(tmp_path: Path) -> None:
    ir_path = _write_ir(tmp_path)
    output_dir = tmp_path / "generated"

    test_file = generator.generate(ir_path, output_dir)

    source = test_file.read_text()
    assert "def test_sample_1__example_1() -> None:" in source
    assert "def test_sample_1__example_2() -> None:" in source
    assert "_run('sample-1/example_1')" in source


def test_generate_embeds_the_ir_without_touching_feature_files(tmp_path: Path) -> None:
    ir_path = _write_ir(tmp_path)
    output_dir = tmp_path / "generated"

    test_file = generator.generate(ir_path, output_dir)

    source = test_file.read_text()
    assert "IR = json.loads(" in source
    assert "sample-1" in source
    assert ".feature" not in source.split("Source IR:")[0]


def test_generate_routes_through_resolve_ir_so_mutation_can_override_it(
    tmp_path: Path,
) -> None:
    ir_path = _write_ir(tmp_path)
    output_dir = tmp_path / "generated"

    test_file = generator.generate(ir_path, output_dir)

    source = test_file.read_text()
    assert "resolve_ir" in source
    assert "ir = resolve_ir(IR)" in source


def test_generate_writes_metadata_with_the_expected_schema(tmp_path: Path) -> None:
    ir_path = _write_ir(tmp_path)
    output_dir = tmp_path / "generated"

    test_file = generator.generate(ir_path, output_dir)

    metadata_file = output_dir / "metadata" / "features-sample-feature-feature.json"
    metadata = json.loads(metadata_file.read_text())

    assert metadata["schema_version"] == 1
    assert metadata["feature_path"] == "features/sample_feature.feature"
    assert metadata["hash_scope"] == "generated_files"
    assert metadata["generated_files"] == [str(test_file)]
    assert metadata["implementation_hash"].startswith("sha256:")


def test_generate_is_deterministic_for_a_fixed_ir(tmp_path: Path) -> None:
    ir_path = _write_ir(tmp_path)
    output_dir = tmp_path / "generated"

    first = generator.generate(ir_path, output_dir).read_text()
    second = generator.generate(ir_path, output_dir).read_text()

    assert first == second


def test_main_reports_usage_error_on_wrong_arg_count() -> None:
    assert generator.main(["only-one-arg"]) == 2


def test_main_reports_error_exit_code_on_missing_ir(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    output_dir = tmp_path / "generated"

    assert generator.main([str(missing), str(output_dir)]) == 1


def test_main_returns_ok_on_success(tmp_path: Path) -> None:
    ir_path = _write_ir(tmp_path)
    output_dir = tmp_path / "generated"

    assert generator.main([str(ir_path), str(output_dir)]) == 0
