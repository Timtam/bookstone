from queue import Queue
from typing import TYPE_CHECKING, Any, List

from dependency_injector.providers import Factory
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtWidgets import (
    QAction,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QMenuBar,
    QTreeView,
)

from ui.controller import WindowController
from ui.models.grouped_books.grouped_books_item import (
    GroupedBooksItem,
    GroupedBooksItemType,
)
from ui.models.grouped_books.sorted_grouped_books_model import SortedGroupedBooksModel
from ui.window import Window
from ui.windows.libraries import LibrariesWindow
from ui.windows.settings import SettingsWindow

if TYPE_CHECKING:
    from ui.models.grouped_books import GroupedBooksModel


class MainWindow(Window):

    _current_index: str
    _expanded_items: List[str]
    _grouped_books_model_factory: Factory["GroupedBooksModel"]
    _libraries_window_factory: Factory[LibrariesWindow]
    _settings_window_factory: Factory[SettingsWindow]
    _window_controller: WindowController

    file_menu: QMenu
    libraries_model: "GroupedBooksModel"
    libraries_view: QTreeView
    menu_bar: QMenuBar
    sorted_libraries_model: SortedGroupedBooksModel

    def __init__(
        self,
        window_controller: WindowController,
        libraries_window_factory: Factory[LibrariesWindow],
        settings_window_factory: Factory[SettingsWindow],
        grouped_books_model_factory: Factory["GroupedBooksModel"],
        *args: Any,
        **kwargs: Any,
    ):

        super().__init__(*args, **kwargs)

        self._libraries_window_factory = libraries_window_factory
        self._settings_window_factory = settings_window_factory
        self._window_controller = window_controller
        self._grouped_books_model_factory = grouped_books_model_factory
        self._expanded_items = []

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
        act.triggered.connect(self.close)
        self.file_menu.addAction(act)

        layout: QHBoxLayout = QHBoxLayout(self)

        layout.setMenuBar(self.menu_bar)

        libraries_view_label = QLabel("Books", self)
        layout.addWidget(libraries_view_label)
        self.libraries_model = self._grouped_books_model_factory(parent=self)
        self.sorted_libraries_model = SortedGroupedBooksModel(self)
        self.sorted_libraries_model.setSourceModel(self.libraries_model)
        self.sorted_libraries_model.modelAboutToBeReset.connect(self._save_tree_state)
        self.sorted_libraries_model.modelReset.connect(self._restore_tree_state)

        self.libraries_view = QTreeView(self)
        layout.addWidget(self.libraries_view)
        self.libraries_view.setModel(self.sorted_libraries_model)
        self.libraries_view.setSortingEnabled(True)
        self.libraries_view.sortByColumn(1, Qt.AscendingOrder)
        self.libraries_view.setSizeAdjustPolicy(QTreeView.AdjustToContentsOnFirstShow)
        libraries_view_label.setBuddy(self.libraries_view)

        self.setLayout(layout)

        self.libraries_view.header().setSectionResizeMode(QHeaderView.ResizeToContents)

    def showLibrariesWindow(self) -> None:

        window: LibrariesWindow = self._libraries_window_factory()

        self._window_controller.pushWindow(window)

    def showSettingsWindow(self) -> None:

        self._window_controller.pushWindow(self._settings_window_factory())

    def _save_tree_state(self) -> None:

        open: Queue[QModelIndex] = Queue()
        next: QModelIndex
        index: QModelIndex
        source_index: QModelIndex
        item: GroupedBooksItem

        open.put(QModelIndex())

        while not open.empty():

            next = open.get()

            for i in range(self.sorted_libraries_model.rowCount(next)):

                index = self.sorted_libraries_model.index(i, 0, next)

                if not index.isValid():
                    continue

                if self.libraries_view.isExpanded(index):

                    source_index = self.sorted_libraries_model.mapToSource(index)

                    if not source_index.isValid():
                        continue

                    item = self.libraries_model.getItem(source_index)

                    self._expanded_items.append(str(item))

                if self.sorted_libraries_model.hasChildren(index):
                    open.put(index)

        index = self.libraries_view.currentIndex()

        if not index.isValid():
            return

        source_index = self.sorted_libraries_model.mapToSource(index)

        if not source_index.isValid():
            return

        item = self.libraries_model.getItem(source_index)

        self._current_index = str(item)

    def _restore_tree_state(self) -> None:

        open: Queue[QModelIndex] = Queue()
        next: QModelIndex
        i: int
        index: QModelIndex
        source_index: QModelIndex
        item: GroupedBooksItem

        open.put(QModelIndex())

        while not open.empty():

            next = open.get()

            for i in range(self.sorted_libraries_model.rowCount(next)):

                index = self.sorted_libraries_model.index(i, 0, next)

                if not index.isValid():
                    continue

                source_index = self.sorted_libraries_model.mapToSource(index)

                if not source_index.isValid():
                    continue

                item = self.libraries_model.getItem(source_index)

                try:

                    if str(item) == self._current_index:
                        self.libraries_view.setCurrentIndex(index)

                except AttributeError:
                    pass

                if item._type != GroupedBooksItemType.book:
                    self.libraries_view.setFirstColumnSpanned(i, next, True)

                    if str(item) in self._expanded_items:
                        self.libraries_view.setExpanded(index, True)

                    open.put(index)

        self._expanded_items.clear()

        self._current_index = ""
