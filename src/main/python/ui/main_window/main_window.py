from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
  QAction,
  QLabel, 
  QMenu,
  QMenuBar)

from ui import WindowController
from storage import Storage
from .. import Window
from ui.libraries_window import LibrariesWindow

class MainWindow(Window):

  def __init__(self, *args, **kwargs):
    Window.__init__(self, *args, **kwargs)

    self.setWindowTitle('Bookstone')

    self.menu_bar = QMenuBar(self)
    self.file_menu = self.menu_bar.addMenu('&File')
    
    act = QAction('Manage libraries', self.file_menu)
    act.triggered.connect(self.showLibrariesWindow)
    self.file_menu.addAction(act)

    act = QAction('&Exit', self.file_menu)
    act.triggered.connect(self.exit)
    self.file_menu.addAction(act)

  def exit(self):
    self.closed.emit()

  def showLibrariesWindow(self):
  
    WindowController.getInstance().pushWindow(LibrariesWindow())
