from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import yaml


@dataclass
class ScraperType:
    scraper_engine: str = "requests"
    browser_type: str | None = None
    use_proxy: bool = False
    proxy_url: str | None = None
    proxy_port: str | None = None
    proxy_pass_key: str | None = None
    proxy_pass_val: str | None = None
    processing_type: str | None = None
    secondary: str | None = None
    retry_attempts: int = 1


def load_scraper_type(spec: dict[str, Any] | str) -> ScraperType:
    data = yaml.safe_load(spec) if isinstance(spec, str) else spec
    return ScraperType(**(data or {}))
