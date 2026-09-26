"""Runner adapter for gherkin-mutator's ``--runner-worker``.

Speaks the persistent worker protocol from Acceptance-Pipeline-Specification's
mutator-spec.md "Runner Adapter": one JSON job per input line, one JSON
response per output line, process reused across many mutation jobs.

Each job supplies a mutated IR file. This adapter points
``tests.acceptance.runtime.IR_OVERRIDE_ENV`` at that file and runs the
already-generated acceptance tests as a subprocess, so the same generated
entry points execute against each mutation without being regenerated.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, Protocol, TextIO

from tests.acceptance.runtime import IR_OVERRIDE_ENV

ROOT = Path(__file__).resolve().parents[2]


class _CompletedProcessLike(Protocol):
    returncode: int
    stdout: str
    stderr: str


Runner = Callable[..., _CompletedProcessLike]


def _parse_timeout(raw: str | None) -> float | None:
    if not raw:
        return None
    raw = raw.strip()
    if raw.endswith("ms"):
        return float(raw[:-2]) / 1000
    if raw.endswith("s"):
        raw = raw[:-1]
    return float(raw)


def _classify(returncode: int) -> str:
    if returncode == 0:
        return "test_success"
    if returncode == 1:
        return "test_failure"
    return "infrastructure_error"


def run_job(
    job: dict[str, Any], *, runner: Runner = subprocess.run, root: Path = ROOT
) -> dict[str, Any]:
    start = time.monotonic()
    timeout = _parse_timeout(job.get("timeout"))
    env = dict(os.environ)
    env[IR_OVERRIDE_ENV] = job["feature_json"]

    try:
        result = runner(
            [sys.executable, "-m", "pytest", job["generated_dir"], "-q"],
            cwd=str(root),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        duration = int((time.monotonic() - start) * 1e9)
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        return {
            "id": job["id"],
            "outcome": "infrastructure_error",
            "output": stdout,
            "error": f"timed out after {timeout}s",
            "duration": duration,
        }

    duration = int((time.monotonic() - start) * 1e9)
    return {
        "id": job["id"],
        "outcome": _classify(result.returncode),
        "output": result.stdout,
        "error": result.stderr,
        "duration": duration,
    }


def serve(
    stdin: TextIO = sys.stdin,
    stdout: TextIO = sys.stdout,
    run_job: Callable[[dict[str, Any]], dict[str, Any]] = run_job,
) -> int:
    for raw_line in stdin:
        line = raw_line.strip()
        if not line:
            continue
        job = json.loads(line)
        response = run_job(job)
        stdout.write(json.dumps(response) + "\n")
        stdout.flush()
    return 0


def main() -> int:
    return serve()


if __name__ == "__main__":
    raise SystemExit(main())
