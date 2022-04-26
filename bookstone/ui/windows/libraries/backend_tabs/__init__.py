from typing import Tuple, Type

from ..backend_tab import BackendTab
from .ftp import FTPBackendTab
from .local import LocalBackendTab
from .smb import SMBBackendTab

BackendTabs: Tuple[Type[BackendTab], ...] = (
    LocalBackendTab,
    FTPBackendTab,
    SMBBackendTab,
)
