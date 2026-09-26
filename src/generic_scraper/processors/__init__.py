from __future__ import annotations

from generic_scraper.processors.base import Processor
from generic_scraper.processors.beautifulsoup_processor import BeautifulSoupProcessor
from generic_scraper.processors.html_parser_processor import HtmlParserProcessor
from generic_scraper.processors.lxml_processor import LxmlProcessor
from generic_scraper.processors.regex_processor import RegexProcessor

PROCESSOR_REGISTRY: dict[str, type[Processor]] = {
    BeautifulSoupProcessor.name: BeautifulSoupProcessor,
    LxmlProcessor.name: LxmlProcessor,
    HtmlParserProcessor.name: HtmlParserProcessor,
    RegexProcessor.name: RegexProcessor,
}

__all__ = ["Processor", "PROCESSOR_REGISTRY"]
