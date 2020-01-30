import os
import os.path

from backend import Backend
from exceptions import BackendError
from .file import LocalBackendFile

class LocalBackend(Backend):

  @staticmethod
  def getName():
    return 'Local'

  def serialize(self):
    return Backend.serialize(self)
  
  def deserialize(self, serialized):
    Backend.deserialize(self, serialized)

  def listDirectory(self, dir):
    return os.listdir(dir)

  def isDirectory(self, path):
    return os.path.isdir(path)
  
  def isFile(self, path):
    return os.path.isfile(path)

  def openFile(self, path):
  
    path = os.path.join(self.getPath(), path)

    obj = open(path, 'rb')
    return LocalBackendFile(obj)

  def getStats(self, path):
  
    path = os.path.join(self.getPath(), path)

    return os.stat(path)