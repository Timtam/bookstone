import re
import string
from typing import Any, Dict, Iterable, List, Optional, Pattern, Tuple, cast

from .tag import Tag
from .tag_collection import TagCollection
from .tags import Tags


class NamingSchemeEntry:

    # the human-readable pattern
    # e.g.: {author} - {title}
    _pattern: str

    # the compiled regex pattern for the above pattern
    _regex_pattern: Pattern[str]

    def __init__(self, pattern: str) -> None:

        # populate the patterns, including validity check
        self.setPattern(pattern)

    def checkValid(self, value: str) -> None:

        placeholders: Iterable[
            Tuple[str, Optional[str], Optional[str], Optional[str]]
        ] = string.Formatter().parse(value)
        p: Tuple[str, Optional[str], Optional[str], Optional[str]]

        for p in placeholders:
            if isinstance(p[1], str) and p[1] not in Tags:
                raise AttributeError(f"invalid tag specified: {p[1]}")

    def setPattern(self, value: str) -> None:

        self.checkValid(value)

        names: List[str] = [
            t[1] for t in string.Formatter().parse(value) if isinstance(t[1], str)
        ]

        self._regex_pattern = re.compile(
            value.format(
                **{
                    n: f"(?P<{n}>.*?)"
                    if names.index(n) < len(names) - 1
                    else f"(?P<{n}>.*)"
                    for n in names
                }
            )
        )

        self._pattern = value

    # returns the human-readable pattern
    def getPattern(self) -> str:
        return self._pattern

    # resolves the human-readable pattern with the given tags
    def getResolved(self, tags: Iterable[Tag] = Tags) -> str:
        return self._pattern.format(**{t.name: t.value for t in tags})

    # matches a path with the given human-readable pattern
    # if the match is valid, returns a TagCollection() with all the tags found
    def match(self, path: str) -> Optional[TagCollection]:

        match: Optional[re.Match] = self._regex_pattern.match(path)

        if not match:
            return None

        tags: TagCollection = TagCollection()

        g: str
        v: str

        for g, v in match.groupdict().items():
            tags[g].value = v

        return tags


class NamingScheme:

    # not associated with a series
    standalone: NamingSchemeEntry

    # contained within a series of books
    volume: NamingSchemeEntry

    # is this naming scheme available by default?
    _default: bool

    name: str

    def __init__(
        self, name: str, standalone: str, volume: str, default: bool = False
    ) -> None:

        self._default = default

        self.name = name
        self.standalone = NamingSchemeEntry(standalone)
        self.volume = NamingSchemeEntry(volume)

    @property
    def default(self) -> bool:
        return self._default

    def serialize(self) -> Dict[str, str]:

        return {
            "name": self.name,
            "standalone": self.standalone.getPattern(),
            "volume": self.volume.getPattern(),
        }

    def __eq__(self, other: Any) -> bool:

        if isinstance(other, NamingScheme):
            return self.name == cast(NamingScheme, other).name
        elif isinstance(other, str):
            return self.name == other
        return NotImplemented

    # returns tree depth of a string
    # usually means that it just counts the delimiters (/) and adds 1
    # might become more complicated later on
    # will mainly be used to pre-filter a node tree using Node.findChildren()

    def getDepth(self, value: str) -> int:
        return len(value.split("/"))
