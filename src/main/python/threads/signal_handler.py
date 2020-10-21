from PyQt5.QtCore import QObject, pyqtSignal


class SignalHandler(QObject):

    finished: pyqtSignal = pyqtSignal(bool)
    result: pyqtSignal = pyqtSignal(tuple)
