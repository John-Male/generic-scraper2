from __future__ import annotations

import random
import string

import pytest

from generic_scraper.config import ScraperType
from generic_scraper.engines.requests_engine import RequestsEngine
from tests.property.support import draw_text, for_each_trial

_URL_ALPHABET = string.ascii_lowercase + string.digits
_HEADER_ALPHABET = string.ascii_uppercase + "-"


@pytest.mark.property
def test_proxy_is_the_joined_url_and_port_when_use_proxy_is_true() -> None:
    def check(rng: random.Random) -> None:
        url = draw_text(rng, alphabet=_URL_ALPHABET, max_size=20)
        port = draw_text(rng, alphabet=string.digits, min_size=1, max_size=5)
        engine = RequestsEngine(ScraperType(use_proxy=True, proxy_url=url, proxy_port=port))

        assert engine.proxy == f"{url}:{port}"

    for_each_trial(check)


@pytest.mark.property
def test_proxy_is_none_when_use_proxy_is_false_regardless_of_url_and_port() -> None:
    def check(rng: random.Random) -> None:
        url = draw_text(rng, alphabet=_URL_ALPHABET, max_size=20)
        port = draw_text(rng, alphabet=string.digits, min_size=1, max_size=5)
        engine = RequestsEngine(ScraperType(use_proxy=False, proxy_url=url, proxy_port=port))

        assert engine.proxy is None

    for_each_trial(check)


@pytest.mark.property
def test_pass_key_header_is_included_exactly_when_both_key_and_value_are_set() -> None:
    def check(rng: random.Random) -> None:
        key = draw_text(rng, alphabet=_HEADER_ALPHABET, max_size=16)
        val = draw_text(rng, alphabet=_URL_ALPHABET, max_size=20)
        engine = RequestsEngine(ScraperType(proxy_pass_key=key, proxy_pass_val=val))

        assert engine.headers[key] == val

    for_each_trial(check)


@pytest.mark.property
def test_no_pass_key_header_when_either_key_or_value_is_missing() -> None:
    def check(rng: random.Random) -> None:
        key = draw_text(rng, alphabet=_HEADER_ALPHABET, max_size=16)
        keep_key = rng.choice([True, False])
        config = ScraperType(
            proxy_pass_key=key if keep_key else None,
            proxy_pass_val=None if keep_key else draw_text(rng, alphabet=_URL_ALPHABET),
        )

        engine = RequestsEngine(config)

        assert key not in engine.headers

    for_each_trial(check)
