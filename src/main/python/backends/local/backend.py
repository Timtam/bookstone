import os
import os.path

from backend import Backend
from exceptions import BackendError
from .file import LocalBackendFile

class LocalBackend(Backend):

  @staticmethod
  def getName():
    return 'Local'

  @Backend.withPath
  def listDirectory(self, dir):
    return os.listdir(dir)

  @Backend.withPath
  def isDirectory(self, path):
    return os.path.isdir(path)
  
  @Backend.withPath
  def isFile(self, path):
    return os.path.isfile(path)

  @Backend.withPath
  def openFile(self, path):
  
    obj = open(path, 'rb')
    return LocalBackendFile(obj)

  @Backend.withPath
  def getStats(self, path):
  
    return os.stat(path)