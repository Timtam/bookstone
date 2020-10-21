from typing import Tuple

from .tag import Tag

Tags: Tuple[Tag, ...] = (
    Tag("author", "Unknown Author"),
    Tag("title", "Unknown Title"),
    Tag("series"),
    Tag("collection"),
    Tag("number"),
)
