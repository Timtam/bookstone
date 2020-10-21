from collections import UserDict
from typing import Any, Dict

from .tag import Tag
from .tags import Tags


class TagCollection(UserDict):
    def __init__(self) -> None:

        super().__init__()

        tag: Tag

        for tag in Tags:
            self.add(tag())

    def __delitem__(self, idx: int) -> None:
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
