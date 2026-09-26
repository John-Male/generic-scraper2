from __future__ import annotations

from typing import Any

import pytest

from tests.acceptance import steps  # noqa: F401  (registers step handlers)
from tests.acceptance.registry import registry


def test_build_scraper_spec_rejects_an_unsupported_format() -> None:
    with pytest.raises(AssertionError, match="unsupported spec format: 'xml'"):
        registry.dispatch(
            "given",
            'a scraper spec in "<format>" format with "scraper_engine" set to "requests"',
            world={},
            example={"format": "xml"},
        )


def test_set_scraper_engine_creates_a_config_when_none_exists() -> None:
    world: dict[str, Any] = {}

    registry.dispatch(
        "given",
        'I have a ScraperType configuration with "scraper_engine" set to "<engine>"',
        world=world,
        example={"engine": "playwright"},
    )

    assert world["config"].scraper_engine == "playwright"
