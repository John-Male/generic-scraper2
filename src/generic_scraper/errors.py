from __future__ import annotations


class UnsupportedScraperEngineError(Exception):
    """Raised when ScraperType.scraper_engine names an engine that isn't registered."""


class TransientFetchError(Exception):
    """Raised by an engine's fetch when a transient (retryable) error occurs."""
