from __future__ import annotations

import subprocess
from pathlib import Path

from tests.acceptance.generator import generate

ROOT = Path(__file__).resolve().parent
FEATURES_DIR = ROOT / "features"
IR_DIR = ROOT / "tests" / "acceptance" / "build" / "ir"
GENERATED_DIR = ROOT / "tests" / "acceptance" / "generated"

# One entry per feature the coder has shipped step handlers for. A feature
# without handlers would generate acceptance tests that fail with "no step
# handler matched", turning an unimplemented slice into a red suite.
ACTIVE_FEATURES = [
    "01_initialize_scraper.feature",
    "02_browser_configuration.feature",
    "03_defaults_and_fallbacks.feature",
    "04_proxy_and_headers.feature",
    "05_processing_types.feature",
    "06_end_to_end_fetch_parse.feature",
    "07_distributed_execution_and_artifacts.feature",
    "08_error_handling_and_retries.feature",
]


def pytest_configure(config: object) -> None:
    IR_DIR.mkdir(parents=True, exist_ok=True)
    for name in ACTIVE_FEATURES:
        feature_file = FEATURES_DIR / name
        ir_path = IR_DIR / f"{feature_file.stem}.json"
        subprocess.run(["gherkin-parser", str(feature_file), str(ir_path)], check=True)
        generate(ir_path, GENERATED_DIR)
