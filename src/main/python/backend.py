import os.path
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

from backend_file import BackendFile


class Backend(ABC):

    _path: Path

    def __init__(self) -> None:

        self._path = Path("")

    def withPath(f: Any) -> Any:
        def helper(self, path: Path, *args: Any, **kwargs: Any) -> Any:

            path = self._path / path

            return f(self, os.path.normpath(str(path)), *args, **kwargs)

        return helper

    def withPosixPath(f: Any) -> Any:
        def helper(self, path: Path, *args: Any, **kwargs: Any) -> Any:

            path = self._path / path

            path = Path(os.path.normpath(str(path)))

            return f(self, path.as_posix(), *args, **kwargs)

        return helper

    def setPath(self, path: str) -> None:

        self._path = Path(os.path.normpath(path))

    def getPath(self) -> str:
        return self._path.as_posix()

    @staticmethod
    @abstractmethod
    def getName() -> str:
        pass

    def serialize(self) -> Dict[str, Any]:
        return {
            "name": self.getName(),
            "path": self.getPath(),
        }

    def deserialize(self, serialized: Dict[str, Any]) -> None:

        self.setPath(serialized.get("path", ""))

    @abstractmethod
    def listDirectory(self, dir: str) -> List[str]:
        pass

    @abstractmethod
    def isDirectory(self, path: str) -> bool:
        pass

    @abstractmethod
    def isFile(self, path: str) -> bool:
        pass

    @abstractmethod
    def openFile(self, path: str) -> BackendFile:
        pass

    @abstractmethod
    def getStats(self, path: str) -> Any:
        pass
