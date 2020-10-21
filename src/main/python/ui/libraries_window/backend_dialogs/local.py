from typing import Any, Dict, List

from PyQt5.QtWidgets import (
    QFileDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from backend import Backend
from backends.local import LocalBackend

from ..backend_dialog import BackendDialog


class LocalBackendDialog(BackendDialog):

    browse_button: QPushButton
    folder_input: QLineEdit

    def __init__(self, *args: Any, **kwargs: Any):

        super().__init__()

    def build(self) -> Dict[str, QWidget]:

        folder_tab: QWidget = QWidget(self.tabs)

        layout: QVBoxLayout = QVBoxLayout(folder_tab)
        folder_label: QLabel = QLabel("Library directory:", self)
        layout.addWidget(folder_label)

        self.folder_input = QLineEdit(folder_tab)
        self.folder_input.setReadOnly(True)
        folder_label.setBuddy(self.folder_input)
        layout.addWidget(self.folder_input)

        self.browse_button = QPushButton("Browse...", folder_tab)
        self.browse_button.pressed.connect(self.browseDirectory)
        layout.addWidget(self.browse_button)

        folder_tab.setLayout(layout)

        return {"Location": folder_tab}

    def getBackend(self) -> Backend:

        b: Backend = LocalBackend()

        b.setPath(self.folder_input.text())

        return b

    @staticmethod
    def getName() -> str:
        return LocalBackend.getName()

    def browseDirectory(self) -> None:

        picker: QFileDialog = QFileDialog(self)

        picker.setFileMode(QFileDialog.Directory)

        if self.folder_input.text():
            picker.setDirectory(self.folder_input.text())

        picker.exec_()

        files: List[str] = picker.selectedFiles()

        if len(files):
            self.folder_input.setText(files[0])

        self.update()

    def isValid(self) -> bool:

        return bool(self.folder_input.text())
