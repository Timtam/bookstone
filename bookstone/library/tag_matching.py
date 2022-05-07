import re
from typing import List, Optional, Pattern

from .tag_collection import TagCollection

Patterns: List[Pattern[str]] = [
    # series: Author - Series/Entry - Title
    re.compile(
        r"^(?P<author>.+?(?= -)) - (?P<series>.+?(?=/))/(?P<volume>.+?(?= -)) - (?P<title>.+)"
    ),
    # standalone: Author - Title
    re.compile(
        r"^(?P<author>.+?(?= -)) - (?P<title>.+?(?= -|$))(?: - )?(?P<subtitle>.+)?"
    ),
]


def matchPattern(pattern: Pattern[str], path: str) -> Optional[TagCollection]:

    match = pattern.match(path)

    if not match:
        return None

    tags: TagCollection = TagCollection()

    for name, value in match.groupdict().items():

        if value:

            tags[name].value = value.strip()

    return tags


def getPatternDepth(pattern: Pattern[str]) -> int:

    s: str = pattern.pattern
    groups: int = 0
    stripped: str = ""
    c: str

    for c in s:
        if c not in "()" and groups == 0:
            stripped += c
        elif c == "(":
            groups += 1
        elif c == ")":
            groups -= 1

    return stripped.count("/") + 1
