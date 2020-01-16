from PyQt5.QtWidgets import (
  QDialog,
  QDialogButtonBox,
  QLabel, 
  QLineEdit,
  QHBoxLayout)

from backends.smb import SMBBackend
from ui.libraries_window.backend_dialog import BackendDialog

class SMBBackendDialog(QDialog, BackendDialog):

  def __init__(self, *args, **kwargs):
    QDialog.__init__(self, *args, **kwargs)
    BackendDialog.__init__(self)

    self.setWindowTitle('Bookstone - SMB Library')

    self.layout = QHBoxLayout(self)

    self.path_label = QLabel('Path:', self)
    self.layout.addWidget(self.path_label)

    self.path_input = QLineEdit(self)
    self.path_input.textChanged.connect(self.validate)
    self.path_label.setBuddy(self.path_input)
    self.layout.addWidget(self.path_input)

    self.username_label = QLabel('Username:', self)
    self.layout.addWidget(self.username_label)

    self.username_input = QLineEdit(self)
    self.username_input.textChanged.connect(self.validate)
    self.username_label.setBuddy(self.username_input)
    self.layout.addWidget(self.username_input)

    self.password_label = QLabel('Password:', self)
    self.layout.addWidget(self.password_label)

    self.password_input = QLineEdit(self)
    self.password_input.setEchoMode(QLineEdit.Password)
    self.password_input.textChanged.connect(self.validate)
    self.password_label.setBuddy(self.password_input)
    self.layout.addWidget(self.password_input)

    self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
    self.button_box.accepted.connect(self.accept)
    self.button_box.rejected.connect(self.reject)
    self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
    self.layout.addWidget(self.button_box)

    self.setLayout(self.layout)

  def getBackend(self):

    b = SMBBackend()
    
    b.setPath(self.path_input.text())
    b.setUsername(self.username_input.text())
    b.setPassword(self.password_input.text())

    return b
  
  def validate(self):
  
    username_present = False
    password_present = False
    unc_path_present = False
    
    if len(self.username_input.text()) > 0:
      username_present = True
    
    if len(self.password_input.text()) > 0:
      password_present = True

    # checking for valid unc path
    
    path = self.path_input.text()
    
    # needs to start with either two // or two \\
    if path.startswith(r'\\') or path.startswith('//'):
      try:
        tail = path[path[2:].index(path[0])+3:]

        if len(tail) > 0:
          unc_path_present = True

      except ValueError:
        pass

    enable = username_present and password_present and unc_path_present

    self.button_box.button(QDialogButtonBox.Ok).setEnabled(enable)
    
  @staticmethod
  def getName():
    return SMBBackend.getName()
  
  def accept(self):
    if self.testConnection():
      return QDialog.accept(self)
      