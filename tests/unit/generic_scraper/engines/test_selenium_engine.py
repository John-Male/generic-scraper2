from __future__ import annotations

import pytest

from generic_scraper.config import ScraperType
from generic_scraper.engines.selenium_engine import SeleniumEngine


def test_selenium_engine_reports_its_name() -> None:
    assert SeleniumEngine.name == "selenium"


def test_selenium_engine_is_ready_after_construction() -> None:
    engine = SeleniumEngine(ScraperType())

    assert engine.is_ready() is True


def test_selenium_engine_records_the_configured_browser() -> None:
    engine = SeleniumEngine(ScraperType(browser_type="firefox"))

    assert engine.browser == "firefox"


def test_selenium_engine_fetch_uses_the_injected_transport() -> None:
    engine = SeleniumEngine(ScraperType(), transport=lambda url: f"content for {url}")

    assert engine.fetch("https://example.com") == "content for https://example.com"


def test_selenium_engine_fetch_without_a_transport_is_not_implemented() -> None:
    engine = SeleniumEngine(ScraperType())

    with pytest.raises(NotImplementedError):
        engine.fetch("https://example.com")
