import os

from backend import Backend

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
