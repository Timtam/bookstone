from Bass4Py.BASS import BASS
import os.path

from .stream import AudioStream

class AudioManager:

  def __init__(self):
  
    self._bass = BASS()
    self._device = None
  
  def initialize(self):

    self._device = self._bass.GetOutputDevice(-1)
    self._device.Init(44100, 0, -1)

  def openStream(self, node):
  
    device = self._device
    
    backend = node.getBackend()
    
    obj = backend.openFile(os.path.join(backend.getPath(), node.getPath()))
    
    return AudioStream(obj)
