from typing import Tuple, Type

from ..backend_dialog import BackendDialog
from .ftp import FTPBackendDialog
from .local import LocalBackendDialog
from .smb import SMBBackendDialog

BackendDialogs: Tuple[Type[BackendDialog], ...] = (
    LocalBackendDialog,
    FTPBackendDialog,
    SMBBackendDialog,
)
