from typing import Any, Callable, List, Optional, Tuple, Type, cast

from PyQt5.QtCore import QEvent, QObject
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QAction, QLabel, QMenu, QPushButton, QTableView, QVBoxLayout

from library.library import Library
from library.manager import LibraryManager
from ui.models.libraries import LibrariesModel
from ui.window import Window

from .backend_tab import BackendTab
from .details_dialog import DetailsDialog
from .ftp import FTPBackendTab
from .local import LocalBackendTab
from .smb import SMBBackendTab

BackendTabs: Tuple[Type[BackendTab], ...] = (
    LocalBackendTab,
    FTPBackendTab,
    SMBBackendTab,
)


class LibrariesWindow(Window):

    _library_manager: LibraryManager

    add_button: QPushButton
    add_actions: List[QAction]
    add_menu: QMenu
    close_button: QPushButton
    libraries_label: QLabel
    libraries_list: QTableView
    libraries_model: LibrariesModel

    def __init__(
        self,
        library_manager: LibraryManager,
        libraries_model: LibrariesModel,
        *args: Any,
        **kwargs: Any,
    ):

        super().__init__(*args, **kwargs)

        self._library_manager = library_manager

        self.setWindowTitle("Bookstone - Libraries")

        layout = QVBoxLayout(self)

        self.libraries_label = QLabel("Known libraries", self)
        layout.addWidget(self.libraries_label)

        self.libraries_list = QTableView(self)
        self.libraries_list.setTabKeyNavigation(False)
        self.libraries_model = libraries_model
        self.libraries_list.setModel(self.libraries_model)
        self.libraries_list.setSelectionMode(QTableView.SingleSelection)
        self.libraries_list.setSelectionBehavior(QTableView.SelectRows)
        self.libraries_list.installEventFilter(self)
        self.libraries_label.setBuddy(self.libraries_list)
        layout.addWidget(self.libraries_list)

        self.add_button = QPushButton("Add", self)
        layout.addWidget(self.add_button)

        self.add_menu = QMenu(self.add_button)

        self.add_actions = []

        i: int
        tab: Type[BackendTab]

        for tab in BackendTabs:
            act: QAction = QAction(tab.getName(), self.add_menu)
            self.add_menu.addAction(act)
            self.add_actions.append(act)
            act.triggered.connect(self.generateShowAddDialogLambda(tab))

        self.add_button.setMenu(self.add_menu)

        self.close_button = QPushButton("Close", self)
        self.close_button.pressed.connect(self.close)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

    def showAddDialog(self, tab: Type[BackendTab]) -> None:

        library: Library = Library()

        dlg: DetailsDialog = DetailsDialog(tab, library, self)
        success: int = dlg.exec_()

        if not success:
            return

        self._library_manager.addLibrary(library)
        self._library_manager.save(library)

        self.libraries_model.reloadLibraries()

    def generateShowAddDialogLambda(self, tab: Type[BackendTab]) -> Callable[[], None]:
        return lambda: self.showAddDialog(tab)

    def removeLibrary(self, lib: Library) -> None:

        self._library_manager.removeLibrary(lib)

        self.libraries_list.selectionModel().clearSelection()
        self.libraries_model.reloadLibraries()

    def editLibrary(self, lib: Library) -> None:

        tab: Optional[Type[BackendTab]] = next(
            (t for t in BackendTabs if t.matchesPath(lib.getPath())),
            None,
        )

        if not tab:
            return

        dlg: DetailsDialog = DetailsDialog(tab, lib, self)

        success: int = dlg.exec_()

        if not success:
            return

        self._library_manager.save(lib)
        self.libraries_model.updateLibrary(lib)

    def eventFilter(self, source: QObject, event: QEvent) -> bool:

        act: QAction

        if event.type() == QEvent.ContextMenu and source is self.libraries_list:

            index: int = (
                cast(QTableView, source)
                .indexAt(cast(QContextMenuEvent, event).pos())
                .row()
            )

            if index >= 0:
                lib: Library = self._library_manager.getLibraries()[index]
                menu: QMenu = QMenu(self.libraries_list)
                act = QAction("Edit", menu)
                act.triggered.connect(lambda: self.editLibrary(lib))
                menu.addAction(act)
                act = QAction("Remove", menu)
                act.triggered.connect(lambda: self.removeLibrary(lib))
                menu.addAction(act)
                menu.exec_()

                return True
        return super().eventFilter(source, event)
