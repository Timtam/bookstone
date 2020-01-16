from PyQt5.QtWidgets import QFileDialog

from backends.local import LocalBackend
from ..backend_dialog import BackendDialog

class LocalBackendDialog(QFileDialog, BackendDialog):

  def __init__(self, *args, **kwargs):
    QFileDialog.__init__(self, *args, **kwargs)
    BackendDialog.__init__(self)

    self.setFileMode(QFileDialog.Directory)
    
  def getBackend(self):

    files = self.selectedFiles()

    b = LocalBackend()
    
    b.setPath(files[0])

    return b
  
  @staticmethod
  def getName():
    return LocalBackend.getName()