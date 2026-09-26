from __future__ import annotations

from generic_scraper.engines.browser_engine import NoDriverBrowserEngine


class SeleniumEngine(NoDriverBrowserEngine):
    name = "selenium"
