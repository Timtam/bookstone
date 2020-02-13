from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
  QCheckBox,
  QLabel,
  QWidget,
  QVBoxLayout)

from storage import Storage

class GeneralTab(QWidget):

  def __init__(self, *args, **kwargs):
    QWidget.__init__(self, *args, **kwargs)

    self.layout = QVBoxLayout(self)
    
    self.ask_on_exit_when_indexing = QCheckBox('Ask before exiting when an indexing operation is currently in progress', self)
    self.ask_on_exit_when_indexing.stateChanged.connect(self.askOnExitWhenIndexingChanged)
    self.layout.addWidget(self.ask_on_exit_when_indexing)
    
    config = Storage.getInstance().getConfigurationManager()
    
    self.ask_on_exit_when_indexing.setChecked(config.askBeforeExitWhenIndexing)
  
  def askOnExitWhenIndexingChanged(self, state):
  
    if state == Qt.Checked:
      Storage.getInstance().getConfigurationManager().askBeforeExitWhenIndexing = True
    else:
      Storage.getInstance().getConfigurationManager().askBeforeExitWhenIndexing = False
