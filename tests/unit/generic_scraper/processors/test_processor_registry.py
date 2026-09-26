from __future__ import annotations

import pytest

from generic_scraper.processors import PROCESSOR_REGISTRY


@pytest.mark.parametrize("processor", ["beautifulsoup", "lxml", "html.parser", "regex"])
def test_registry_maps_name_to_a_processor_reporting_that_name(processor: str) -> None:
    assert PROCESSOR_REGISTRY[processor]().name == processor
