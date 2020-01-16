from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import (
  QAction,
  QWidget,
  QInputDialog,
  QLabel, 
  QLineEdit,
  QMenu,
  QPushButton,
  QTableView,
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

    self.libraries_list = QTableView(self)
    self.libraries_list.setTabKeyNavigation(False)
    self.libraries_model = LibrariesModel()
    self.libraries_list.setModel(self.libraries_model)
    self.libraries_list.setSelectionMode(QTableView.SingleSelection)
    self.libraries_list.installEventFilter(self)
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

  def generateShowAddDialogLambda(self, dialog):
    return lambda: self.showAddDialog(dialog)

  def removeLibrary(self, lib):
  
    Storage.getInstance().getLibraryManager().removeLibrary(lib)
    self.libraries_list.selectionModel().clearSelection()
    self.libraries_model.reloadLibraries()
    
  def renameLibrary(self, lib):
  
    text, ok = QInputDialog.getText(self, 'Bookstone - Rename Library', 'Enter new name:', QLineEdit.Normal, lib.getName())
    
    if ok:
      lib.setName(text)
      Storage.getInstance().getLibraryManager().save(getLibrariesDirectory())
      self.libraries_model.updateLibrary(lib)

  def eventFilter(self, source, event):
  
    if event.type() == QEvent.ContextMenu and source is self.libraries_list:

      index = source.indexAt(event.pos()).row()

      if index >= 0:
        lib = Storage.getInstance().getLibraryManager().getLibraries()[index]
        menu = QMenu(self.libraries_list)
        act = QAction('Rename', menu)
        act.triggered.connect(lambda: self.renameLibrary(lib))
        menu.addAction(act)
        act = QAction('Remove', menu)
        act.triggered.connect(lambda: self.removeLibrary(lib))
        menu.addAction(act)
        menu.exec_()

        return True
    return QWidget.eventFilter(self, source, event)
