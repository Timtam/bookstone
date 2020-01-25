import smbclient
import smbclient.path
import smbprotocol.exceptions

from backend import Backend
from exceptions import BackendError
from .file import SMBBackendFile

class SMBBackend(Backend):

  def __init__(self):
    self._username = ''
    self._password = ''

  @staticmethod
  def getName():
    return 'SMB'

  def serialize(self):
    ser = Backend.serialize(self)
    
    ser['username'] = self._username
    ser['password'] = self._password
    
    return ser
  
  def deserialize(self, serialized):

    Backend.deserialize(self, serialized)

    self._username = serialized.get('username', '')
    self._password = serialized.get('password', '')

  def setUsername(self, username):
    self._username = username
  
  def setPassword(self, password):
    self._password = password

  def listDirectory(self, dir):
    try:
      return smbclient.listdir(dir, username=self._username, password=self._password)
    except smbprotocol.exceptions.SMBResponseException as exc:
      raise BackendError(exc.message)

  def isDirectory(self, path):
    return smbclient.path.isdir(path, username=self._username, password=self._password)
  
  def isFile(self, path):
    return smbclient.path.isfile(path, username=self._username, password=self._password)

  def openFile(self, path):
  
    if not self.isFile(path):
      raise BackendError('{path} is not a file'.format(path = path))
    
    obj = smbclient.open_file(path, mode = 'rb', username = self._username, password = self._password)
    
    return SMBBackendFile(obj)
