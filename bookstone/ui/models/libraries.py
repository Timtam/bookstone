from typing import TYPE_CHECKING, Any, List, Optional, Tuple, Type

from PyQt5.QtGui import QStandardItem, QStandardItemModel

from library.library import Library
from library.manager import LibraryManager

if TYPE_CHECKING:
    from ui.windows.libraries.backend_tab import BackendTab


class LibrariesModel(QStandardItemModel):

    _backend_tabs: Tuple[Type["BackendTab"]]
    _libraries: List[Library]
    _library_manager: LibraryManager

    def __init__(
        self,
        library_manager: LibraryManager,
        backend_tabs: Tuple[Type["BackendTab"]],
        *args: Any,
        **kwargs: Any
    ):

        super().__init__(*args, **kwargs)

        self._backend_tabs = backend_tabs
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

            tab: Optional[Type["BackendTab"]] = next(
                (t for t in self._backend_tabs if t.matchesPath(lib.getPath())),
                None,
            )

            if tab:
                item = QStandardItem(tab.getName())
            else:
                item = QStandardItem("Unknown")

            item.setEditable(False)
            row.append(item)

            self.appendRow(row)

    def updateLibrary(self, lib: Library) -> None:

        index: int = self._libraries.index(lib)

        item: QStandardItem = self.item(index, 0)
        item.setText(lib.getName())
