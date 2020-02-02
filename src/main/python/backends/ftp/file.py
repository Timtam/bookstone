from backend_file import BackendFile

class FTPBackendFile(BackendFile):

  def __init__(self, obj):
    self._file = obj
  
  def read(self, bytes = -1):
    return self._file.read(bytes)
  
  def close(self):
    self._file.close()
  
  def tell(self):
    return self._file.tell()
  
  def seek(self, offset, whence = 0):
    self._file.seek(offset, whence)