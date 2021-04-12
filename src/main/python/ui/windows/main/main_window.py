from typing import Any, cast

from PyQt5.QtWidgets import QAction, QLabel, QMenu, QMenuBar, QTreeView, QVBoxLayout

from library.manager import LibraryManager
from storage import Storage
from ui import Window, WindowController
from ui.models.libraries_books import LibrariesBooksModel
from ui.windows.libraries import LibrariesWindow
from ui.windows.settings import SettingsWindow


class MainWindow(Window):

    file_menu: QMenu
    libraries_model: LibrariesBooksModel
    libraries_view: QTreeView
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

        layout: QVBoxLayout = QVBoxLayout(self)

        libraries_view_label = QLabel("Books", self)
        layout.addWidget(libraries_view_label)
        self.libraries_model = LibrariesBooksModel(self)

        self.libraries_view = QTreeView(self)
        layout.addWidget(self.libraries_view)
        self.libraries_view.setModel(self.libraries_model)
        libraries_view_label.setBuddy(self.libraries_view)

        self.libraries_model.update(
            cast(LibraryManager, Storage().getLibraryManager()).getLibraries()
        )

    def showLibrariesWindow(self) -> None:
        def update():
            self.libraries_model.update(
                cast(LibraryManager, Storage().getLibraryManager()).getLibraries()
            )

        window: LibrariesWindow = LibrariesWindow()
        window.closed.connect(update)

        WindowController().pushWindow(window)

    def showSettingsWindow(self) -> None:

        WindowController().pushWindow(SettingsWindow())
