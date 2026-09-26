from __future__ import annotations

from tests.acceptance.registry import StepContext, then


@then(r'the Scraper should use "<(?P<placeholder>[A-Za-z0-9_]+)>" to parse HTML responses')
def assert_scraper_uses_processor(ctx: StepContext) -> None:
    expected_processor = ctx.example[ctx.match.group("placeholder")]
    assert ctx.world["scraper"].processor_name == expected_processor
