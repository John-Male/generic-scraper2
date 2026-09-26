from __future__ import annotations

import random
import string

import pytest

from generic_scraper.processors.beautifulsoup_processor import BeautifulSoupProcessor
from generic_scraper.processors.html_parser_processor import HtmlParserProcessor
from generic_scraper.processors.lxml_processor import LxmlProcessor
from generic_scraper.processors.regex_processor import RegexProcessor
from tests.property.support import draw_text, for_each_trial

_PROCESSOR_CLASSES = (BeautifulSoupProcessor, LxmlProcessor, HtmlParserProcessor, RegexProcessor)
_TITLE_ALPHABET = string.ascii_letters + string.digits + " "


@pytest.mark.property
def test_every_processor_extracts_a_plain_title_consistently() -> None:
    def check(rng: random.Random) -> None:
        title = draw_text(rng, alphabet=_TITLE_ALPHABET, max_size=30).strip()
        if not title:
            return
        html = f"<html><head><title>{title}</title></head><body></body></html>"

        for processor_cls in _PROCESSOR_CLASSES:
            assert processor_cls().parse(html).title == title

    for_each_trial(check)
