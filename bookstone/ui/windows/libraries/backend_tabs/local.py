import re
from typing import Any, List

import fs
from PyQt5.QtWidgets import QFileDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout

from ..backend_tab import BackendTab


class LocalBackendTab(BackendTab):

    _PATH_REGEX_ = re.compile("(?:osfs://)(?P<path>.*)")

    browse_button: QPushButton
    folder_input: QLineEdit

    def __init__(self, *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)

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

    @staticmethod
    def getName() -> str:
        return "Local"

    def browseDirectory(self) -> None:

        picker: QFileDialog = QFileDialog(self)

        picker.setFileMode(QFileDialog.Directory)

        if self.folder_input.text():
            picker.setDirectory(self.folder_input.text())

        picker.exec_()

        files: List[str] = picker.selectedFiles()

        if len(files):
            self.folder_input.setText(files[0])

        self.parent.updated.emit()

    def isValid(self) -> bool:

        return bool(self.folder_input.text())

    def getPath(self) -> str:

        if not self.isValid():
            return ""

        with fs.open_fs(f"osfs://{self.folder_input.text()}") as f:
            return f.geturl(".", purpose="fs")

    def setPath(self, path: str) -> None:

        match = self._PATH_REGEX_.match(path)

        if not match:
            return

        self.folder_input.blockSignals(True)
        self.folder_input.setText(match.group("path"))
        self.folder_input.blockSignals(False)
