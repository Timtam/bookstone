from typing import Any, Dict

from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit, QWidget

from backend import Backend
from backends.ftp import FTPBackend

from ..backend_dialog import BackendDialog


class FTPBackendDialog(BackendDialog):

    ftps_checkbox: QCheckBox
    host_input: QLineEdit
    password_input: QLineEdit
    path_input: QLineEdit
    port_input: QLineEdit
    username_input: QLineEdit

    def __init__(self, *args: Any, **kwargs: Any):

        super().__init__()

    def build(self) -> Dict[str, QWidget]:

        connection_tab: QWidget = QWidget(self)

        layout: QHBoxLayout = QHBoxLayout(connection_tab)

        host_label: QLabel = QLabel("Host:", connection_tab)
        layout.addWidget(host_label)

        self.host_input = QLineEdit(connection_tab)
        self.host_input.textChanged.connect(self.update)
        host_label.setBuddy(self.host_input)
        layout.addWidget(self.host_input)

        username_label: QLabel = QLabel("Username:", connection_tab)
        layout.addWidget(username_label)

        self.username_input = QLineEdit(connection_tab)
        self.username_input.textChanged.connect(self.update)
        username_label.setBuddy(self.username_input)
        layout.addWidget(self.username_input)

        password_label: QLabel = QLabel("Password:", connection_tab)
        layout.addWidget(password_label)

        self.password_input = QLineEdit(connection_tab)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.textChanged.connect(self.update)
        password_label.setBuddy(self.password_input)
        layout.addWidget(self.password_input)

        port_label: QLabel = QLabel("Port:", connection_tab)
        layout.addWidget(port_label)

        self.port_input = QLineEdit(connection_tab)
        self.port_input.setText(str(21))
        validator = QIntValidator(connection_tab)
        validator.setBottom(1)
        self.port_input.setValidator(validator)
        port_label.setBuddy(self.port_input)
        layout.addWidget(self.port_input)

        path_label: QLabel = QLabel("Path:", connection_tab)
        layout.addWidget(path_label)

        self.path_input = QLineEdit(connection_tab)
        self.path_input.setText("/")
        self.path_input.textChanged.connect(self.update)
        path_label.setBuddy(self.path_input)
        layout.addWidget(self.path_input)

        self.ftps_checkbox = QCheckBox("FTPS", connection_tab)
        layout.addWidget(self.ftps_checkbox)

        connection_tab.setLayout(layout)

        return {"Connection": connection_tab}

    def getBackend(self) -> Backend:

        b: FTPBackend = FTPBackend()

        b.setPath(self.path_input.text())
        b.setUsername(self.username_input.text())
        b.setPassword(self.password_input.text())
        b.setHost(self.host_input.text())
        b.setPort(int(self.port_input.text()))
        b.setFTPS(self.ftps_checkbox.isChecked())

        return b

    def isValid(self) -> bool:

        valid = super().isValid()

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
            valid
            and username_present
            and password_present
            and path_present
            and host_present
        )

        return enable

    @staticmethod
    def getName() -> str:
        return FTPBackend.getName()

    def accept(self) -> None:
        if self.testConnection():
            return super().accept()
