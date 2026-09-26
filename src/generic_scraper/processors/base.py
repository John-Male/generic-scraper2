from __future__ import annotations

from typing import Protocol

from generic_scraper.document import ParsedDocument


class Processor(Protocol):
    name: str

    def parse(self, html: str) -> ParsedDocument: ...
