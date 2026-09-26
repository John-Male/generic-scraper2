from __future__ import annotations

from pathlib import Path

from tests.acceptance.registry import StepContext, given, then, when

FIXTURES_DIR = Path(__file__).resolve().parents[3] / "fixtures"


@given(r'a test URL "(?P<url>[^"]+)"')
def set_test_url(ctx: StepContext) -> None:
    ctx.world["test_url"] = ctx.match.group("url")
    fixture_html = (FIXTURES_DIR / "test-page.html").read_text()
    ctx.world["transport"] = lambda fetched_url: fixture_html


@when(r"I fetch the test URL")
def fetch_test_url(ctx: StepContext) -> None:
    ctx.world["document"] = ctx.world["scraper"].fetch(ctx.world["test_url"])


@then(r'the Scraper should return a parsed document using "<(?P<placeholder>[A-Za-z0-9_]+)>"')
def assert_parsed_with_processor(ctx: StepContext) -> None:
    expected_processor = ctx.example[ctx.match.group("placeholder")]
    assert ctx.world["scraper"].processor_name == expected_processor
    assert ctx.world["document"] is not None


@then(r"the parsed document should contain the page title")
def assert_document_has_title(ctx: StepContext) -> None:
    assert ctx.world["document"].title
