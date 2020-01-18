from fbs_runtime.application_context.PyQt5 import ApplicationContext

from library import LibraryManager
from storage import Storage
from ui import WindowController
from ui.main_window import MainWindow
from utils import getLibrariesDirectory

import sys

if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext

    store = Storage.getInstance()
    store.setApplicationContext(appctxt)
    manager = LibraryManager()
    store.setLibraryManager(manager)
    manager.load(getLibrariesDirectory())

    controller = WindowController.getInstance()
    controller.pushWindow( MainWindow() )
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)