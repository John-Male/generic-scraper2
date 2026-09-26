from __future__ import annotations

import random
import string

import pytest

from generic_scraper.errors import UnsupportedScraperEngineError
from generic_scraper.scraper import Scraper, ScraperType
from tests.property.support import draw_choice, draw_text, for_each_trial

_REGISTERED_ENGINES = ["requests", "playwright", "selenium"]
_BROWSER_ENGINES = ["playwright", "selenium"]
_BROWSER_ALPHABET = string.ascii_lowercase


@pytest.mark.property
def test_scraper_uses_the_primary_engine_exactly_when_available() -> None:
    def check(rng: random.Random) -> None:
        engine = draw_choice(rng, _REGISTERED_ENGINES)
        available = rng.choice([True, False])

        def is_available(name: str) -> bool:
            return True if name == "requests" else available

        scraper = Scraper(ScraperType(scraper_engine=engine), is_available=is_available)

        assert scraper.engine_name == (engine if available else "requests")

    for_each_trial(check)


@pytest.mark.property
def test_scraper_reports_the_configured_browser_for_browser_engines() -> None:
    def check(rng: random.Random) -> None:
        engine = draw_choice(rng, _BROWSER_ENGINES)
        browser = draw_text(rng, alphabet=_BROWSER_ALPHABET, max_size=16)

        scraper = Scraper(ScraperType(scraper_engine=engine, browser_type=browser))

        assert scraper.browser == browser

    for_each_trial(check)


@pytest.mark.property
def test_requests_engine_never_reports_a_browser() -> None:
    def check(rng: random.Random) -> None:
        browser = draw_text(rng, alphabet=_BROWSER_ALPHABET, max_size=16)

        scraper = Scraper(ScraperType(scraper_engine="requests", browser_type=browser))

        assert scraper.browser is None

    for_each_trial(check)


@pytest.mark.property
def test_engine_selection_follows_the_primary_secondary_requests_fallback_chain() -> None:
    def check(rng: random.Random) -> None:
        primary = draw_choice(rng, _REGISTERED_ENGINES)
        secondary = rng.choice([None, *_REGISTERED_ENGINES])
        primary_available = rng.choice([True, False])
        secondary_available = rng.choice([True, False])
        requests_available = rng.choice([True, False])

        def is_available(name: str) -> bool:
            if name == primary:
                return primary_available
            if name == secondary:
                return secondary_available
            return requests_available

        config = ScraperType(scraper_engine=primary, secondary=secondary)

        if primary_available:
            expected: str | None = primary
        elif secondary and is_available(secondary):
            expected = secondary
        elif is_available("requests"):
            expected = "requests"
        else:
            expected = None

        if expected is None:
            with pytest.raises(UnsupportedScraperEngineError):
                Scraper(config, is_available=is_available)
        else:
            scraper = Scraper(config, is_available=is_available)
            assert scraper.engine_name == expected

    for_each_trial(check)
