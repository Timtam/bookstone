from PyQt5.QtCore import QAbstractListModel, Qt

from storage import Storage

class LibrariesModel(QAbstractListModel):

  def __init__(self, *args, **kwargs):
    QAbstractListModel.__init__(self, *args, **kwargs)

    self._libraries = []

    self.reloadLibraries()
  
  def reloadLibraries(self):

    amount = len(self._libraries)

    self._libraries = Storage.getInstance().getLibraryManager().getLibraries()

    if amount != len(self._libraries):
      self.layoutChanged.emit()

  def data(self, index, role):
  
    if role == Qt.DisplayRole:

      return self._libraries[index.row()].getUUID()
  
  def rowCount(self, index):
    return len(self._libraries)