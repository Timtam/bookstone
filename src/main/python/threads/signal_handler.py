from PyQt5.QtCore import QObject, pyqtSignal

class SignalHandler(QObject):

  finished = pyqtSignal(bool)
  result = pyqtSignal(tuple)
