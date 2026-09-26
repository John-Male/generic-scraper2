from __future__ import annotations

import pytest

from generic_scraper.errors import TransientFetchError, UnsupportedScraperEngineError
from generic_scraper.scraper import Scraper, ScraperType, load_scraper_type


@pytest.mark.parametrize("engine", ["requests", "playwright", "selenium"])
def test_scraper_uses_the_configured_engine(engine: str) -> None:
    scraper = Scraper(ScraperType(scraper_engine=engine))

    assert scraper.engine_name == engine


@pytest.mark.parametrize("engine", ["requests", "playwright", "selenium"])
def test_scraper_is_ready_to_fetch_pages(engine: str) -> None:
    scraper = Scraper(ScraperType(scraper_engine=engine))

    assert scraper.is_ready() is True


def test_scraper_type_defaults_to_requests_engine() -> None:
    assert ScraperType().scraper_engine == "requests"


def test_load_scraper_type_from_dict() -> None:
    config = load_scraper_type({"scraper_engine": "requests"})

    assert config.scraper_engine == "requests"


def test_load_scraper_type_from_yaml() -> None:
    config = load_scraper_type("scraper_engine: requests\n")

    assert config.scraper_engine == "requests"


def test_scraper_type_defaults_to_no_browser() -> None:
    assert ScraperType().browser_type is None


@pytest.mark.parametrize("engine", ["playwright", "selenium"])
@pytest.mark.parametrize("browser", ["chrome", "firefox"])
def test_scraper_launches_the_configured_browser(engine: str, browser: str) -> None:
    scraper = Scraper(ScraperType(scraper_engine=engine, browser_type=browser))

    assert scraper.browser == browser


def test_scraper_has_no_browser_for_requests_engine() -> None:
    scraper = Scraper(ScraperType(scraper_engine="requests"))

    assert scraper.browser is None


@pytest.mark.parametrize("engine", ["playwright", "selenium"])
def test_scraper_falls_back_to_requests_when_primary_unavailable(engine: str) -> None:
    scraper = Scraper(ScraperType(scraper_engine=engine), is_available=lambda name: name != engine)

    assert scraper.engine_name == "requests"


def test_scraper_uses_primary_engine_when_available() -> None:
    scraper = Scraper(ScraperType(scraper_engine="playwright"), is_available=lambda name: True)

    assert scraper.engine_name == "playwright"


def test_scraper_has_no_proxy_by_default() -> None:
    scraper = Scraper(ScraperType())

    assert scraper.proxy is None


def test_scraper_configures_the_proxy_when_use_proxy_is_set() -> None:
    config = ScraperType(use_proxy=True, proxy_url="http://proxy.example", proxy_port="8080")

    scraper = Scraper(config)

    assert scraper.proxy == "http://proxy.example:8080"


def test_scraper_does_not_configure_the_proxy_when_use_proxy_is_false() -> None:
    config = ScraperType(use_proxy=False, proxy_url="http://proxy.example", proxy_port="8080")

    scraper = Scraper(config)

    assert scraper.proxy is None


def test_scraper_includes_the_pass_key_header_when_configured() -> None:
    config = ScraperType(proxy_pass_key="X-Proxy-Auth", proxy_pass_val="dummy-token-abc")

    scraper = Scraper(config)

    assert scraper.headers["X-Proxy-Auth"] == "dummy-token-abc"


def test_scraper_has_no_pass_key_header_by_default() -> None:
    scraper = Scraper(ScraperType())

    assert "X-Proxy-Auth" not in scraper.headers


@pytest.mark.parametrize("processor", ["beautifulsoup", "lxml", "html.parser", "regex"])
def test_scraper_uses_the_configured_processor(processor: str) -> None:
    scraper = Scraper(ScraperType(processing_type=processor))

    assert scraper.processor_name == processor


def test_scraper_has_no_processor_by_default() -> None:
    scraper = Scraper(ScraperType())

    assert scraper.processor_name is None


def test_scraper_fetch_returns_a_parsed_document_via_the_configured_processor() -> None:
    html = "<html><head><title>Injected Title</title></head><body></body></html>"
    scraper = Scraper(
        ScraperType(processing_type="beautifulsoup"),
        transport=lambda url: html,
    )

    document = scraper.fetch("https://example.com")

    assert document.title == "Injected Title"


def test_scraper_fetch_raises_without_a_configured_processor() -> None:
    scraper = Scraper(ScraperType(), transport=lambda url: "<html></html>")

    with pytest.raises(ValueError, match="processing_type"):
        scraper.fetch("https://example.com")


def test_scraper_type_defaults_to_no_secondary_engine() -> None:
    assert ScraperType().secondary is None


def test_scraper_type_defaults_to_one_retry_attempt() -> None:
    assert ScraperType().retry_attempts == 1


def test_scraper_falls_back_to_secondary_when_primary_unavailable() -> None:
    config = ScraperType(scraper_engine="playwright", secondary="selenium")

    scraper = Scraper(config, is_available=lambda name: name == "selenium")

    assert scraper.engine_name == "selenium"


def test_scraper_falls_back_to_requests_when_primary_and_secondary_unavailable() -> None:
    config = ScraperType(scraper_engine="playwright", secondary="selenium")

    scraper = Scraper(config, is_available=lambda name: name == "requests")

    assert scraper.engine_name == "requests"


def test_scraper_raises_for_an_unregistered_scraper_engine() -> None:
    config = ScraperType(scraper_engine="unknown")

    with pytest.raises(UnsupportedScraperEngineError, match="unknown"):
        Scraper(config)


def test_scraper_raises_for_an_unregistered_engine_even_if_assumed_available() -> None:
    config = ScraperType(scraper_engine="unknown")

    with pytest.raises(UnsupportedScraperEngineError):
        Scraper(config, is_available=lambda name: True)


def test_scraper_raises_when_the_entire_fallback_chain_is_exhausted() -> None:
    config = ScraperType(scraper_engine="playwright", secondary="selenium")

    expected = "tried: playwright, selenium, requests"
    with pytest.raises(UnsupportedScraperEngineError, match=expected):
        Scraper(config, is_available=lambda name: False)


def test_scraper_raises_without_duplicating_requests_already_tried_as_primary() -> None:
    config = ScraperType(scraper_engine="requests")

    with pytest.raises(UnsupportedScraperEngineError, match="tried: requests$"):
        Scraper(config, is_available=lambda name: False)


def test_scraper_raises_without_duplicating_a_secondary_equal_to_the_primary() -> None:
    config = ScraperType(scraper_engine="playwright", secondary="playwright")

    expected = "tried: playwright, requests"
    with pytest.raises(UnsupportedScraperEngineError, match=expected):
        Scraper(config, is_available=lambda name: False)


def test_scraper_fetch_page_retries_on_transient_errors_up_to_the_configured_attempts() -> None:
    calls = {"n": 0}

    def failing_transport(url: str) -> str:
        calls["n"] += 1
        raise TransientFetchError("simulated transient network error")

    scraper = Scraper(
        ScraperType(retry_attempts=3),
        transport=failing_transport,
        sleep=lambda seconds: None,
    )

    with pytest.raises(TransientFetchError):
        scraper.fetch_page("https://example.com")

    assert calls["n"] == 3


def test_scraper_fetch_page_succeeds_after_a_transient_error_recovers() -> None:
    calls = {"n": 0}

    def flaky_transport(url: str) -> str:
        calls["n"] += 1
        if calls["n"] < 2:
            raise TransientFetchError("simulated transient network error")
        return "<html></html>"

    scraper = Scraper(
        ScraperType(retry_attempts=3),
        transport=flaky_transport,
        sleep=lambda seconds: None,
    )

    html = scraper.fetch_page("https://example.com")

    assert html == "<html></html>"
    assert calls["n"] == 2


def test_scraper_fetch_page_sleeps_between_retries_but_not_after_the_last_attempt() -> None:
    sleeps: list[float] = []

    def failing_transport(url: str) -> str:
        raise TransientFetchError("simulated transient network error")

    scraper = Scraper(
        ScraperType(retry_attempts=3),
        transport=failing_transport,
        sleep=sleeps.append,
    )

    with pytest.raises(TransientFetchError):
        scraper.fetch_page("https://example.com")

    assert len(sleeps) == 2


def test_scraper_fetch_page_does_not_retry_by_default() -> None:
    calls = {"n": 0}

    def failing_transport(url: str) -> str:
        calls["n"] += 1
        raise TransientFetchError("simulated transient network error")

    scraper = Scraper(ScraperType(), transport=failing_transport, sleep=lambda seconds: None)

    with pytest.raises(TransientFetchError):
        scraper.fetch_page("https://example.com")

    assert calls["n"] == 1
