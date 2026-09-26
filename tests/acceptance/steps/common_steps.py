from __future__ import annotations

import re

from generic_scraper.scraper import ScraperType
from tests.acceptance.registry import StepContext, given, then

_PLACEHOLDER = re.compile(r"<([A-Za-z0-9_]+)>")


def _resolve_field_value(raw: str, example: dict[str, str]) -> str | bool:
    placeholder = _PLACEHOLDER.fullmatch(raw)
    value = example[placeholder.group(1)] if placeholder else raw
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    return value


@given(r"default scraper configuration exists|I have an empty ScraperType configuration")
def default_configuration_exists(ctx: StepContext) -> None:
    ctx.world["config"] = ScraperType()


@then(r'the ScraperType should have "(?P<key>[A-Za-z_]+)" set to "(?P<value>[^"]+)"')
def assert_scraper_type_field(ctx: StepContext) -> None:
    key = ctx.match.group("key")
    value = ctx.match.group("value")
    assert getattr(ctx.world["config"], key) == value


@given(
    r'(?:I have a ScraperType configuration with )?"(?P<key>[A-Za-z_]+)" set to'
    r' "(?P<value>[^"]+)"'
)
def set_config_field(ctx: StepContext) -> None:
    key = ctx.match.group("key")
    raw_value = ctx.match.group("value")
    config = ctx.world.setdefault("config", ScraperType())
    setattr(config, key, _resolve_field_value(raw_value, ctx.example))
