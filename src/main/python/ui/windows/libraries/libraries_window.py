from typing import Any, Callable, List, Type, cast

from PyQt5.QtCore import QEvent, QObject
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import (
    QAction,
    QLabel,
    QMenu,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from backend import Backend
from library.library import Library
from library.manager import LibraryManager
from storage import Storage
from ui import Window
from ui.models.libraries import LibrariesModel
from utils import getLibrariesDirectory

from .backend_tab import BackendTab
from .backend_tabs import BackendTabs
from .details_dialog import DetailsDialog


class LibrariesWindow(Window):

    add_button: QPushButton
    add_actions: List[QAction]
    add_menu: QMenu
    close_button: QPushButton
    indexing_button: QPushButton
    libraries_label: QLabel
    libraries_list: QTableView
    libraries_model: LibrariesModel

    def __init__(self, *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)

        self.setWindowTitle("Bookstone - Libraries")

        layout = QVBoxLayout(self)

        self.libraries_label = QLabel("Known libraries", self)
        layout.addWidget(self.libraries_label)

        self.libraries_list = QTableView(self)
        self.libraries_list.setTabKeyNavigation(False)
        self.libraries_model = LibrariesModel()
        self.libraries_list.setModel(self.libraries_model)
        self.libraries_list.setSelectionMode(QTableView.SingleSelection)
        self.libraries_list.installEventFilter(self)
        self.libraries_label.setBuddy(self.libraries_list)
        layout.addWidget(self.libraries_list)

        self.add_button = QPushButton("Add", self)
        layout.addWidget(self.add_button)

        self.add_menu = QMenu(self.add_button)

        self.add_actions = []

        i: int
        tab: Type[BackendTab]

        for i, tab in enumerate(BackendTabs.values()):
            act: QAction = QAction(tab.getName(), self.add_menu)
            self.add_menu.addAction(act)
            self.add_actions.append(act)
            act.triggered.connect(self.generateShowAddDialogLambda(tab))

        self.add_button.setMenu(self.add_menu)

        self.indexing_button = QPushButton(self)
        layout.addWidget(self.indexing_button)

        self.close_button = QPushButton("Close", self)
        self.close_button.pressed.connect(self.close)  # type: ignore
        layout.addWidget(self.close_button)

        self.setLayout(layout)

        manager: LibraryManager = Storage().getLibraryManager()
        manager.indexingStarted.connect(self.indexingHandler)
        manager.indexingFinished.connect(self.indexingHandler)

        self.initializeIndexingButton()

    def showAddDialog(self, tab: Type[BackendTab]) -> None:

        library: Library = Library()

        dlg: DetailsDialog = DetailsDialog(tab, library, self)
        success: int = dlg.exec_()

        if not success:
            return

        store: Storage = Storage()
        store.getLibraryManager().addLibrary(library)
        store.getLibraryManager().save(getLibrariesDirectory())

        self.libraries_model.reloadLibraries()
        self.initializeIndexingButton()

    def generateShowAddDialogLambda(self, tab: Type[BackendTab]) -> Callable[[], None]:
        return lambda: self.showAddDialog(tab)

    def removeLibrary(self, lib: Library) -> None:

        manager: LibraryManager = Storage().getLibraryManager()

        manager.removeLibrary(lib)
        manager.save(getLibrariesDirectory())

        self.libraries_list.selectionModel().clearSelection()
        self.libraries_model.reloadLibraries()
        self.initializeIndexingButton()

    def editLibrary(self, lib: Library) -> None:

        dlg: DetailsDialog = DetailsDialog(
            BackendTabs[cast(Type[Backend], type(lib.getBackend()))], lib, self
        )

        success: int = dlg.exec_()

        if not success:
            return

        Storage().getLibraryManager().save(getLibrariesDirectory())
        self.libraries_model.updateLibrary(lib)

    def eventFilter(self, source: QObject, event: QEvent) -> bool:

        act: QAction

        if event.type() == QEvent.ContextMenu and source is self.libraries_list:

            index: int = source.indexAt(cast(QContextMenuEvent, event).pos()).row()

            if index >= 0:
                lib: Library = Storage().getLibraryManager().getLibraries()[index]
                menu: QMenu = QMenu(self.libraries_list)
                act = QAction("Edit", menu)
                act.triggered.connect(lambda: self.editLibrary(lib))
                menu.addAction(act)
                act = QAction("Remove", menu)
                act.triggered.connect(lambda: self.removeLibrary(lib))
                menu.addAction(act)
                menu.exec_()

                return True
        return QWidget.eventFilter(self, source, event)

    def close(self) -> bool:

        manager: LibraryManager = Storage().getLibraryManager()
        manager.indexingStarted.disconnect(self.indexingHandler)
        manager.indexingFinished.disconnect(self.indexingHandler)

        self.closed.emit()

        return super().close()

    def indexingHandler(self, success: Any = None) -> None:
        self.initializeIndexingButton()

    def startIndexing(self) -> None:
        Storage().getLibraryManager().startIndexing()
        self.initializeIndexingButton()

    def cancelIndexing(self) -> None:
        Storage().getLibraryManager().cancelIndexing()
        self.initializeIndexingButton()

    def initializeIndexingButton(self) -> None:

        manager: LibraryManager = Storage().getLibraryManager()

        libs: int = len(manager.getLibraries())

        if libs == 0:
            self.indexing_button.setEnabled(False)
        else:
            self.indexing_button.setEnabled(True)

        if not manager.isIndexing() or libs == 0:

            try:
                self.indexing_button.pressed.disconnect()
            except TypeError:
                pass

            self.indexing_button.pressed.connect(self.startIndexing)
            self.indexing_button.setText("Start indexing")

        else:

            try:
                self.indexing_button.pressed.disconnect()
            except TypeError:
                pass

            self.indexing_button.pressed.connect(self.cancelIndexing)
            self.indexing_button.setText("Cancel indexing")
