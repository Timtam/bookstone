from abc import ABC, abstractmethod

class Backend(ABC):

  def __init__(self):
    self._path = ''

  def setPath(self, path):
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

    self._path = serialized.get('path', '')

  @abstractmethod
  def listDirectory(self, dir):
    raise NotImplementedError()
