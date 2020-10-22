import sys

from fbs_runtime.application_context.PyQt5 import ApplicationContext

from audio import AudioManager
from configuration_manager import ConfigurationManager
from library import LibraryManager
from storage import Storage
from ui import WindowController
from ui.main_window import MainWindow
from utils import getConfigFile, getLibrariesDirectory

if __name__ == "__main__":
    appctxt: ApplicationContext = (
        ApplicationContext()
    )  # 1. Instantiate ApplicationContext

    store: Storage = Storage()
    store.setApplicationContext(appctxt)

    conf_manager: ConfigurationManager = ConfigurationManager()
    conf_manager.load(getConfigFile())

    lib_manager: LibraryManager = LibraryManager()
    store.setLibraryManager(lib_manager)
    am: AudioManager = AudioManager()
    store.setAudioManager(am)
    lib_manager.load(getLibrariesDirectory())
    am.initialize()

    controller: WindowController = WindowController()
    controller.pushWindow(MainWindow())

    exit_code: int = appctxt.app.exec_()  # 2. Invoke appctxt.app.exec_()
    conf_manager.save(getConfigFile())
    sys.exit(exit_code)
