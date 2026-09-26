from __future__ import annotations

import time
from collections.abc import Callable

from generic_scraper.config import ScraperType, load_scraper_type
from generic_scraper.document import ParsedDocument
from generic_scraper.engines import ENGINE_REGISTRY
from generic_scraper.engines.base import Transport
from generic_scraper.errors import TransientFetchError, UnsupportedScraperEngineError
from generic_scraper.processors import PROCESSOR_REGISTRY

AvailabilityCheck = Callable[[str], bool]

__all__ = [
    "ScraperType",
    "load_scraper_type",
    "Scraper",
    "UnsupportedScraperEngineError",
    "TransientFetchError",
]


def _assume_available(engine_name: str) -> bool:
    return True


def _select_engine_name(config: ScraperType, is_available: AvailabilityCheck) -> str:
    if config.scraper_engine not in ENGINE_REGISTRY:
        raise UnsupportedScraperEngineError(
            f"unsupported scraper_engine: {config.scraper_engine!r}"
        )
    tried = [config.scraper_engine]
    if is_available(config.scraper_engine):
        return config.scraper_engine
    if config.secondary and config.secondary in ENGINE_REGISTRY and config.secondary not in tried:
        tried.append(config.secondary)
        if is_available(config.secondary):
            return config.secondary
    if "requests" not in tried:
        tried.append("requests")
    if is_available("requests"):
        return "requests"
    raise UnsupportedScraperEngineError(f"no available engine; tried: {', '.join(tried)}")


class Scraper:
    def __init__(
        self,
        config: ScraperType,
        is_available: AvailabilityCheck = _assume_available,
        transport: Transport | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._config = config
        self._sleep = sleep
        engine_name = _select_engine_name(config, is_available)
        self._engine = ENGINE_REGISTRY[engine_name](config, transport)
        self._processor = (
            PROCESSOR_REGISTRY[config.processing_type]() if config.processing_type else None
        )

    @property
    def engine_name(self) -> str:
        return self._engine.name

    @property
    def processor_name(self) -> str | None:
        return self._processor.name if self._processor is not None else None

    @property
    def browser(self) -> str | None:
        return self._engine.browser

    @property
    def proxy(self) -> str | None:
        return self._engine.proxy

    @property
    def headers(self) -> dict[str, str]:
        return dict(self._engine.headers)

    def is_ready(self) -> bool:
        return self._engine.is_ready()

    def fetch_page(self, url: str) -> str:
        attempts = max(1, self._config.retry_attempts)
        last_error: TransientFetchError | None = None
        for attempt in range(attempts):
            try:
                return self._engine.fetch(url)
            except TransientFetchError as exc:
                last_error = exc
                if attempt < attempts - 1:
                    self._sleep(2**attempt)
        assert last_error is not None
        raise last_error

    def fetch(self, url: str) -> ParsedDocument:
        if self._processor is None:
            raise ValueError("processing_type must be configured to fetch and parse a page")
        html = self.fetch_page(url)
        return self._processor.parse(html)
