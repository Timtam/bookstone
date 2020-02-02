from .ftp import FTPBackend
from .local import LocalBackend
from .smb import SMBBackend

Backends = (
  LocalBackend,
  FTPBackend,
  SMBBackend,)