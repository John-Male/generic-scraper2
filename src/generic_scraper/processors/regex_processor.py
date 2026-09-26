from __future__ import annotations

import re

from generic_scraper.document import ParsedDocument

_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


class RegexProcessor:
    name = "regex"

    def parse(self, html: str) -> ParsedDocument:
        match = _TITLE_RE.search(html)
        return ParsedDocument(title=match.group(1).strip() if match else None)
