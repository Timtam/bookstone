from typing import Dict, Type

from backend import Backend
from backends.ftp import FTPBackend
from backends.local import LocalBackend
from backends.smb import SMBBackend

from ..backend_tab import BackendTab
from .ftp import FTPBackendTab
from .local import LocalBackendTab
from .smb import SMBBackendTab

BackendTabs: Dict[Type[Backend], Type[BackendTab]] = {
    LocalBackend: LocalBackendTab,
    FTPBackend: FTPBackendTab,
    SMBBackend: SMBBackendTab,
}
