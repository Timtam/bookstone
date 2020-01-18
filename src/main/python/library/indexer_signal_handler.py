from PyQt5.QtCore import QObject, pyqtSignal

from .library import Library
from .node import Node

class IndexerSignalHandler(QObject):

  statusChanged = pyqtSignal(Library, str)
  finished = pyqtSignal(bool)
  result = pyqtSignal(Library, Node)
