from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Factory, Singleton
from PyQt5.QtWidgets import QApplication

from library.manager import LibraryManager

from .controller import WindowController
from .models.libraries import LibrariesModel
from .windows.libraries import LibrariesWindow
from .windows.main import MainWindow
from .windows.settings import SettingsWindow


class UIContainer(DeclarativeContainer):

    application: Dependency[QApplication] = Dependency()
    library_manager: Dependency[LibraryManager] = Dependency()

    settings_window = Factory(SettingsWindow)
    window_controller = Singleton(WindowController, application, library_manager)

    libraries_model = Factory(LibrariesModel, library_manager=library_manager)
    libraries_window = Factory(
        LibrariesWindow,
        library_manager=library_manager,
        libraries_model=libraries_model,
    )
    main_window = Factory(
        MainWindow,
        library_manager=library_manager,
        window_controller=window_controller,
        libraries_window_factory=libraries_window.provider,
        settings_window_factory=settings_window.provider,
    )