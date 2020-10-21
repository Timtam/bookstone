import os
import os.path
from typing import Any, BinaryIO, List

from backend import Backend

from .file import LocalBackendFile


class LocalBackend(Backend):
    @staticmethod
    def getName() -> str:
        return "Local"

    @Backend.withPath
    def listDirectory(self, dir: str) -> List[str]:
        return os.listdir(dir)

    @Backend.withPath
    def isDirectory(self, path: str) -> bool:
        return os.path.isdir(path)

    @Backend.withPath
    def isFile(self, path: str) -> bool:
        return os.path.isfile(path)

    @Backend.withPath
    def openFile(self, path: str) -> LocalBackendFile:

        obj: BinaryIO = open(path, "rb")

        return LocalBackendFile(obj)

    @Backend.withPath
    def getStats(self, path: str) -> Any:

        return os.stat(path)
