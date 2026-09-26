from __future__ import annotations

import random

import pytest

from generic_scraper.errors import TransientFetchError
from generic_scraper.scraper import Scraper, ScraperType
from tests.property.support import for_each_trial


@pytest.mark.property
def test_fetch_page_retries_exactly_retry_attempts_times_with_exponential_backoff() -> None:
    def check(rng: random.Random) -> None:
        retry_attempts = rng.randint(1, 8)
        calls = {"n": 0}
        sleeps: list[float] = []

        def failing_transport(url: str) -> str:
            calls["n"] += 1
            raise TransientFetchError("simulated transient network error")

        scraper = Scraper(
            ScraperType(retry_attempts=retry_attempts),
            transport=failing_transport,
            sleep=sleeps.append,
        )

        with pytest.raises(TransientFetchError):
            scraper.fetch_page("https://example.com")

        assert calls["n"] == retry_attempts
        assert sleeps == [2**attempt for attempt in range(retry_attempts - 1)]

    for_each_trial(check)


@pytest.mark.property
def test_fetch_page_succeeds_once_the_transport_recovers_within_the_attempt_budget() -> None:
    def check(rng: random.Random) -> None:
        retry_attempts = rng.randint(1, 8)
        succeed_on_attempt = rng.randint(1, retry_attempts)
        calls = {"n": 0}
        sleeps: list[float] = []

        def flaky_transport(url: str) -> str:
            calls["n"] += 1
            if calls["n"] < succeed_on_attempt:
                raise TransientFetchError("simulated transient network error")
            return "ok"

        scraper = Scraper(
            ScraperType(retry_attempts=retry_attempts),
            transport=flaky_transport,
            sleep=sleeps.append,
        )

        result = scraper.fetch_page("https://example.com")

        assert result == "ok"
        assert calls["n"] == succeed_on_attempt
        assert len(sleeps) == succeed_on_attempt - 1

    for_each_trial(check)
