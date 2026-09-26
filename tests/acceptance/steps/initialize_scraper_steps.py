from __future__ import annotations

import yaml

from generic_scraper.scraper import Scraper, load_scraper_type
from tests.acceptance.registry import StepContext, given, then, when


@given(
    r'a scraper spec in "<(?P<placeholder>[A-Za-z0-9_]+)>" format with'
    r' "(?P<key>[A-Za-z_]+)" set to "(?P<value>[^"]+)"'
)
def build_scraper_spec(ctx: StepContext) -> None:
    format_ = ctx.example[ctx.match.group("placeholder")]
    field = {ctx.match.group("key"): ctx.match.group("value")}
    if format_ == "dict":
        ctx.world["spec"] = field
    elif format_ == "yaml":
        ctx.world["spec"] = yaml.safe_dump(field)
    else:
        raise AssertionError(f"unsupported spec format: {format_!r}")


@when(r"I initialize the Scraper")
def initialize_scraper(ctx: StepContext) -> None:
    unavailable = ctx.world.get("unavailable_engines", frozenset())
    try:
        ctx.world["scraper"] = Scraper(
            ctx.world["config"],
            is_available=lambda name: name not in unavailable,
            transport=ctx.world.get("transport"),
        )
    except Exception as exc:  # captured for "should fail with" assertions
        ctx.world["initialization_error"] = exc


@when(r"I load the ScraperType configuration from the spec")
def load_scraper_type_from_spec(ctx: StepContext) -> None:
    ctx.world["config"] = load_scraper_type(ctx.world["spec"])


@then(r'the Scraper should use the "<(?P<placeholder>[A-Za-z0-9_]+)>" engine')
def assert_scraper_uses_engine(ctx: StepContext) -> None:
    placeholder = ctx.match.group("placeholder")
    expected_engine = ctx.example[placeholder]
    assert ctx.world["scraper"].engine_name == expected_engine


@then(r"the Scraper should be ready to fetch pages")
def assert_scraper_is_ready(ctx: StepContext) -> None:
    assert ctx.world["scraper"].is_ready() is True
