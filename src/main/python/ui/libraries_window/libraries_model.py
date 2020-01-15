from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel

from storage import Storage

class LibrariesModel(QStandardItemModel):

  def __init__(self, *args, **kwargs):
    QStandardItemModel.__init__(self, *args, **kwargs)

    self._libraries = []

    self.reloadLibraries()
  
  def reloadLibraries(self):

    self.clear()

    self.setColumnCount(2)
    self.setHorizontalHeaderLabels(['Name', 'Connection'])

    self._libraries = Storage.getInstance().getLibraryManager().getLibraries()

    for lib in self._libraries:
      row = []
      row.append(QStandardItem(lib.getUUID()))
      row.append(QStandardItem(lib.getBackend().getName()))
      self.appendRow(row)
