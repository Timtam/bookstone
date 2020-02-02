from .ftp import FTPBackendDialog
from .local import LocalBackendDialog
from .smb import SMBBackendDialog

BackendDialogs = (
  LocalBackendDialog,
  FTPBackendDialog,
  SMBBackendDialog,)
