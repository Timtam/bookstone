from typing import Any, Dict, Optional

import ftputil
import ftputil.error

from backend import Backend
from exceptions import BackendError

from .factory import EncryptedFTPSessionFactory, UnencryptedFTPSessionFactory
from .file import FTPBackendFile


class FTPBackend(Backend):

    _ftps: bool
    _host: str
    _host_obj: Optional[ftputil.FTPHost]
    _password: str
    _port: int
    _username: str

    def __init__(self) -> None:
        super().__init__()

        self._host = ""
        self._username = ""
        self._password = ""
        self._port = 21
        self._ftps = False
        self._host_obj = None

    @staticmethod
    def getName() -> str:
        return "FTP"

    def withHost(f: Any) -> Any:
        def supply(self, *args: Any, **kwargs: Any) -> Any:

            exc: ftputil.error.FTPOSError

            if self._host_obj is None:
                try:
                    self._host_obj = ftputil.FTPHost(
                        self._host,
                        self._username,
                        self._password,
                        port=self._port,
                        session_factory=self._get_session_factory(),
                    )
                except ftputil.error.FTPOSError as exc:
                    raise BackendError(str(exc))
            return f(self, *args, host=self._host_obj, **kwargs)

        return supply

    def serialize(self) -> Dict[str, Any]:

        ser: Dict[str, Any] = super().serialize()

        ser["host"] = self._host
        ser["username"] = self._username
        ser["password"] = self._password
        ser["port"] = self._port
        ser["ftps"] = self._ftps

        return ser

    def deserialize(self, serialized: Dict[str, Any]) -> None:

        super().deserialize(serialized)

        self._host = serialized.get("host", "")
        self._username = serialized.get("username", "")
        self._password = serialized.get("password", "")
        self._port = serialized.get("port", 21)
        self._ftps = serialized.get("ftps", False)

    def getUsername(self) -> str:
        return self._username

    def setUsername(self, username: str) -> None:
        self._username = username

    def getPassword(self) -> str:
        return self._password

    def setPassword(self, password: str) -> None:
        self._password = password

    def getPort(self) -> int:
        return self._port

    def setPort(self, port: int) -> None:

        if not isinstance(port, int):
            raise IOError("port must be an integer")

        self._port = port

    def getHost(self) -> str:
        return self._host

    def setHost(self, host: str) -> None:
        self._host = host

    def getFTPS(self) -> bool:
        return self._ftps

    def setFTPS(self, ftps: bool) -> None:

        if not isinstance(ftps, bool):
            raise IOError("parameter must be boolean")

        self._ftps = ftps

    @withHost
    @Backend.withPosixPath
    def listDirectory(self, dir: str, host: ftputil.FTPHost):

        exc: ftputil.error.PermanentError

        try:
            return host.listdir(dir)
        except ftputil.error.PermanentError as exc:
            raise BackendError(str(exc))

    @withHost
    @Backend.withPosixPath
    def isDirectory(self, path: str, host: ftputil.FTPHost) -> bool:

        return host.path.isdir(path)

    @withHost
    @Backend.withPosixPath
    def isFile(self, path: str, host: ftputil.FTPHost) -> bool:

        return host.path.isfile(path)

    @withHost
    @Backend.withPosixPath
    def openFile(self, path: str, host: ftputil.FTPHost) -> FTPBackendFile:

        return FTPBackendFile(host, path)

    @withHost
    @Backend.withPosixPath
    def getStats(self, path: str, host: ftputil.FTPHost) -> Any:

        return host.stat(path)

    def _get_session_factory(self) -> Any:
        if self._ftps:
            return EncryptedFTPSessionFactory
        return UnencryptedFTPSessionFactory
