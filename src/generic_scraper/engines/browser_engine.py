from __future__ import annotations

from generic_scraper.config import ScraperType
from generic_scraper.engines.base import Transport


class NoDriverBrowserEngine:
    """Shared machinery for browser engines with no real driver wired up yet.

    Playwright and Selenium report readiness and browser configuration
    identically, and both raise the same error on an unfaked fetch; only
    `name` differs. Subclasses set `name` and nothing else.
    """

    name: str
    proxy: str | None = None

    def __init__(self, config: ScraperType, transport: Transport | None = None) -> None:
        self.browser = config.browser_type
        self.headers: dict[str, str] = {}
        self._transport = transport or self._default_transport

    def _default_transport(self, url: str) -> str:
        raise NotImplementedError(
            f"{type(self).__name__} has no real browser driver wired up yet; "
            "inject a transport to fetch in tests"
        )

    def fetch(self, url: str) -> str:
        return self._transport(url)

    def is_ready(self) -> bool:
        return True
