from PyQt5.QtWidgets import (
  QCheckBox,
  QDialog,
  QDialogButtonBox,
  QLabel, 
  QLineEdit,
  QHBoxLayout)
from PyQt5.QtGui import QIntValidator

from backends.ftp import FTPBackend
from ..backend_dialog import BackendDialog

class FTPBackendDialog(QDialog, BackendDialog):

  def __init__(self, *args, **kwargs):
    QDialog.__init__(self, *args, **kwargs)
    BackendDialog.__init__(self)

    self.setWindowTitle('Bookstone - FTP Library')

    self.layout = QHBoxLayout(self)

    self.host_label = QLabel('Host:', self)
    self.layout.addWidget(self.host_label)

    self.host_input = QLineEdit(self)
    self.host_input.textChanged.connect(self.validate)
    self.host_label.setBuddy(self.host_input)
    self.layout.addWidget(self.host_input)

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

    self.port_label = QLabel('Port:', self)
    self.layout.addWidget(self.port_label)

    self.port_input = QLineEdit(self)
    self.port_input.setText(str(21))
    validator = QIntValidator(self)
    validator.setBottom(1)
    self.port_input.setValidator(validator)
    self.port_label.setBuddy(self.port_input)
    self.layout.addWidget(self.port_input)

    self.path_label = QLabel('Path:', self)
    self.layout.addWidget(self.path_label)

    self.path_input = QLineEdit(self)
    self.path_input.setText('/')
    self.path_input.textChanged.connect(self.validate)
    self.path_label.setBuddy(self.path_input)
    self.layout.addWidget(self.path_input)

    self.ftps_checkbox = QCheckBox('FTPS', self)
    self.layout.addWidget(self.ftps_checkbox)

    self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
    self.button_box.accepted.connect(self.accept)
    self.button_box.rejected.connect(self.reject)
    self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
    self.layout.addWidget(self.button_box)

    self.setLayout(self.layout)

  def getBackend(self):

    b = FTPBackend()
    
    b.setPath(self.path_input.text())
    b.setUsername(self.username_input.text())
    b.setPassword(self.password_input.text())
    b.setHost(self.host_input.text())
    b.setPort(int(self.port_input.text()))
    b.setFTPS(self.ftps_checkbox.isChecked())

    return b
  
  def validate(self):
  
    host_present = False
    username_present = False
    password_present = False
    path_present = False
    
    if len(self.username_input.text()) > 0:
      username_present = True
    
    if len(self.password_input.text()) > 0:
      password_present = True

    if len(self.host_input.text()) > 0:
      host_present = True

    if len(self.path_input.text()) > 0:
      path_present = True

    enable = username_present and password_present and path_present and host_present

    self.button_box.button(QDialogButtonBox.Ok).setEnabled(enable)
    
  @staticmethod
  def getName():
    return FTPBackend.getName()
  
  def accept(self):
    if self.testConnection():
      return QDialog.accept(self)
      