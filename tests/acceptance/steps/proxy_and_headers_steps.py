from __future__ import annotations

from tests.acceptance.registry import StepContext, then


@then(
    r'the Scraper should configure the HTTP client to use the proxy'
    r' "<(?P<url_placeholder>[A-Za-z0-9_]+)>:<(?P<port_placeholder>[A-Za-z0-9_]+)>"'
)
def assert_scraper_configures_proxy(ctx: StepContext) -> None:
    url = ctx.example[ctx.match.group("url_placeholder")]
    port = ctx.example[ctx.match.group("port_placeholder")]
    assert ctx.world["scraper"].proxy == f"{url}:{port}"


@then(
    r'the Scraper should include header "<(?P<key_placeholder>[A-Za-z0-9_]+)>:'
    r' <(?P<val_placeholder>[A-Za-z0-9_]+)>" on proxied requests'
)
def assert_scraper_includes_header(ctx: StepContext) -> None:
    key = ctx.example[ctx.match.group("key_placeholder")]
    val = ctx.example[ctx.match.group("val_placeholder")]
    assert ctx.world["scraper"].headers.get(key) == val
