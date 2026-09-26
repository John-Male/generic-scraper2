from __future__ import annotations

from typing import Any

from tests.acceptance import steps  # noqa: F401  (registers step handlers)
from tests.acceptance.registry import registry


def test_set_config_field_coerces_the_literal_false_to_a_bool() -> None:
    world: dict[str, Any] = {}

    registry.dispatch("given", '"use_proxy" set to "false"', world=world, example={})

    assert world["config"].use_proxy is False


def test_set_config_field_coerces_the_literal_true_to_a_bool() -> None:
    world: dict[str, Any] = {}

    registry.dispatch("given", '"use_proxy" set to "true"', world=world, example={})

    assert world["config"].use_proxy is True
