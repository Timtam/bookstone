from collections import UserDict
from typing import TYPE_CHECKING, Any, Dict

from .tag import Tag
from .tags import Tags

if TYPE_CHECKING:

    _Base = UserDict[str, Tag]

else:

    _Base = UserDict


class TagCollection(_Base):
    def __init__(self) -> None:

        super().__init__()

        tag: Tag

        for tag in Tags:
            self.add(tag())

    def __delitem__(self, name: str) -> None:
        raise IndexError("you cannot remove tags")

    def add(self, tag: Tag) -> None:

        self[tag.name] = tag

    def serialize(self) -> Dict[str, Any]:

        res: Dict[str, str] = {}
        tag: Tag

        for tag in self.data.values():
            if tag.isModified():
                res[tag.name] = tag.value

        return res

    def deserialize(self, serialized: Dict[str, str]) -> None:

        name: str
        value: str

        for name, value in serialized.items():

            try:
                tag: Tag = self[name]

                tag.value = value
            except IndexError:
                pass

    def __eq__(self, tags: Any) -> bool:

        if isinstance(tags, TagCollection):

            name: str
            tag: Tag

            for name, tag in tags.items():

                if self.get(name, None) != tag:
                    return False

            return True

        return NotImplemented

    def __str__(self) -> str:
        return "{" + ", ".join([k + ": " + v.value for k, v in self.items()]) + "}"

    def __repr__(self) -> str:
        return str(self)
