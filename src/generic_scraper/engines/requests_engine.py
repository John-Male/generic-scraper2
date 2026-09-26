from __future__ import annotations

import requests

from generic_scraper.config import ScraperType
from generic_scraper.engines.base import Transport
from generic_scraper.errors import TransientFetchError


class RequestsEngine:
    name = "requests"
    browser: str | None = None

    def __init__(self, config: ScraperType, transport: Transport | None = None) -> None:
        self._session = requests.Session()
        self.proxy: str | None = None
        if config.use_proxy and config.proxy_url and config.proxy_port:
            self.proxy = f"{config.proxy_url}:{config.proxy_port}"
            self._session.proxies = {"http": self.proxy, "https": self.proxy}
        if config.proxy_pass_key and config.proxy_pass_val:
            self._session.headers[config.proxy_pass_key] = config.proxy_pass_val
        self._transport = transport or self._default_transport

    def _default_transport(self, url: str) -> str:
        try:
            return str(self._session.get(url).text)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
            raise TransientFetchError(f"transient network error fetching {url}: {exc}") from exc

    def fetch(self, url: str) -> str:
        return self._transport(url)

    @property
    def headers(self) -> dict[str, str]:
        return dict(self._session.headers)

    def is_ready(self) -> bool:
        return self._session is not None
