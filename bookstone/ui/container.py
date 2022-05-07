from typing import TYPE_CHECKING, Tuple, Type

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Factory, Object, Singleton
from PyQt5.QtWidgets import QApplication

from library.manager import LibraryManager

from .controller import WindowController
from .models.grouped_books import GroupedBooksModel
from .models.libraries import LibrariesModel
from .windows.libraries import BackendTabs, LibrariesWindow
from .windows.main import MainWindow
from .windows.main.groups_dialog import GroupsDialog
from .windows.settings import SettingsWindow

if TYPE_CHECKING:
    from .windows.libraries.backend_tab import BackendTab


class UIContainer(DeclarativeContainer):

    application: Dependency[QApplication] = Dependency()
    library_manager: Dependency[LibraryManager] = Dependency()

    settings_window: Factory[SettingsWindow] = Factory(SettingsWindow)
    window_controller: Singleton[WindowController] = Singleton(
        WindowController, application
    )
    backend_tabs: Object[Tuple[Type["BackendTab"], ...]] = Object(BackendTabs)

    libraries_model: Factory[LibrariesModel] = Factory(
        LibrariesModel, library_manager=library_manager, backend_tabs=backend_tabs
    )
    grouped_books_model: Factory[GroupedBooksModel] = Factory(
        GroupedBooksModel, library_manager=library_manager
    )
    libraries_window: Factory[LibrariesWindow] = Factory(
        LibrariesWindow,
        library_manager=library_manager,
        libraries_model=libraries_model,
    )
    groups_dialog: Factory[GroupsDialog] = Factory(
        GroupsDialog, library_manager=library_manager
    )
    main_window: Factory[MainWindow] = Factory(
        MainWindow,
        window_controller=window_controller,
        libraries_window_factory=libraries_window.provider,
        settings_window_factory=settings_window.provider,
        grouped_books_model_factory=grouped_books_model.provider,
        groups_dialog_factory=groups_dialog.provider,
    )
