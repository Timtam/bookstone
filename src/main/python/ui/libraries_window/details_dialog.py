from typing import Any, Type

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QMessageBox,
    QTabWidget,
)

from backend import Backend
from exceptions import BackendError
from library.library import Library

from .backend_tab import BackendTab


class DetailsDialog(QDialog):

    backend_tab: BackendTab
    backend_tab_t: Type[BackendTab]
    button_box: QDialogButtonBox
    layout: QHBoxLayout
    library: Library
    tabs: QTabWidget

    def __init__(
        self, backend_tab: Type[BackendTab], library: Library, *args: Any, **kwargs: Any
    ):

        super().__init__(*args, **kwargs)

        self.backend_tab_t = backend_tab
        self.library = library

    def setup(self) -> None:

        self.layout = QHBoxLayout(self)

        self.tabs = QTabWidget(self)

        self.backend_tab = self.backend_tab_t(self, self.library.getBackend())

        self.tabs.addTab(self.backend_tab, "Location")

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

        self.update()

    def testConnection(self) -> bool:

        backend: Backend = self.backend_tab.getBackend()
        exc: BackendError

        try:
            backend.listDirectory(".")
        except BackendError as exc:
            box: QMessageBox = QMessageBox()
            box.setText("Error connecting using the provided information.")
            box.setStandardButtons(QMessageBox.Ok)
            box.setDetailedText(Qt.convertFromPlainText(str(exc)))
            box.setTextFormat(Qt.RichText)
            box.setIcon(QMessageBox.Warning)
            box.exec_()
            return False

        return True

    def isValid(self) -> bool:
        return self.backend_tab.isValid()

    def update(self) -> None:

        valid: bool = self.isValid()

        self.button_box.button(QDialogButtonBox.Ok).setEnabled(valid)

    def accept(self) -> None:
        if self.testConnection():
            self.library.setBackend(self.backend_tab.getBackend())
            return super().accept()
