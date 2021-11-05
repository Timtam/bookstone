from typing import Any

from dependency_injector.providers import Factory
from PyQt5.QtWidgets import QAction, QLabel, QMenu, QMenuBar, QTreeView, QVBoxLayout

from library.manager import LibraryManager
from ui.controller import WindowController
from ui.models.libraries_books import LibrariesBooksModel
from ui.window import Window
from ui.windows.libraries import LibrariesWindow
from ui.windows.settings import SettingsWindow


class MainWindow(Window):

    _libraries_window_factory: Factory[LibrariesWindow]
    _library_manager: LibraryManager
    _settings_window_factory: Factory[SettingsWindow]
    _window_controller: WindowController

    file_menu: QMenu
    libraries_model: LibrariesBooksModel
    libraries_view: QTreeView
    menu_bar: QMenuBar

    def __init__(
        self,
        library_manager: LibraryManager,
        window_controller: WindowController,
        libraries_window_factory: Factory[LibrariesWindow],
        settings_window_factory: Factory[SettingsWindow],
        *args: Any,
        **kwargs: Any
    ):

        super().__init__(*args, **kwargs)

        self._libraries_window_factory = libraries_window_factory
        self._library_manager = library_manager
        self._settings_window_factory = settings_window_factory
        self._window_controller = window_controller

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

        self.libraries_model.update(self._library_manager.getLibraries())

        self._library_manager.startIndexing()

    def showLibrariesWindow(self) -> None:
        def update():
            self.libraries_model.update(self._library_manager.getLibraries())

        window: LibrariesWindow = self._libraries_window_factory()
        window.closed.connect(update)

        self._window_controller.pushWindow(window)

    def showSettingsWindow(self) -> None:

        self._window_controller.pushWindow(self._settings_window_factory())
