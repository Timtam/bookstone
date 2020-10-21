import os
from typing import Any

import ftputil.error
from PyQt5.QtCore import QMutex

from backend_file import BackendFile


class FTPBackendFile(BackendFile):

    _file: Any
    _file_mutex: QMutex = QMutex()
    _host: ftputil.FTPHost
    _path: str
    _pos: int
    _size: int

    def __init__(self, host: ftputil.FTPHost, path: str):

        self._file = None
        self._host = host
        self._path = path
        self._size = 0
        self._pos = 0

        stats: Any = host.stat(path)
        self._size = stats.st_size

    def _get_file(self, rest=None):

        if self._file is None:
            self._file_mutex.lock()
            self._file = self._host.open(self._path, "rb", rest=rest)
            self._file_mutex.unlock()

            if rest:
                self._pos = rest
            else:
                self._pos = 0
        return self._file

    def read(self, length: int = -1) -> bytes:

        if length == 0:
            return b""

        if length < 0 or self._pos + length > self._size:
            length = self._size - self._pos

        file: Any = self._get_file()

        data: bytes = file.read(length)

        self._pos += len(data)

        return data

    def close(self) -> None:

        if self._file is not None:

            try:
                self._file.close()
            except ftputil.error.FTPIOError:
                pass

            self._file = None

        self._pos = 0

    def tell(self) -> int:
        return self._pos

    def seek(self, offset: int, whence: int = 0) -> int:

        if whence == os.SEEK_CUR:
            offset = self._pos + offset
        elif whence == os.SEEK_END:
            offset = self._size + offset - 1

        if offset == self._pos:
            return self._pos

        self.close()

        self._get_file(offset)

        return self._pos
