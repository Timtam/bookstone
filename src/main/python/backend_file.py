from abc import ABC, abstractmethod

class BackendFile(ABC):

  @abstractmethod
  def close(self):
    raise NotImplementedError()

  @abstractmethod
  def read(self, bytes = 0):
    raise NotImplementedError()
  
  @abstractmethod
  def seek(self, byte, whence = 0):
    raise NotImplementedError()

  @abstractmethod
  def tell(self):
    raise NotImplementedError()

  def readline(self):
    raise NotImplementedError()
  
  def readlines(self):
    raise NotImplementedError()
  
  def __iter__(self):
    raise NotImplementedError()
