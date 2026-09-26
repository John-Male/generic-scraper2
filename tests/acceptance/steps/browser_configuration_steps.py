from __future__ import annotations

from tests.acceptance.registry import StepContext, then


@then(
    r'the Scraper should launch "<(?P<browser_placeholder>[A-Za-z0-9_]+)>" for'
    r' "<(?P<engine_placeholder>[A-Za-z0-9_]+)>"'
)
def assert_scraper_launches_browser(ctx: StepContext) -> None:
    expected_browser = ctx.example[ctx.match.group("browser_placeholder")]
    expected_engine = ctx.example[ctx.match.group("engine_placeholder")]
    scraper = ctx.world["scraper"]
    assert scraper.engine_name == expected_engine
    assert scraper.browser == expected_browser
