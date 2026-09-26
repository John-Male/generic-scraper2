#!/usr/bin/env bash
# Normal acceptance run: parse -> generate -> execute, acceptance tests only.
# Codegen is triggered by the root conftest.py's pytest_configure hook, so a
# plain `pytest` run also regenerates and runs these tests.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest tests/acceptance "$@"
