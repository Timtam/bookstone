from typing import Any, List, cast

from PyQt5.QtWidgets import QFileDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout

from backend import Backend
from backends.local import LocalBackend

from ..backend_tab import BackendTab


class LocalBackendTab(BackendTab):

    browse_button: QPushButton
    folder_input: QLineEdit

    def __init__(self, *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)

        if not self.backend:
            self.backend = LocalBackend()

        layout: QVBoxLayout = QVBoxLayout(self)
        folder_label: QLabel = QLabel("Library directory:", self)
        layout.addWidget(folder_label)

        self.folder_input = QLineEdit(self)
        self.folder_input.setReadOnly(True)
        folder_label.setBuddy(self.folder_input)
        layout.addWidget(self.folder_input)

        self.browse_button = QPushButton("Browse...", self)
        self.browse_button.pressed.connect(self.browseDirectory)
        layout.addWidget(self.browse_button)

        self.setLayout(layout)

    def getBackend(self) -> Backend:

        b: LocalBackend = cast(LocalBackend, self.backend)

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

        self.parent.update()

    def isValid(self) -> bool:

        return bool(self.folder_input.text())
