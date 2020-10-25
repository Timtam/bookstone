from typing import Any, Type, cast

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTabWidget,
    QWidget,
)

from backend import Backend
from exceptions import BackendError
from library.library import Library

from .backend_tab import BackendTab


class DetailsDialog(QDialog):

    backend_tab: BackendTab
    button_box: QDialogButtonBox
    general_tab: QWidget
    library: Library
    name_input: QLineEdit
    name_input_was_edited: bool
    tabs: QTabWidget
    updated: pyqtSignal = pyqtSignal()

    def __init__(
        self, backend_tab: Type[BackendTab], library: Library, *args: Any, **kwargs: Any
    ):

        super().__init__(*args, **kwargs)

        self.library = library
        self.name_input_was_edited = False

        self.updated.connect(self.handleUpdated)

        layout = QHBoxLayout(self)

        self.tabs = QTabWidget(self)

        self.general_tab = QWidget(self)

        general_layout: QHBoxLayout = QHBoxLayout(self.general_tab)

        name_label: QLabel = QLabel("Name:", self.general_tab)
        general_layout.addWidget(name_label)

        self.name_input = QLineEdit(self.library.getName(), self.general_tab)
        self.name_input.textChanged.connect(self.handleUpdated)
        self.name_input.textEdited.connect(self.setNameInputWasEdited)
        name_label.setBuddy(self.name_input)
        general_layout.addWidget(self.name_input)

        self.general_tab.setLayout(general_layout)

        self.tabs.addTab(self.general_tab, "General")

        self.backend_tab = backend_tab(self, self.library.getBackend())

        self.tabs.addTab(self.backend_tab, "Location")

        self.button_box = QDialogButtonBox(
            cast(
                QDialogButtonBox.StandardButton,
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            ),
            self,
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        self.updated.emit()

    def testConnection(self) -> bool:

        backend: Backend = self.backend_tab.getBackend()
        exc: BackendError

        try:
            backend.listDirectory(".")
        except BackendError as exc:
            box: QMessageBox = QMessageBox()
            box.setText("Error connecting using the provided information.")
            box.setStandardButtons(QMessageBox.Ok)
            box.setDetailedText(Qt.convertFromPlainText(str(exc)))  # type: ignore
            box.setTextFormat(Qt.RichText)
            box.setIcon(QMessageBox.Warning)
            box.exec_()
            return False

        return True

    def isValid(self) -> bool:
        return self.name_input.text() != "" and self.backend_tab.isValid()

    def handleUpdated(self) -> None:

        valid: bool = self.isValid()

        self.button_box.button(QDialogButtonBox.Ok).setEnabled(valid)

        if (
            not self.name_input_was_edited
            and self.backend_tab.getBackend().getPath() != "."
        ):
            self.name_input.setText(self.backend_tab.getBackend().getPath())

    def accept(self) -> None:
        if self.testConnection():
            self.library.setBackend(self.backend_tab.getBackend())
            self.library.setName(self.name_input.text())
            return super().accept()

    def setNameInputWasEdited(self) -> None:
        self.name_input_was_edited = True
