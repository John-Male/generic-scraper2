from __future__ import annotations

from lxml import html as lxml_html

from generic_scraper.document import ParsedDocument


class LxmlProcessor:
    name = "lxml"

    def parse(self, html: str) -> ParsedDocument:
        tree = lxml_html.fromstring(html)
        titles = tree.xpath("//title/text()")
        return ParsedDocument(title=str(titles[0]) if titles else None)
