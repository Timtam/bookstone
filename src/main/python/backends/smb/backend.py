from typing import Any, Dict, List

import smbclient
import smbclient.path
import smbprotocol.exceptions

from backend import Backend
from exceptions import BackendError

from .file import SMBBackendFile


class SMBBackend(Backend):

    _password: str
    _username: str

    def __init__(self) -> None:

        super().__init__()

        self._username = ""
        self._password = ""

    @staticmethod
    def getName() -> str:
        return "SMB"

    def serialize(self) -> Dict[str, Any]:

        ser: Dict[str, Any] = super().serialize()

        ser["username"] = self._username
        ser["password"] = self._password

        return ser

    def deserialize(self, serialized: Dict[str, Any]) -> None:

        super().deserialize(serialized)

        self._username = serialized.get("username", "")
        self._password = serialized.get("password", "")

    def setUsername(self, username: str) -> None:
        self._username = username

    def setPassword(self, password: str) -> None:
        self._password = password

    @Backend.withPath
    def listDirectory(self, dir: str) -> List[str]:

        try:
            return smbclient.listdir(
                dir, username=self._username, password=self._password
            )
        except smbprotocol.exceptions.SMBResponseException as exc:
            raise BackendError(exc.message)
        except smbprotocol.exceptions.SMBException as exc:
            raise BackendError(str(exc))

    @Backend.withPath
    def isDirectory(self, path: str) -> bool:
        return smbclient.path.isdir(
            path, username=self._username, password=self._password
        )

    @Backend.withPath
    def isFile(self, path: str) -> bool:
        return smbclient.path.isfile(
            path, username=self._username, password=self._password
        )

    @Backend.withPath
    def openFile(self, path: str) -> SMBBackendFile:

        obj = smbclient.open_file(
            path, mode="rb", username=self._username, password=self._password
        )

        return SMBBackendFile(obj)

    @Backend.withPath
    def getStats(self, path: str) -> Any:

        return smbclient.stat(path, username=self._username, password=self._password)
