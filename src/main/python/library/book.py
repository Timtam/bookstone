import pathlib
from typing import Any, Dict, Optional, Union

from .tag_collection import TagCollection


class Book:

    _path: pathlib.Path
    _tags: TagCollection

    def __init__(
        self, path: Union[pathlib.Path, str] = "", tags: Optional[TagCollection] = None
    ) -> None:

        if isinstance(tags, TagCollection):
            self._tags = tags
        else:
            self._tags = TagCollection()

        self.setPath(path)

    def serialize(self) -> Dict[str, Any]:

        return {
            "tags": self._tags.serialize(),
            "path": str(self._path),
        }

    def deserialize(self, serialized: Dict[str, Any]) -> None:

        self._path = pathlib.Path(serialized.get("path", ""))

        tags: Dict[str, str] = serialized.get("tags", {})

        self._tags.deserialize(tags)

    def getPath(self) -> pathlib.Path:
        return self._path

    def setPath(self, path: Union[pathlib.Path, str]) -> None:

        if isinstance(path, str):
            self._path = pathlib.Path(path)
        else:
            self._path = path

    @property
    def tags(self) -> TagCollection:
        return self._tags
