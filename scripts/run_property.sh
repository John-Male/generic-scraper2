#!/usr/bin/env bash
# Property-only run: seeded, wide-range invariant tests. No codegen needed.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest -m property "$@"
