from abc import ABC, abstractmethod
import os.path

class Backend(ABC):

  def __init__(self):
    self._path = ''

  def setPath(self, path):

    path = os.path.normpath(path)
    
    if not path.endswith(os.path.sep):
      path = path + os.path.sep

    self._path = path

  def getPath(self):
    return self._path

  @staticmethod
  @abstractmethod
  def getName(self):
    raise NotImplementedError()

  @abstractmethod
  def serialize(self):
    return {
      'name': self.getName(),
      'path': self._path,
    }
  
  @abstractmethod
  def deserialize(self, serialized):

    self.setPath(serialized.get('path', ''))

  @abstractmethod
  def listDirectory(self, dir):
    raise NotImplementedError()

  @abstractmethod
  def isDirectory(self, path):
    raise NotImplementedError()
  
  @abstractmethod
  def isFile(self, path):
    raise NotImplementedError()
