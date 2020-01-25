from storage import Storage

class AudioStream:

  def __init__(self, obj, device):
  
    self._obj = obj
    self._stream = device.CreateStreamFromFileObj(obj)
  
  @property
  def tags(self):
    return self._stream.Tags.Read()

  def close(self):
    self._stream.Free()
