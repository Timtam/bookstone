from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
  QDialog,
  QDialogButtonBox,
  QHBoxLayout,
  QMessageBox,
  QTabWidget
)

from exceptions import BackendError

class BackendDialog(QDialog):

  def __init__(self, *args, **kwargs):
    QDialog.__init__(self, *args, **kwargs)

  def build(self):
    pass

  def setup(self):

    self.layout = QHBoxLayout(self)

    self.tabs = QTabWidget(self)

    tabs = self.build()

    for name, tab in tabs.items():
      self.tabs.addTab(tab, name)

    self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
    self.button_box.accepted.connect(self.accept)
    self.button_box.rejected.connect(self.reject)
    self.layout.addWidget(self.button_box)

    self.setLayout(self.layout)

    self.update()

  @staticmethod
  def getName():
    raise NotImplementedError()

  def getBackend(self):
    raise NotImplementedError()

  def testConnection(self):
    
    backend = self.getBackend()
    
    try:
      content = backend.listDirectory('.')
    except BackendError as exc:
      box = QMessageBox()
      box.setText("Error connecting using the provided information.")
      box.setStandardButtons( QMessageBox.Ok )
      box.setDetailedText( Qt.convertFromPlainText(str(exc)) )
      box.setTextFormat( Qt.RichText )
      box.setIcon( QMessageBox.Warning )
      box.exec_()
      return False

    return True

  def isValid(self):
    return True

  def update(self):
  
    valid = self.isValid()

    self.button_box.button(QDialogButtonBox.Ok).setEnabled(valid)
