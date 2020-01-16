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

      item = QStandardItem(lib.getName())
      item.setEditable(False)
      row.append(item)
      
      item = QStandardItem(lib.getBackend().getName())
      item.setEditable(False)
      row.append(item)

      self.appendRow(row)

  def updateLibrary(self, lib):
  
    index = self._libraries.index(lib)
    
    item = self.item(index, 0)
    item.setText(lib.getName())
