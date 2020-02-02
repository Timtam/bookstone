from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

from exceptions import BackendError

class BackendDialog:

  @staticmethod
  def getName():
    raise NotImplementedError()

  def getBackend(self):
    raise NotImplementedError()

  def testConnection(self):
    
    backend = self.getBackend()
    
    try:
      content = backend.listDirectory('.')
    except BackendError as exc:
      box = QMessageBox()
      box.setText("Error connecting using the provided information.")
      box.setStandardButtons( QMessageBox.Ok )
      box.setDetailedText( Qt.convertFromPlainText(str(exc)) )
      box.setTextFormat( Qt.RichText )
      box.setIcon( QMessageBox.Warning )
      box.exec_()
      return False

    return True
