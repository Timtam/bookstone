from typing import TYPE_CHECKING, Tuple, Type

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Factory, Object, Singleton
from PyQt5.QtWidgets import QApplication

from library.manager import LibraryManager

from .controller import WindowController
from .models.libraries import LibrariesModel
from .windows.libraries import BackendTabs, LibrariesWindow
from .windows.main import MainWindow
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
    libraries_window: Factory[LibrariesWindow] = Factory(
        LibrariesWindow,
        library_manager=library_manager,
        libraries_model=libraries_model,
    )
    main_window: Factory[MainWindow] = Factory(
        MainWindow,
        library_manager=library_manager,
        window_controller=window_controller,
        libraries_window_factory=libraries_window.provider,
        settings_window_factory=settings_window.provider,
    )
