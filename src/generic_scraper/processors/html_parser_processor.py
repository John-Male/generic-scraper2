from __future__ import annotations

from html.parser import HTMLParser

from generic_scraper.document import ParsedDocument


class _TitleExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_title = False
        self.title: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title = data


class HtmlParserProcessor:
    name = "html.parser"

    def parse(self, html: str) -> ParsedDocument:
        extractor = _TitleExtractor()
        extractor.feed(html)
        return ParsedDocument(title=extractor.title)
