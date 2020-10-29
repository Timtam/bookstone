from typing import Any, Callable, List, Tuple, Type, Union, cast

from PyQt5.QtCore import QEvent, QObject, Qt
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import (
    QAction,
    QLabel,
    QMenu,
    QProgressDialog,
    QPushButton,
    QTableView,
    QVBoxLayout,
)

from backend import Backend
from library.constants import INDEXING, PROGRESS
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

        for i, tab in enumerate(BackendTabs.values()):
            act: QAction = QAction(tab.getName(), self.add_menu)
            self.add_menu.addAction(act)
            self.add_actions.append(act)
            act.triggered.connect(self.generateShowAddDialogLambda(tab))

        self.add_button.setMenu(self.add_menu)

        self.indexing_button = QPushButton("Index libraries", self)
        self.indexing_button.pressed.connect(self.runIndexer)
        layout.addWidget(self.indexing_button)

        self.close_button = QPushButton("Close", self)
        self.close_button.pressed.connect(self.close)  # type: ignore
        layout.addWidget(self.close_button)

        self.setLayout(layout)

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
        return super().eventFilter(source, event)

    def runIndexer(self) -> None:

        dlg: QProgressDialog
        current_value: int = 0
        maximum: int = 0
        manager: LibraryManager = Storage().getLibraryManager()

        def library_fun(lib: str) -> None:

            nonlocal current_value, maximum

            dlg.setWindowTitle(f"Bookstone - Indexing library {lib}...")

            dlg.reset()

            current_value = 0
            maximum = 0
            dlg.setValue(current_value)
            dlg.setMaximum(maximum)

        def progress_fun(t: Tuple[int, int, Union[str, int]]) -> None:

            nonlocal current_value, maximum

            op: int = t[0]
            msg: int = t[1]

            if op == INDEXING.READING and msg == PROGRESS.VALUE:
                current_value += cast(int, t[2])
                dlg.setValue(current_value)
            elif op == INDEXING.READING and msg == PROGRESS.UPDATE_MAXIMUM:
                maximum += cast(int, t[2])
                dlg.setMaximum(maximum)
            elif op == INDEXING.READING and msg == PROGRESS.MESSAGE:
                dlg.setLabelText(
                    cast(str, t[2]).format(value=current_value, maximum=maximum)
                )

        def finished_fun(success: bool) -> None:

            nonlocal dlg

            if not success:
                dlg.cancel()
            else:
                dlg.close()

        manager.indexingFinished.connect(finished_fun)
        manager.indexingLibrary.connect(library_fun)
        manager.indexingProgress.connect(progress_fun)

        dlg = QProgressDialog(self)
        dlg.setAutoClose(False)
        dlg.setAutoReset(False)

        dlg.setWindowModality(Qt.WindowModal)

        manager.index()

        manager.indexingFinished.disconnect(finished_fun)
        manager.indexingLibrary.disconnect(library_fun)
        manager.indexingProgress.disconnect(progress_fun)
