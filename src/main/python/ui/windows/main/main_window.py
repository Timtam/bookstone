from typing import Any

from PyQt5.QtWidgets import QAction, QMenu, QMenuBar

from ui import Window, WindowController
from ui.windows.libraries import LibrariesWindow
from ui.windows.settings import SettingsWindow


class MainWindow(Window):

    file_menu: QMenu
    menu_bar: QMenuBar

    def __init__(self, *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)

        self.setWindowTitle("Bookstone")

        self.menu_bar = QMenuBar(self)
        self.file_menu = self.menu_bar.addMenu("&File")

        act: QAction

        act = QAction("Manage &libraries", self.file_menu)
        act.triggered.connect(self.showLibrariesWindow)
        self.file_menu.addAction(act)

        act = QAction("&Settings", self.file_menu)
        act.triggered.connect(self.showSettingsWindow)
        self.file_menu.addAction(act)

        act = QAction("&Exit", self.file_menu)
        act.triggered.connect(self.close)  # type: ignore
        self.file_menu.addAction(act)

    def showLibrariesWindow(self) -> None:

        WindowController().pushWindow(LibrariesWindow())

    def showSettingsWindow(self) -> None:

        WindowController().pushWindow(SettingsWindow())
