import uuid
from typing import Any, Dict, Optional, Union

from .tag_collection import TagCollection


class Book:

    _path: str
    _tags: TagCollection
    _uuid: uuid.UUID

    def __init__(self, path: str = "", tags: Optional[TagCollection] = None) -> None:

        if isinstance(tags, TagCollection):
            self._tags = tags
        else:
            self._tags = TagCollection()

        self.path = path
        self._uuid = uuid.uuid4()

    def serialize(self) -> Dict[str, Any]:

        return {
            "tags": self._tags.serialize(),
            "path": self._path,
            "uuid": str(self._uuid),
        }

    def deserialize(self, serialized: Dict[str, Any]) -> None:

        self._path = serialized.get("path", "")
        self._uuid = uuid.UUID(serialized.get("uuid", str(self._uuid)))

        tags: Dict[str, str] = serialized.get("tags", {})

        self._tags.deserialize(tags)

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, path: str) -> None:

        self._path = path

    @property
    def tags(self) -> TagCollection:
        return self._tags

    def __eq__(self, book: Any) -> bool:

        if isinstance(book, Book):
            return self._path == book._path and self._tags == book._tags
        elif isinstance(book, str):
            return str(self._path) == book

        return NotImplemented

    def __str__(self) -> str:
        return f"<Book tags={str(self.tags)}, path={self._path}>"

    def __repr__(self) -> str:
        return str(self)

    @property
    def uuid(self) -> str:
        return str(self._uuid)

    def __hash__(self) -> int:
        return self._uuid.int
