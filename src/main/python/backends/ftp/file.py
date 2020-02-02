import os

from backend_file import BackendFile

class FTPBackendFile(BackendFile):

  def __init__(self, host, path):
    self._file = None
    self._host = host
    self._path = path
    self._size = 0
    self._pos = 0

    stats = host.stat(path)
    self._size = stats.st_size

  def _get_file(self, rest = None):

    if self._file is None:
      self._file = self._host.open(self._path, 'rb', rest = rest)

      if rest:
        self._pos = rest
      else:
        self._pos = 0
    return self._file

  def read(self, bytes = -1):

    if bytes == 0:
      return b''

    if bytes < 0 or self._pos + bytes > self._size:
      bytes = self._size - self._pos

    file = self._get_file()

    data = file.read(bytes)

    self._pos += len(data)
    
    return data
  
  def close(self):
    self._file.close()
    self._file = None
    self._pos = 0

  def tell(self):
    return self._pos
  
  def seek(self, offset, whence = 0):

    if whence == os.SEEK_CUR:
      offset = self._pos + offset
    elif whence == os.SEEK_END:
      offset = self._size + offset - 1

    if offset == self._pos:
      return self._pos

    self.close()

    self._get_file(offset)

    return self._pos