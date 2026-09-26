from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

StepHandler = Callable[["StepContext"], None]


@dataclass
class StepContext:
    world: dict[str, Any]
    example: dict[str, str]
    match: re.Match[str]


@dataclass
class _Pattern:
    keyword: str
    regex: re.Pattern[str]
    handler: StepHandler


class StepRegistry:
    """Maps Gherkin step text to project step handlers by keyword and regex.

    Step text is matched as written in the IR, placeholders and all (e.g.
    ``"<engine>"``), so one handler can cover every example row for a step
    shape. The handler resolves the actual value itself, from the captured
    placeholder name, looked up in the current example row.
    """

    def __init__(self) -> None:
        self._patterns: list[_Pattern] = []

    def _register(self, keyword: str, pattern: str) -> Callable[[StepHandler], StepHandler]:
        compiled = re.compile(pattern)

        def decorator(func: StepHandler) -> StepHandler:
            self._patterns.append(_Pattern(keyword, compiled, func))
            return func

        return decorator

    def given(self, pattern: str) -> Callable[[StepHandler], StepHandler]:
        return self._register("given", pattern)

    def when(self, pattern: str) -> Callable[[StepHandler], StepHandler]:
        return self._register("when", pattern)

    def then(self, pattern: str) -> Callable[[StepHandler], StepHandler]:
        return self._register("then", pattern)

    def dispatch(
        self, keyword: str, text: str, world: dict[str, Any], example: dict[str, str]
    ) -> None:
        for pattern in self._patterns:
            if pattern.keyword != keyword:
                continue
            match = pattern.regex.fullmatch(text)
            if match is not None:
                pattern.handler(StepContext(world=world, example=example, match=match))
                return
        raise AssertionError(f"no {keyword!r} step handler matched: {text!r}")


registry = StepRegistry()
given = registry.given
when = registry.when
then = registry.then
