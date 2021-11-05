from typing import Any, List, cast

from PyQt5.QtGui import QStandardItem, QStandardItemModel

from backend import Backend
from library.library import Library
from library.manager import LibraryManager


class LibrariesModel(QStandardItemModel):

    _libraries: List[Library]
    _library_manager: LibraryManager

    def __init__(self, library_manager: LibraryManager, *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)

        self._library_manager = library_manager

        self._libraries = []

        self.reloadLibraries()

    def reloadLibraries(self) -> None:

        lib: Library

        self.clear()

        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Name", "Connection"])

        self._libraries = self._library_manager.getLibraries()

        for lib in self._libraries:

            item: QStandardItem
            row: List[QStandardItem] = []

            item = QStandardItem(lib.getName())
            item.setEditable(False)
            row.append(item)

            item = QStandardItem(cast(Backend, lib.getBackend()).getName())
            item.setEditable(False)
            row.append(item)

            self.appendRow(row)

    def updateLibrary(self, lib: Library) -> None:

        index: int = self._libraries.index(lib)

        item: QStandardItem = self.item(index, 0)
        item.setText(lib.getName())
