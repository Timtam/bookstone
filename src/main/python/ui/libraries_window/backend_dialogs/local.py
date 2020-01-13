from PyQt5.QtWidgets import QFileDialog

from backends.local import LocalBackend

class LocalBackendDialog(QFileDialog):

  def __init__(self, *args, **kwargs):
    QFileDialog.__init__(self, *args, **kwargs)

    self.setFileMode(QFileDialog.Directory)
    
  def getBackend(self):

    files = self.selectedFiles()

    b = LocalBackend()
    
    b.setPath(files[0])

    return b
  
  @staticmethod
  def getName():
    return LocalBackend.getName()