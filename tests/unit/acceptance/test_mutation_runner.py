from __future__ import annotations

import io
import json
import subprocess
from pathlib import Path
from typing import Any

from tests.acceptance import mutation_runner
from tests.acceptance.runtime import IR_OVERRIDE_ENV


class _FakeCompleted:
    def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _job(**overrides: Any) -> dict[str, Any]:
    job = {
        "id": "m1",
        "feature_json": "/work/mutations/m1/feature.json",
        "generated_dir": "/work/generated",
        "work_dir": "/work/mutations/m1",
    }
    job.update(overrides)
    return job


def test_run_job_points_the_ir_override_env_at_the_mutated_feature_file() -> None:
    seen: dict[str, Any] = {}

    def fake_runner(cmd: list[str], **kwargs: Any) -> _FakeCompleted:
        seen["cmd"] = cmd
        seen["env"] = kwargs["env"]
        seen["cwd"] = kwargs["cwd"]
        return _FakeCompleted(0)

    mutation_runner.run_job(_job(), runner=fake_runner, root=Path("/repo"))

    assert seen["env"][IR_OVERRIDE_ENV] == "/work/mutations/m1/feature.json"
    assert seen["cwd"] == "/repo"
    assert seen["cmd"][-2:] == ["/work/generated", "-q"]


def test_run_job_classifies_passing_tests_as_test_success() -> None:
    def fake_runner(cmd: list[str], **kwargs: Any) -> _FakeCompleted:
        return _FakeCompleted(0, stdout="1 passed")

    response = mutation_runner.run_job(_job(), runner=fake_runner)

    assert response == {
        "id": "m1",
        "outcome": "test_success",
        "output": "1 passed",
        "error": "",
        "duration": response["duration"],
    }


def test_run_job_classifies_failing_tests_as_test_failure() -> None:
    def fake_runner(cmd: list[str], **kwargs: Any) -> _FakeCompleted:
        return _FakeCompleted(1, stdout="1 failed")

    response = mutation_runner.run_job(_job(), runner=fake_runner)

    assert response["outcome"] == "test_failure"


def test_run_job_classifies_other_exit_codes_as_infrastructure_error() -> None:
    def fake_runner(cmd: list[str], **kwargs: Any) -> _FakeCompleted:
        return _FakeCompleted(4, stderr="usage error")

    response = mutation_runner.run_job(_job(), runner=fake_runner)

    assert response["outcome"] == "infrastructure_error"
    assert response["error"] == "usage error"


def test_run_job_reports_timeout_as_infrastructure_error() -> None:
    def fake_runner(cmd: list[str], **kwargs: Any) -> Any:
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=kwargs["timeout"], output="partial")

    response = mutation_runner.run_job(_job(timeout="5s"), runner=fake_runner)

    assert response["outcome"] == "infrastructure_error"
    assert "timed out" in response["error"]
    assert response["output"] == "partial"


def test_parse_timeout_supports_seconds_milliseconds_and_bare_numbers() -> None:
    assert mutation_runner._parse_timeout(None) is None
    assert mutation_runner._parse_timeout("30s") == 30.0
    assert mutation_runner._parse_timeout("5000ms") == 5.0
    assert mutation_runner._parse_timeout("10") == 10.0


def test_serve_reads_newline_delimited_jobs_and_writes_newline_delimited_responses() -> None:
    jobs = [_job(id="m1"), _job(id="m2")]
    stdin = io.StringIO("\n".join(json.dumps(j) for j in jobs) + "\n")
    stdout = io.StringIO()

    def fake_run_job(job: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": job["id"],
            "outcome": "test_success",
            "output": "",
            "error": "",
            "duration": 0,
        }

    exit_code = mutation_runner.serve(stdin=stdin, stdout=stdout, run_job=fake_run_job)

    responses = [json.loads(line) for line in stdout.getvalue().splitlines()]
    assert exit_code == 0
    assert [r["id"] for r in responses] == ["m1", "m2"]


def test_serve_skips_blank_lines() -> None:
    stdin = io.StringIO("\n" + json.dumps(_job()) + "\n\n")
    stdout = io.StringIO()

    def fake_run_job(job: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": job["id"],
            "outcome": "test_success",
            "output": "",
            "error": "",
            "duration": 0,
        }

    mutation_runner.serve(stdin=stdin, stdout=stdout, run_job=fake_run_job)

    responses = [json.loads(line) for line in stdout.getvalue().splitlines()]
    assert len(responses) == 1
