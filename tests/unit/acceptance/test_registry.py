from __future__ import annotations

import pytest

from tests.acceptance.registry import StepContext, StepRegistry


def test_dispatch_routes_to_the_matching_handler_by_keyword_and_text() -> None:
    registry = StepRegistry()
    received: list[StepContext] = []

    @registry.given(r'a "<(?P<placeholder>[a-z]+)>" thing')
    def _handler(ctx: StepContext) -> None:
        received.append(ctx)

    registry.dispatch("given", 'a "<color>" thing', world={}, example={"color": "red"})

    assert len(received) == 1
    assert received[0].match.group("placeholder") == "color"
    assert received[0].example == {"color": "red"}


def test_dispatch_only_matches_within_the_same_keyword() -> None:
    registry = StepRegistry()

    @registry.given(r"a shared phrase")
    def _given_handler(ctx: StepContext) -> None:
        raise AssertionError("given handler should not run for a then dispatch")

    with pytest.raises(AssertionError, match="no 'then' step handler matched"):
        registry.dispatch("then", "a shared phrase", world={}, example={})


def test_dispatch_raises_on_no_match() -> None:
    registry = StepRegistry()

    with pytest.raises(AssertionError, match="no 'given' step handler matched: 'unknown step'"):
        registry.dispatch("given", "unknown step", world={}, example={})


def test_world_is_passed_through_to_the_handler() -> None:
    registry = StepRegistry()
    world = {"count": 0}

    @registry.when(r"count is incremented")
    def _handler(ctx: StepContext) -> None:
        ctx.world["count"] += 1

    registry.dispatch("when", "count is incremented", world=world, example={})

    assert world["count"] == 1
