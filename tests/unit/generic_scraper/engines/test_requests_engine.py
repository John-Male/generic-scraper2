from __future__ import annotations

import pytest
import requests

from generic_scraper.config import ScraperType
from generic_scraper.engines.requests_engine import RequestsEngine
from generic_scraper.errors import TransientFetchError


def test_requests_engine_reports_its_name() -> None:
    assert RequestsEngine.name == "requests"


def test_requests_engine_is_ready_after_construction() -> None:
    engine = RequestsEngine(ScraperType())

    assert engine.is_ready() is True


def test_requests_engine_configures_the_proxy_when_use_proxy_is_set() -> None:
    config = ScraperType(use_proxy=True, proxy_url="http://proxy.example", proxy_port="8080")

    engine = RequestsEngine(config)

    assert engine.proxy == "http://proxy.example:8080"


def test_requests_engine_has_no_proxy_by_default() -> None:
    engine = RequestsEngine(ScraperType())

    assert engine.proxy is None


def test_requests_engine_includes_the_pass_key_header_when_configured() -> None:
    config = ScraperType(proxy_pass_key="X-Proxy-Auth", proxy_pass_val="dummy-token-abc")

    engine = RequestsEngine(config)

    assert engine.headers["X-Proxy-Auth"] == "dummy-token-abc"


def test_requests_engine_fetch_uses_the_injected_transport() -> None:
    engine = RequestsEngine(ScraperType(), transport=lambda url: f"content for {url}")

    assert engine.fetch("https://example.com") == "content for https://example.com"


@pytest.mark.parametrize(
    "raised",
    [requests.exceptions.ConnectionError("boom"), requests.exceptions.Timeout("boom")],
)
def test_requests_engine_translates_connection_errors_to_transient_fetch_error(
    raised: Exception,
) -> None:
    engine = RequestsEngine(ScraperType())

    def raise_it(url: str) -> str:
        raise raised

    engine._session.get = raise_it

    with pytest.raises(TransientFetchError):
        engine.fetch("https://example.com")
