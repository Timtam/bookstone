import time

from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot


class PlaybackWorker(QObject):

    finished: pyqtSignal = pyqtSignal()

    def __init__(self) -> None:

        super().__init__()

    @pyqtSlot()
    def run(self) -> None:

        while True:
            if QThread.currentThread().isInterruptionRequested():
                break
            time.sleep(0.1)

        self.finished.emit()
