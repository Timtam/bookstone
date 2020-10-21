from PyQt5.QtCore import QObject, pyqtSignal

from .priorizable_thread import PriorizableThread


class ThreadPoolSignalHandler(QObject):

    threadFinished: pyqtSignal = pyqtSignal(PriorizableThread, bool)
