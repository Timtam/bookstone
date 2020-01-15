from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel

from storage import Storage

class LibrariesModel(QStandardItemModel):

  def __init__(self, *args, **kwargs):
    QStandardItemModel.__init__(self, 0, 2, *args, **kwargs)

    self._libraries = []

    self.setHorizontalHeaderLabels(['Name', 'Connection'])

    self.reloadLibraries()
  
  def reloadLibraries(self):

    amount = len(self._libraries)

    self.clear()

    self._libraries = Storage.getInstance().getLibraryManager().getLibraries()

    if amount != len(self._libraries):
      self.layoutChanged.emit()

      for lib in self._libraries:
        row = []
        row.append(QStandardItem(lib.getUUID()))
        row.append(QStandardItem(lib.getBackend().getName()))
        self.appendRow(row)

  def rowCount(self, index):
    return len(self._libraries)
