import sys

from fbs_runtime.application_context.PyQt5 import ApplicationContext

from audio.manager import AudioManager
from configuration_manager import ConfigurationManager
from library.manager import LibraryManager
from storage import Storage
from ui import WindowController
from ui.windows.main import MainWindow
from utils import getConfigFile

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
    lib_manager.load()
    am.initialize()

    controller: WindowController = WindowController()
    controller.pushWindow(MainWindow())

    exit_code: int = appctxt.app.exec_()  # 2. Invoke appctxt.app.exec_()
    conf_manager.save(getConfigFile())
    sys.exit(exit_code)
