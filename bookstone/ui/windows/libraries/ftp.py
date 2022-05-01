import re
import urllib.parse
from typing import Any

from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit

from .backend_tab import BackendTab


class FTPBackendTab(BackendTab):

    _PATH_REGEX_ = re.compile(
        r"(?P<protocol>ftps?)://((?P<username>.*(?=\:)):(?P<password>.*(?=@))@)?(?P<host>.*(?=[/\:]))(\:(?P<port>\d+))?(?P<path>.*)"
    )

    ftps_checkbox: QCheckBox
    host_input: QLineEdit
    password_input: QLineEdit
    path_input: QLineEdit
    port_input: QLineEdit
    username_input: QLineEdit

    def __init__(self, *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)

        layout: QHBoxLayout = QHBoxLayout(self)

        host_label: QLabel = QLabel("Host:", self)
        layout.addWidget(host_label)

        self.host_input = QLineEdit(self)
        self.host_input.textChanged.connect(self.parent.updated.emit)
        host_label.setBuddy(self.host_input)
        layout.addWidget(self.host_input)

        username_label: QLabel = QLabel("Username:", self)
        layout.addWidget(username_label)

        self.username_input = QLineEdit(self)
        self.username_input.textChanged.connect(self.parent.updated.emit)
        username_label.setBuddy(self.username_input)
        layout.addWidget(self.username_input)

        password_label: QLabel = QLabel("Password:", self)
        layout.addWidget(password_label)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.textChanged.connect(self.parent.updated.emit)
        password_label.setBuddy(self.password_input)
        layout.addWidget(self.password_input)

        port_label: QLabel = QLabel("Port:", self)
        layout.addWidget(port_label)

        self.port_input = QLineEdit(self)
        self.port_input.setText(str(21))
        validator = QIntValidator(self)
        validator.setBottom(1)
        self.port_input.setValidator(validator)
        port_label.setBuddy(self.port_input)
        layout.addWidget(self.port_input)

        path_label: QLabel = QLabel("Path:", self)
        layout.addWidget(path_label)

        self.path_input = QLineEdit(self)
        self.path_input.setText("/")
        self.path_input.textChanged.connect(self.parent.updated.emit)
        path_label.setBuddy(self.path_input)
        layout.addWidget(self.path_input)

        self.ftps_checkbox = QCheckBox("FTPS", self)
        layout.addWidget(self.ftps_checkbox)

        self.setLayout(layout)

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
        return "FTP"

    def getPath(self) -> str:

        if not self.isValid():
            return ""

        protocol: str = "ftp"
        credentials: str = ""
        port: str = ""

        if self.ftps_checkbox.isChecked():
            protocol = "ftps"

        if self.username_input.text() and self.password_input.text():
            credentials = f"{urllib.parse.quote(self.username_input.text())}:{urllib.parse.quote(self.password_input.text())}@"

        if self.port_input.text() and self.port_input.text() != "21":
            port = f":{self.port_input.text()}"

        return f"{protocol}://{credentials}{self.host_input.text()}{port}{self.path_input.text()}"

    def setPath(self, path: str) -> None:

        match = self._PATH_REGEX_.match(path)

        if not match:
            return

        if match.group("protocol") == "ftps":
            self.ftps_checkbox.blockSignals(True)
            self.ftps_checkbox.setChecked(True)
            self.ftps_checkbox.blockSignals(False)

        if match.group("username"):
            self.username_input.blockSignals(True)
            self.username_input.setText(urllib.parse.unquote(match.group("username")))
            self.username_input.blockSignals(False)

        if match.group("password"):
            self.password_input.blockSignals(True)
            self.password_input.setText(urllib.parse.unquote(match.group("password")))
            self.password_input.blockSignals(False)

        if match.group("host"):
            self.host_input.blockSignals(True)
            self.host_input.setText(match.group("host"))
            self.host_input.blockSignals(False)

        if match.group("port"):
            self.port_input.blockSignals(True)
            self.port_input.setText(match.group("port"))
            self.port_input.blockSignals(False)

        if match.group("path"):
            self.path_input.blockSignals(True)
            self.path_input.setText(match.group("path"))
            self.path_input.blockSignals(False)
