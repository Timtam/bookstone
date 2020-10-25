from typing import Any, cast

from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit

from backend import Backend
from backends.smb import SMBBackend

from ..backend_tab import BackendTab


class SMBBackendTab(BackendTab):

    password_input: QLineEdit
    path_input: QLineEdit
    username_input: QLineEdit

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        super().__init__(*args, **kwargs)

        if not self.backend:
            self.backend = SMBBackend()

        layout: QHBoxLayout = QHBoxLayout(self)

        path_label: QLabel = QLabel("Path:", self)
        layout.addWidget(path_label)

        self.path_input = QLineEdit(self.backend.getPath(), self)
        self.path_input.textChanged.connect(self.parent.updated.emit)
        path_label.setBuddy(self.path_input)
        layout.addWidget(self.path_input)

        username_label: QLabel = QLabel("Username:", self)
        layout.addWidget(username_label)

        self.username_input = QLineEdit(
            cast(SMBBackend, self.backend).getUsername(), self
        )
        self.username_input.textChanged.connect(self.parent.updated.emit)
        username_label.setBuddy(self.username_input)
        layout.addWidget(self.username_input)

        password_label = QLabel("Password:", self)
        layout.addWidget(password_label)

        self.password_input = QLineEdit(
            cast(SMBBackend, self.backend).getPassword(), self
        )
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.textChanged.connect(self.parent.updated.emit)
        password_label.setBuddy(self.password_input)
        layout.addWidget(self.password_input)

        self.setLayout(layout)

    def getBackend(self) -> Backend:

        b: SMBBackend = cast(SMBBackend, self.backend)

        b.setPath(self.path_input.text())
        b.setUsername(self.username_input.text())
        b.setPassword(self.password_input.text())

        return b

    def isValid(self) -> bool:

        username_present: bool = False
        password_present: bool = False
        unc_path_present: bool = False

        if len(self.username_input.text()) > 0:
            username_present = True

        if len(self.password_input.text()) > 0:
            password_present = True

        # checking for valid unc path

        path: str = self.path_input.text()

        # needs to start with either two // or two \\
        if path.startswith(r"\\") or path.startswith("//"):
            try:
                tail: str = path[path[2:].index(path[0]) + 3 :]

                if len(tail) > 0:
                    unc_path_present = True

            except ValueError:
                pass

        enable: bool = username_present and password_present and unc_path_present

        return enable

    @staticmethod
    def getName() -> str:
        return SMBBackend.getName()
