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
from .. import Window
from library import Library
from storage import Storage
from utils import getLibrariesDirectory

class LibrariesWindow(Window):

  def __init__(self, *args, **kwargs):
    Window.__init__(self, *args, **kwargs)

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

    self.indexing_button = QPushButton(self)
    self.layout.addWidget(self.indexing_button)

    self.close_button = QPushButton('Close', self)
    self.close_button.pressed.connect(self.close)
    self.layout.addWidget(self.close_button)

    self.setLayout(self.layout)

    manager = Storage.getInstance().getLibraryManager()
    manager.indexerStarted.connect(self.indexerHandler)
    manager.indexerFinished.connect(self.indexerHandler)

    self.initializeIndexingButton()

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
    self.initializeIndexingButton()

  def generateShowAddDialogLambda(self, dialog):
    return lambda: self.showAddDialog(dialog)

  def removeLibrary(self, lib):
  
    manager = Storage.getInstance().getLibraryManager()

    manager.removeLibrary(lib)
    manager.save(getLibrariesDirectory())
    
    self.libraries_list.selectionModel().clearSelection()
    self.libraries_model.reloadLibraries()
    self.initializeIndexingButton()
    
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

  def close(self):

    manager = Storage.getInstance().getLibraryManager()
    manager.indexerStarted.disconnect(self.indexerHandler)
    manager.indexerFinished.disconnect(self.indexerHandler)
    
    self.closed.emit()

  def indexerHandler(self, success = None):
    self.initializeIndexingButton()

  def startIndexing(self):
    Storage.getInstance().getLibraryManager().startIndexing()
    self.initializeIndexingButton()

  def cancelIndexing(self):
    Storage.getInstance().getLibraryManager().cancelIndexing()
    self.initializeIndexingButton()

  def initializeIndexingButton(self):
  
    manager = Storage.getInstance().getLibraryManager()
    
    libs = len(manager.getLibraries())
    
    if libs == 0:
      self.indexing_button.setEnabled(False)
    else:
      self.indexing_button.setEnabled(True)

    if not manager.isIndexing() or libs == 0:

      try:
        self.indexing_button.pressed.disconnect()
      except TypeError:
        pass

      self.indexing_button.pressed.connect(self.startIndexing)
      self.indexing_button.setText('Start indexing')

    else:

      try:
        self.indexing_button.pressed.disconnect()
      except TypeError:
        pass

      self.indexing_button.pressed.connect(self.cancelIndexing)
      self.indexing_button.setText('Cancel indexing')
