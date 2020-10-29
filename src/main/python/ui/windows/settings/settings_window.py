from typing import Any

from PyQt5.QtWidgets import QPushButton, QTabWidget, QVBoxLayout

from ui import Window

from .tabs import GeneralTab


class SettingsWindow(Window):

    ok_button: QPushButton
    tabs: QTabWidget

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Bookstone - Settings")

        layout = QVBoxLayout(self)

        self.tabs = QTabWidget(self)
        self.tabs.addTab(GeneralTab(self), "General")

        layout.addWidget(self.tabs)

        self.ok_button = QPushButton("OK", self)
        self.ok_button.pressed.connect(self.close)  # type: ignore
        layout.addWidget(self.ok_button)
