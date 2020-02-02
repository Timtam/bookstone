import ftputil
import ftputil.error

from backend import Backend
from exceptions import BackendError
from .factory import EncryptedFTPSessionFactory, UnencryptedFTPSessionFactory
from .file import FTPBackendFile

class FTPBackend(Backend):

  def __init__(self):
    Backend.__init__(self)
    self._host = ''
    self._username = ''
    self._password = ''
    self._port = 21
    self._ftps = False
    self._host_obj = None

  @staticmethod
  def getName():
    return 'FTP'

  def withHost(f):
  
    def supply(self, *args, **kwargs):

      if self._host_obj is None:
        try:
          self._host_obj = ftputil.FTPHost(self._host, self._username, self._password, port = self._port, session_factory = self._get_session_factory())
        except ftputil.error.FTPOSError as exc:
          raise BackendError(str(exc))
      return f(self, *args, host = self._host_obj, **kwargs)
    return supply

  def serialize(self):
    ser = Backend.serialize(self)
    
    ser['host'] = self._host
    ser['username'] = self._username
    ser['password'] = self._password
    ser['port'] = self._port
    ser['ftps'] = self._ftps
    
    return ser
  
  def deserialize(self, serialized):

    Backend.deserialize(self, serialized)

    self._host = serialized.get('host', '')
    self._username = serialized.get('username', '')
    self._password = serialized.get('password', '')
    self._port = serialized.get('port', 21)
    self._ftps = serialized.get('ftps', False)

  def setUsername(self, username):
    self._username = username
  
  def setPassword(self, password):
    self._password = password

  def setPort(self, port):
    
    if not isinstance(port, int):
      raise IOError('port must be an integer')

    self._port = port

  def setHost(self, host):
    self._host = host

  def setFTPS(self, ftps):

    if not isinstance(ftps, bool):
      raise IOError('parameter must be boolean')

    self._ftps = ftps

  @withHost
  @Backend.withPosixPath
  def listDirectory(self, dir, host):

    try:
      return host.listdir(dir)
    except ftputil.error.PermanentError as exc:
      raise BackendError(str(exc))

  @withHost
  @Backend.withPosixPath
  def isDirectory(self, path, host):

    return host.path.isdir(path)
  
  @withHost
  @Backend.withPosixPath
  def isFile(self, path, host):

    return host.path.isfile(path)

  @withHost
  @Backend.withPosixPath
  def openFile(self, path, host):
  
    return FTPBackendFile(host, path)

  @withHost
  @Backend.withPosixPath
  def getStats(self, path, host):
  
    return host.stat(path)
  
  def _get_session_factory(self):
    if self._ftps:
      return EncryptedFTPSessionFactory
    return UnencryptedFTPSessionFactory
