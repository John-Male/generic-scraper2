from __future__ import annotations

import random
import string

import pytest
import yaml

from generic_scraper.scraper import load_scraper_type
from tests.property.support import draw_text, for_each_trial

_ENGINE_ALPHABET = string.ascii_lowercase + "_"


@pytest.mark.property
def test_load_scraper_type_round_trips_through_a_dict() -> None:
    def check(rng: random.Random) -> None:
        engine = draw_text(rng, alphabet=_ENGINE_ALPHABET, max_size=24)

        config = load_scraper_type({"scraper_engine": engine})

        assert config.scraper_engine == engine

    for_each_trial(check)


@pytest.mark.property
def test_load_scraper_type_round_trips_through_yaml() -> None:
    def check(rng: random.Random) -> None:
        engine = draw_text(rng, alphabet=_ENGINE_ALPHABET, max_size=24)
        spec = yaml.safe_dump({"scraper_engine": engine})

        config = load_scraper_type(spec)

        assert config.scraper_engine == engine

    for_each_trial(check)


@pytest.mark.property
def test_load_scraper_type_agrees_between_dict_and_its_yaml_form() -> None:
    def check(rng: random.Random) -> None:
        engine = draw_text(rng, alphabet=_ENGINE_ALPHABET, max_size=24)

        from_dict = load_scraper_type({"scraper_engine": engine})
        from_yaml = load_scraper_type(yaml.safe_dump({"scraper_engine": engine}))

        assert from_dict == from_yaml

    for_each_trial(check)


@pytest.mark.property
def test_load_scraper_type_round_trips_an_optional_browser_type_through_yaml() -> None:
    def check(rng: random.Random) -> None:
        engine = draw_text(rng, alphabet=_ENGINE_ALPHABET, max_size=24)
        has_browser = rng.random() < 0.5
        browser = draw_text(rng, alphabet=_ENGINE_ALPHABET, max_size=16) if has_browser else None
        spec = yaml.safe_dump({"scraper_engine": engine, "browser_type": browser})

        config = load_scraper_type(spec)

        assert config.scraper_engine == engine
        assert config.browser_type == browser

    for_each_trial(check)
