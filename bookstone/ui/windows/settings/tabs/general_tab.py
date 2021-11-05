from typing import Any

from PyQt5.QtWidgets import QVBoxLayout, QWidget


class GeneralTab(QWidget):
    def __init__(self, *args: Any, **kwargs: Any) -> None:

        super().__init__(*args, **kwargs)

        layout = QVBoxLayout(self)

        self.setLayout(layout)
