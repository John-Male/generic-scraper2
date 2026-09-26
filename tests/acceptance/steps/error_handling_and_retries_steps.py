from __future__ import annotations

from generic_scraper.errors import TransientFetchError
from generic_scraper.scraper import Scraper
from tests.acceptance.registry import StepContext, given, then, when


@given(r"retry policy set to <(?P<placeholder>[A-Za-z0-9_]+)> attempts with exponential backoff")
def set_retry_policy(ctx: StepContext) -> None:
    attempts = int(ctx.example[ctx.match.group("placeholder")])
    ctx.world["config"].retry_attempts = attempts


@when(r"a transient network error occurs during fetch")
def transient_network_error_during_fetch(ctx: StepContext) -> None:
    calls = {"n": 0}

    def failing_transport(url: str) -> str:
        calls["n"] += 1
        raise TransientFetchError("simulated transient network error")

    scraper = Scraper(ctx.world["config"], transport=failing_transport, sleep=lambda seconds: None)
    ctx.world["scraper"] = scraper
    ctx.world["fetch_attempts"] = calls
    try:
        scraper.fetch_page("https://example.com")
    except TransientFetchError:
        pass


@then(r"the Scraper should retry up to <(?P<placeholder>[A-Za-z0-9_]+)> times before failing")
def assert_retried_up_to_attempts(ctx: StepContext) -> None:
    expected = int(ctx.example[ctx.match.group("placeholder")])
    assert ctx.world["fetch_attempts"]["n"] == expected


@then(r'the Scraper should attempt to use "(?P<engine>[A-Za-z0-9_]+)" as the secondary engine')
def assert_used_secondary_engine(ctx: StepContext) -> None:
    assert ctx.world["scraper"].engine_name == ctx.match.group("engine")


@then(r"the initialization should succeed")
def assert_initialization_succeeded(ctx: StepContext) -> None:
    assert "initialization_error" not in ctx.world
    assert ctx.world.get("scraper") is not None


@then(r'the Scraper initialization should fail with "<(?P<placeholder>[A-Za-z0-9_]+)>"')
def assert_initialization_failed_with(ctx: StepContext) -> None:
    expected_error_name = ctx.example[ctx.match.group("placeholder")]
    error = ctx.world.get("initialization_error")
    assert error is not None, "expected Scraper initialization to fail, but it succeeded"
    assert type(error).__name__ == expected_error_name
