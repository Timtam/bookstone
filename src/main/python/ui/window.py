from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget


class Window(QWidget):

    closed: pyqtSignal = pyqtSignal()

    def close(self) -> bool:

        success: bool = super().close()

        if success:
            self.closed.emit()

        return success
