from abc import ABC, abstractmethod
import os.path
from pathlib import Path

class Backend(ABC):

  def __init__(self):
    self._path = Path('')

  def withPath(f):
    def helper(self, path, *args, **kwargs):

      path = self._path / path

      return f(self, os.path.normpath(str(path)), *args, **kwargs)
    return helper

  def withPosixPath(f):
    def helper(self, path, *args, **kwargs):

      path = self._path / path

      path = Path(os.path.normpath(str(path)))

      return f(self, path.as_posix(), *args, **kwargs)
    return helper

  def setPath(self, path):

    self._path = Path(os.path.normpath(path))

  def getPath(self):
    return self._path.as_posix()

  @staticmethod
  @abstractmethod
  def getName(self):
    raise NotImplementedError()

  @abstractmethod
  def serialize(self):
    return {
      'name': self.getName(),
      'path': self.getPath(),
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

  @abstractmethod
  def openFile(self, path):
    raise NotImplementedError()
    
  @abstractmethod
  def getStats(self, path):
    raise NotImplementedError()