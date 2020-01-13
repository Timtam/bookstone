from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
  QAction,
  QWidget,
  QLabel, 
  QListView,
  QMenu,
  QPushButton,
  QTreeView,
  QVBoxLayout)

from .backend_dialogs import BackendDialogs
from .libraries_model import LibrariesModel
from library import Library
from storage import Storage
from utils import getLibrariesDirectory

class LibrariesWindow(QWidget):

  def __init__(self):
    QWidget.__init__(self)

    self.setWindowTitle('Bookstone - Libraries')

    self.layout = QVBoxLayout(self)

    self.libraries_label = QLabel('Known libraries', self)
    self.layout.addWidget(self.libraries_label)

    self.libraries_list = QListView(self)
    self.libraries_model = LibrariesModel()
    self.libraries_list.setModel(self.libraries_model)
    self.libraries_list.selectionModel().selectionChanged.connect(self.librarySelected)
    self.libraries_label.setBuddy(self.libraries_list)
    self.layout.addWidget(self.libraries_list)

    self.add_button = QPushButton('Add', self)
    self.layout.addWidget(self.add_button)

    self.add_menu = QMenu(self.add_button)

    self.add_actions = []
    
    for i, dialog in enumerate(BackendDialogs):
      act = QAction(dialog.getName(), self.add_menu)
      self.add_menu.addAction(act)
      self.add_actions.append(act)
      act.triggered.connect(self.generateShowAddDialogLambda(dialog))
    
    self.add_button.setMenu(self.add_menu)

    self.remove_button = QPushButton('Remove', self)
    self.remove_button.setEnabled(False)
    self.remove_button.clicked.connect(self.removeLibrary)
    self.layout.addWidget(self.remove_button)

    self.library_view = QTreeView(self)
    self.layout.addWidget(self.library_view)

    self.close_button = QPushButton('Close', self)
    self.layout.addWidget(self.close_button)

    self.setLayout(self.layout)

  def showAddDialog(self, dialog):

    dlg = dialog(self)
    success = dlg.exec_()

    if not success:
      return
    
    backend = dlg.getBackend()

    lib = Library()
    lib.setBackend(backend)
    
    store = Storage.getInstance()
    store.getLibraryManager().addLibrary(lib)
    store.getLibraryManager().save(getLibrariesDirectory())

    self.libraries_model.reloadLibraries()

  def librarySelected(self, item_selection):
    
    if len(item_selection.indexes()) == 0:
      self.remove_button.setEnabled(False)
    
    self.remove_button.setEnabled(True)
  
  def generateShowAddDialogLambda(self, dialog):
    return lambda: self.showAddDialog(dialog)

  def removeLibrary(self):
  
    selected = self.libraries_list.currentIndex()
    
    Storage.getInstance().getLibraryManager().removeLibrary(selected.data(Qt.DisplayRole))
    Storage.getInstance().getLibraryManager().save(getLibrariesDirectory())
    self.libraries_model.reloadLibraries()
    self.libraries_list.selectionModel().clearSelection()

    # even though the selection gets cleared, the signal doesn't fire
    if len(self.libraries_list.selectionModel().selectedIndexes()) == 0:
      self.remove_button.setEnabled(False)
