from __future__ import annotations

from tests.acceptance.registry import StepContext, given, then


@given(
    r'"<(?P<placeholder>[A-Za-z0-9_]+)>" is not available on the worker node'
    r'|"<(?P<placeholder2>[A-Za-z0-9_]+)>" fails to start on the worker'
)
def mark_engine_unavailable(ctx: StepContext) -> None:
    placeholder = ctx.match.group("placeholder") or ctx.match.group("placeholder2")
    engine_name = ctx.example[placeholder]
    unavailable = ctx.world.get("unavailable_engines", frozenset())
    ctx.world["unavailable_engines"] = unavailable | {engine_name}


@then(r'the Scraper should use "(?P<value>[A-Za-z0-9_]+)" as the default scraper engine')
def assert_default_scraper_engine(ctx: StepContext) -> None:
    assert ctx.world["scraper"].engine_name == ctx.match.group("value")


@then(r"the Scraper should have no browser configured")
def assert_no_browser_configured(ctx: StepContext) -> None:
    assert ctx.world["scraper"].browser is None


@then(r'the Scraper should fall back to "(?P<value>[A-Za-z0-9_]+)"')
def assert_scraper_falls_back_to(ctx: StepContext) -> None:
    assert ctx.world["scraper"].engine_name == ctx.match.group("value")
