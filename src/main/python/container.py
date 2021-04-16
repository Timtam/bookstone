from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Container as ContainerProvider
from dependency_injector.providers import Singleton
from fbs_runtime.application_context.PyQt5 import ApplicationContext

from audio.manager import AudioManager
from configuration_manager import ConfigurationManager
from library.manager import LibraryManager
from ui.container import UIContainer


class Container(DeclarativeContainer):

    application_context: Singleton[ApplicationContext] = Singleton(ApplicationContext)
    audio_manager = Singleton(AudioManager)
    configuration_manager = Singleton(ConfigurationManager)

    library_manager = Singleton(LibraryManager)

    # sub-container
    ui = ContainerProvider(
        UIContainer,
        application_context=application_context,
        library_manager=library_manager,
    )
