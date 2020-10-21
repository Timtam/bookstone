from typing import Any, Dict

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QMessageBox,
    QTabWidget,
    QWidget,
)

from backend import Backend
from exceptions import BackendError


class BackendDialog(QDialog):

    button_box: QDialogButtonBox
    layout: QHBoxLayout
    tabs: QTabWidget

    def __init__(self, *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)

    def build(self) -> Dict[str, QWidget]:
        return {}

    def setup(self) -> None:

        self.layout = QHBoxLayout(self)

        self.tabs = QTabWidget(self)

        tabs: Dict[str, QWidget] = self.build()
        name: str
        tab: QWidget

        for name, tab in tabs.items():
            self.tabs.addTab(tab, name)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

        self.update()

    @staticmethod
    def getName() -> str:
        pass

    def getBackend(self) -> Backend:
        pass

    def testConnection(self) -> bool:

        backend: Backend = self.getBackend()
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
        return True

    def update(self) -> None:

        valid: bool = self.isValid()

        self.button_box.button(QDialogButtonBox.Ok).setEnabled(valid)
