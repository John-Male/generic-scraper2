from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Protocol

from generic_scraper.config import ScraperType

Transport = Callable[[str], str]


class Engine(Protocol):
    name: str
    browser: str | None
    proxy: str | None

    @property
    def headers(self) -> Mapping[str, str]: ...

    def is_ready(self) -> bool: ...

    def fetch(self, url: str) -> str: ...


EngineFactory = Callable[[ScraperType, "Transport | None"], Engine]
