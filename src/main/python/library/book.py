from typing import Any, Dict

from .tag_collection import TagCollection


class Book:

    _path: str
    _tags: TagCollection

    def __init__(self, path: str = "") -> None:

        self._path = path
        self._tags = TagCollection()

    def serialize(self) -> Dict[str, Any]:

        return {
            "tags": self._tags.serialize(),
            "path": self._path,
        }

    def deserialize(self, serialized: Dict[str, Any]) -> None:

        self._path = serialized.get("path", "")

        tags: Dict[str, str] = serialized.get("tags", {})

        self._tags.deserialize(tags)

    def getPath(self) -> str:
        return self._path

    def setPath(self, path: str) -> None:
        self._path = path

    @property
    def tags(self) -> TagCollection:
        return self._tags
