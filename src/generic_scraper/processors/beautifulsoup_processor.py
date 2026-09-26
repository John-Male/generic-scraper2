from __future__ import annotations

from bs4 import BeautifulSoup

from generic_scraper.document import ParsedDocument


class BeautifulSoupProcessor:
    name = "beautifulsoup"

    def parse(self, html: str) -> ParsedDocument:
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string if soup.title else None
        return ParsedDocument(title=title)
