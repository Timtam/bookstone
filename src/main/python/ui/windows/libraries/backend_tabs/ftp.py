from typing import Any, cast

from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit

from backend import Backend
from backends.ftp import FTPBackend

from ..backend_tab import BackendTab


class FTPBackendTab(BackendTab):

    ftps_checkbox: QCheckBox
    host_input: QLineEdit
    password_input: QLineEdit
    path_input: QLineEdit
    port_input: QLineEdit
    username_input: QLineEdit

    def __init__(self, *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)

        if not self.backend:
            self.backend = FTPBackend()

        layout: QHBoxLayout = QHBoxLayout(self)

        host_label: QLabel = QLabel("Host:", self)
        layout.addWidget(host_label)

        self.host_input = QLineEdit(cast(FTPBackend, self.backend).getHost(), self)
        self.host_input.textChanged.connect(self.parent.updated.emit)
        host_label.setBuddy(self.host_input)
        layout.addWidget(self.host_input)

        username_label: QLabel = QLabel("Username:", self)
        layout.addWidget(username_label)

        self.username_input = QLineEdit(
            cast(FTPBackend, self.backend).getUsername(), self
        )
        self.username_input.textChanged.connect(self.parent.updated.emit)
        username_label.setBuddy(self.username_input)
        layout.addWidget(self.username_input)

        password_label: QLabel = QLabel("Password:", self)
        layout.addWidget(password_label)

        self.password_input = QLineEdit(
            cast(FTPBackend, self.backend).getPassword(), self
        )
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.textChanged.connect(self.parent.updated.emit)
        password_label.setBuddy(self.password_input)
        layout.addWidget(self.password_input)

        port_label: QLabel = QLabel("Port:", self)
        layout.addWidget(port_label)

        self.port_input = QLineEdit(str(cast(FTPBackend, self.backend).getPort()), self)
        self.port_input.setText(str(21))
        validator = QIntValidator(self)
        validator.setBottom(1)
        self.port_input.setValidator(validator)
        port_label.setBuddy(self.port_input)
        layout.addWidget(self.port_input)

        path_label: QLabel = QLabel("Path:", self)
        layout.addWidget(path_label)

        self.path_input = QLineEdit(self.backend.getPath(), self)
        self.path_input.setText("/")
        self.path_input.textChanged.connect(self.parent.updated.emit)
        path_label.setBuddy(self.path_input)
        layout.addWidget(self.path_input)

        self.ftps_checkbox = QCheckBox("FTPS", self)
        self.ftps_checkbox.setChecked(cast(FTPBackend, self.backend).getFTPS())
        layout.addWidget(self.ftps_checkbox)

        self.setLayout(layout)

    def getBackend(self) -> Backend:

        b: FTPBackend = cast(FTPBackend, self.backend)

        b.setPath(self.path_input.text())
        b.setUsername(self.username_input.text())
        b.setPassword(self.password_input.text())
        b.setHost(self.host_input.text())
        b.setPort(int(self.port_input.text()))
        b.setFTPS(self.ftps_checkbox.isChecked())

        return b

    def isValid(self) -> bool:

        host_present: bool = False
        username_present: bool = False
        password_present: bool = False
        path_present: bool = False

        if len(self.username_input.text()) > 0:
            username_present = True

        if len(self.password_input.text()) > 0:
            password_present = True

        if len(self.host_input.text()) > 0:
            host_present = True

        if len(self.path_input.text()) > 0:
            path_present = True

        enable: bool = (
            username_present and password_present and path_present and host_present
        )

        return enable

    @staticmethod
    def getName() -> str:
        return FTPBackend.getName()
