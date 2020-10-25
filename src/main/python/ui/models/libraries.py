from typing import Any, List, cast

from PyQt5.QtGui import QStandardItem, QStandardItemModel

from backend import Backend
from library.library import Library
from storage import Storage


class LibrariesModel(QStandardItemModel):

    _libraries: List[Library]

    def __init__(self, *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)

        self._libraries = []

        self.reloadLibraries()

    def reloadLibraries(self) -> None:

        lib: Library

        self.clear()

        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Name", "Connection"])

        self._libraries = Storage().getLibraryManager().getLibraries()

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
