from typing import Tuple, Type

from backend import Backend

from .ftp import FTPBackend
from .local import LocalBackend
from .smb import SMBBackend

Backends: Tuple[Type[Backend], ...] = (
    LocalBackend,
    FTPBackend,
    SMBBackend,
)
