from typing import Tuple

from .tag import Tag

Tags: Tuple[Tag, ...] = (
    Tag("author", "Unknown Author", r"(?:[^\W\d_]| )+"),
    Tag("title", "Unknown Title", r"\w++(?:[.,_:()\s-](?![.\s-])|\w++)*"),
    Tag("series", pattern=r"\w++(?:[.,_:()\s-](?![.\s-])|\w++)*"),
    Tag("number", pattern=r"\d+"),
)
