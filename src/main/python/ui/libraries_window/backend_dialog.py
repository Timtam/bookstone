from abc import ABC

class BackendDialog(ABC):

  @staticmethod
  @abstractmethod
  def getName():
    raise NotImplementedError()

  @abstractmethod
  def getBackend(self):
    raise NotImplementedError()
