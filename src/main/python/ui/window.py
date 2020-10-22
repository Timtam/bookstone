from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QMessageBox, QWidget

from configuration_manager import ConfigurationManager
from library.manager import LibraryManager
from storage import Storage


class Window(QWidget):

    closed: pyqtSignal = pyqtSignal()

    def closeEvent(self, event: QCloseEvent) -> None:

        manager: LibraryManager = Storage().getLibraryManager()

        if (
            not manager.isIndexing()
            or not ConfigurationManager().askBeforeExitWhenIndexing
        ):
            event.accept()
            return

        box: QMessageBox = QMessageBox()
        box.setText("Indexing operation in progress")
        box.setInformativeText("Do you really want to exit and abort the operation?")
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        box.setDefaultButton(QMessageBox.No)
        box.setIcon(QMessageBox.Question)

        res: int = box.exec_()

        if res == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
