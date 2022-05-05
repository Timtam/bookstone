from typing import Dict

from .group import Group

Groups: Dict[str, Group] = {
    "author": Group(
        tag="author",
    ),
    "series": Group(
        tag="series",
        replacement_text="(no series)",
    ),
}
