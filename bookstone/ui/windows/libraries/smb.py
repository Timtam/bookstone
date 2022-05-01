import re
import urllib.parse
from typing import Any

from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit

from .backend_tab import BackendTab


class SMBBackendTab(BackendTab):

    _PATH_REGEX_ = re.compile("(smb://)(?P<username>.*):(?P<password>.*)@(?P<path>.*)")

    password_input: QLineEdit
    path_input: QLineEdit
    username_input: QLineEdit

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        super().__init__(*args, **kwargs)

        layout: QHBoxLayout = QHBoxLayout(self)

        path_label: QLabel = QLabel("Path:", self)
        layout.addWidget(path_label)

        self.path_input = QLineEdit(self)
        self.path_input.textChanged.connect(self.parent.updated.emit)
        path_label.setBuddy(self.path_input)
        layout.addWidget(self.path_input)

        username_label: QLabel = QLabel("Username:", self)
        layout.addWidget(username_label)

        self.username_input = QLineEdit(self)
        self.username_input.textChanged.connect(self.parent.updated.emit)
        username_label.setBuddy(self.username_input)
        layout.addWidget(self.username_input)

        password_label = QLabel("Password:", self)
        layout.addWidget(password_label)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.textChanged.connect(self.parent.updated.emit)
        password_label.setBuddy(self.password_input)
        layout.addWidget(self.password_input)

        self.setLayout(layout)

    def isValid(self) -> bool:

        username_present: bool = False
        password_present: bool = False

        if len(self.username_input.text()) > 0:
            username_present = True

        if len(self.password_input.text()) > 0:
            password_present = True

        enable: bool = username_present and password_present

        return enable

    @staticmethod
    def getName() -> str:
        return "SMB"

    def setPath(self, path: str) -> None:

        match = self._PATH_REGEX_.match(path)

        if not match:
            return

        self.path_input.blockSignals(True)
        self.path_input.setText(match.group("path"))
        self.path_input.blockSignals(False)
        self.username_input.blockSignals(True)
        self.username_input.setText(urllib.parse.unquote(match.group("username")))
        self.username_input.blockSignals(False)
        self.password_input.blockSignals(True)
        self.password_input.setText(urllib.parse.unquote(match.group("password")))
        self.password_input.blockSignals(False)

    def getPath(self) -> str:

        if not self.isValid():
            return ""

        return f"smb://{urllib.parse.quote(self.username_input.text())}:{urllib.parse.quote(self.password_input.text())}@{self.path_input.text()}"
