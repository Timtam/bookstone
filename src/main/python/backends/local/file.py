from typing import BinaryIO

from backend_file import BackendFile


class LocalBackendFile(BackendFile):

    _file: BinaryIO

    def __init__(self, obj: BinaryIO) -> None:

        self._file = obj

    def read(self, bytes: int = -1) -> bytes:
        return self._file.read(bytes)

    def close(self) -> None:
        self._file.close()

    def tell(self) -> int:
        return self._file.tell()

    def seek(self, offset: int, whence: int = 0) -> int:
        return self._file.seek(offset, whence)
