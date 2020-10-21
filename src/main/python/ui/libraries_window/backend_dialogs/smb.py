from typing import Any, Dict

from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QWidget

from backend import Backend
from backends.smb import SMBBackend

from ..backend_dialog import BackendDialog


class SMBBackendDialog(BackendDialog):

    password_input: QLineEdit
    path_input: QLineEdit
    username_input: QLineEdit

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        super().__init__()

    def build(self) -> Dict[str, QWidget]:

        connection_tab: QWidget = QWidget(self)

        layout: QHBoxLayout = QHBoxLayout(connection_tab)

        path_label: QLabel = QLabel("Path:", connection_tab)
        layout.addWidget(path_label)

        self.path_input = QLineEdit(connection_tab)
        self.path_input.textChanged.connect(self.update)
        path_label.setBuddy(self.path_input)
        layout.addWidget(self.path_input)

        username_label: QLabel = QLabel("Username:", connection_tab)
        layout.addWidget(username_label)

        self.username_input = QLineEdit(connection_tab)
        self.username_input.textChanged.connect(self.update)
        username_label.setBuddy(self.username_input)
        layout.addWidget(self.username_input)

        password_label = QLabel("Password:", connection_tab)
        layout.addWidget(password_label)

        self.password_input = QLineEdit(connection_tab)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.textChanged.connect(self.update)
        password_label.setBuddy(self.password_input)
        layout.addWidget(self.password_input)

        connection_tab.setLayout(layout)

        return {"Connection": connection_tab}

    def getBackend(self) -> Backend:

        b: SMBBackend = SMBBackend()

        b.setPath(self.path_input.text())
        b.setUsername(self.username_input.text())
        b.setPassword(self.password_input.text())

        return b

    def isValid(self) -> bool:

        valid: bool = super().isValid()

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

        enable: bool = (
            valid and username_present and password_present and unc_path_present
        )

        return enable

    @staticmethod
    def getName() -> str:
        return SMBBackend.getName()

    def accept(self) -> None:
        if self.testConnection():
            return super().accept()
