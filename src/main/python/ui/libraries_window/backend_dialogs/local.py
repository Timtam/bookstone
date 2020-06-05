from PyQt5.QtWidgets import (
  QFileDialog,
  QLabel,
  QLineEdit,
  QPushButton,
  QVBoxLayout,
  QWidget)

from backends.local import LocalBackend
from ..backend_dialog import BackendDialog

class LocalBackendDialog(BackendDialog):

  def __init__(self, *args, **kwargs):
    BackendDialog.__init__(self)

  def build(self):
  
    folder_tab = QWidget(self.tabs)
    
    layout = QVBoxLayout(folder_tab)
    folder_label = QLabel("Library directory:", self)
    layout.addWidget(folder_label)
    
    self.folder_input = QLineEdit(folder_tab)
    self.folder_input.setReadOnly(True)
    folder_label.setBuddy(self.folder_input)
    layout.addWidget(self.folder_input)

    self.browse_button = QPushButton('Browse...', folder_tab)
    self.browse_button.pressed.connect(self.browseDirectory)
    layout.addWidget(self.browse_button)
    
    folder_tab.setLayout(layout)

    return {
      'Location': folder_tab
    }

  def getBackend(self):

    b = LocalBackend()
    
    b.setPath(self.folder_input.text())

    return b
  
  @staticmethod
  def getName():
    return LocalBackend.getName()
  
  def browseDirectory(self):
  
    picker = QFileDialog(self)

    picker.setFileMode(QFileDialog.Directory)
    
    if self.folder_input.text():
      picker.setDirectory(self.folder_input.text())

    picker.exec_()

    files = picker.selectedFiles()
    
    if len(files):
      self.folder_input.setText(files[0])

    self.update()
  
  def isValid(self):
  
    return bool(self.folder_input.text())