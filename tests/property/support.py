"""Minimal, dependency-free property-testing support.

The project's allowed dependencies (see
``swarmforge/constitution/articles/project.prompt``) do not include a
property-testing library, so this is a small in-house harness: run a test
body against many independent, deterministically-seeded random draws. The
fixed seed keeps runs hermetic and reproducible while still exercising a
broad range of inputs.
"""

from __future__ import annotations

import random
import string
from collections.abc import Callable

TRIALS = 100
_SEED = 20260101


def draw_text(
    rng: random.Random,
    *,
    alphabet: str = string.ascii_lowercase,
    min_size: int = 1,
    max_size: int = 16,
) -> str:
    size = rng.randint(min_size, max_size)
    return "".join(rng.choice(alphabet) for _ in range(size))


def draw_choice(rng: random.Random, options: list[str]) -> str:
    return rng.choice(options)


def for_each_trial(
    body: Callable[[random.Random], None], *, trials: int = TRIALS, seed: int = _SEED
) -> None:
    """Run `body` once per trial against an independent, seeded RNG draw."""
    rng = random.Random(seed)
    for _ in range(trials):
        body(rng)
