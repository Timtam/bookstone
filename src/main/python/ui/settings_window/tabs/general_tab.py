from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QVBoxLayout, QWidget

from configuration_manager import ConfigurationManager


class GeneralTab(QWidget):

    ask_on_exit_when_indexing: QCheckBox
    layout: QVBoxLayout

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        super().__init__(*args, **kwargs)

        self.layout = QVBoxLayout(self)

        self.ask_on_exit_when_indexing = QCheckBox(
            "Ask before exiting when an indexing operation is currently in progress",
            self,
        )
        self.ask_on_exit_when_indexing.stateChanged.connect(
            self.askOnExitWhenIndexingChanged
        )
        self.layout.addWidget(self.ask_on_exit_when_indexing)

        config: ConfigurationManager = ConfigurationManager()

        self.ask_on_exit_when_indexing.setChecked(config.askBeforeExitWhenIndexing)

    def askOnExitWhenIndexingChanged(self, state: int):

        if state == Qt.Checked:
            ConfigurationManager().askBeforeExitWhenIndexing = True
        else:
            ConfigurationManager().askBeforeExitWhenIndexing = False
