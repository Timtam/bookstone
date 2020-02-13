from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
  QWidget,
  QMessageBox)

from storage import Storage

class Window(QWidget):

  closed = pyqtSignal()

  def closeEvent(self, event):
  
    manager = Storage.getInstance().getLibraryManager()
    
    if not manager.isIndexing() or not Storage.getInstance().getConfigurationManager().askBeforeExitWhenIndexing:
      event.accept()
      return
    
    box = QMessageBox()
    box.setText("Indexing operation in progress")
    box.setInformativeText("Do you really want to exit and abort the operation?")
    box.setStandardButtons( QMessageBox.Yes | QMessageBox.No )
    box.setDefaultButton( QMessageBox.No )
    box.setIcon( QMessageBox.Question )

    res = box.exec_()

    if res == QMessageBox.Yes:
      event.accept()
    else:
      event.ignore()
