from PyQt5.QtWidgets import (
  QAction,
  QLabel,
  QPushButton,
  QTabWidget,
  QVBoxLayout)

from storage import Storage
from .. import Window
from .tabs import GeneralTab

class SettingsWindow(Window):

  def __init__(self, *args, **kwargs):
    Window.__init__(self, *args, **kwargs)

    self.setWindowTitle('Bookstone - Settings')

    self.layout = QVBoxLayout(self)
    
    self.tabs = QTabWidget(self)
    self.tabs.addTab(GeneralTab(self), 'General')
    
    self.layout.addWidget(self.tabs)
    
    self.ok_button = QPushButton('OK', self)
    self.ok_button.pressed.connect(self.close)
    self.layout.addWidget(self.ok_button)
    
  def close(self):
  
    self.closed.emit()
