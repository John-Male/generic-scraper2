from __future__ import annotations

from generic_scraper.engines.base import Engine, EngineFactory
from generic_scraper.engines.playwright_engine import PlaywrightEngine
from generic_scraper.engines.requests_engine import RequestsEngine
from generic_scraper.engines.selenium_engine import SeleniumEngine

ENGINE_REGISTRY: dict[str, EngineFactory] = {
    RequestsEngine.name: RequestsEngine,
    PlaywrightEngine.name: PlaywrightEngine,
    SeleniumEngine.name: SeleniumEngine,
}

__all__ = ["Engine", "EngineFactory", "ENGINE_REGISTRY"]
