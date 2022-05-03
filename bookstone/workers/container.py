from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Factory
from PyQt5.QtWidgets import QApplication

from .library_indexing import LibraryIndexingWorker
from .library_saver import LibrarySaverWorker


class WorkerContainer(DeclarativeContainer):

    application: Dependency[QApplication] = Dependency()

    library_indexing_worker: Factory[LibraryIndexingWorker] = Factory(
        LibraryIndexingWorker, application=application
    )

    library_saver_worker: Factory[LibrarySaverWorker] = Factory(
        LibrarySaverWorker, application=application
    )
