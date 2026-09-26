from __future__ import annotations

import pytest

from generic_scraper.processors.beautifulsoup_processor import BeautifulSoupProcessor
from generic_scraper.processors.html_parser_processor import HtmlParserProcessor
from generic_scraper.processors.lxml_processor import LxmlProcessor
from generic_scraper.processors.regex_processor import RegexProcessor

_HTML = """
<!DOCTYPE html>
<html>
<head><title>Test Page Title</title></head>
<body><h1>Hello</h1></body>
</html>
"""


@pytest.mark.parametrize(
    "processor_cls",
    [BeautifulSoupProcessor, LxmlProcessor, HtmlParserProcessor, RegexProcessor],
)
def test_processor_extracts_the_page_title(processor_cls: type) -> None:
    document = processor_cls().parse(_HTML)

    assert document.title == "Test Page Title"


@pytest.mark.parametrize(
    "processor_cls",
    [BeautifulSoupProcessor, LxmlProcessor, HtmlParserProcessor, RegexProcessor],
)
def test_processor_reports_no_title_when_absent(processor_cls: type) -> None:
    document = processor_cls().parse("<html><body>no title here</body></html>")

    assert document.title is None
