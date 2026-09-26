from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ParsedDocument:
    title: str | None
