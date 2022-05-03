from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Container as ContainerProvider
from dependency_injector.providers import Singleton
from PyQt5.QtWidgets import QApplication

from audio.manager import AudioManager
from configuration_manager import ConfigurationManager
from library.manager import LibraryManager
from ui.container import UIContainer
from workers.container import WorkerContainer


class Container(DeclarativeContainer):

    application: Singleton[QApplication] = Singleton(QApplication, [])

    worker = ContainerProvider(WorkerContainer, application=application)

    library_manager = Singleton(
        LibraryManager,
        library_indexing_worker_factory=worker.library_indexing_worker.provider,
        library_saver_worker_factory=worker.library_saver_worker.provider,
    )

    ui = ContainerProvider(
        UIContainer,
        application=application,
        library_manager=library_manager,
    )

    audio_manager = Singleton(AudioManager)
    configuration_manager = Singleton(ConfigurationManager)
