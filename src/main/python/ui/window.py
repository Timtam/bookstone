from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

class Window(QWidget):

  closed = pyqtSignal()
