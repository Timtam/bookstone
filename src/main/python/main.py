from fbs_runtime.application_context.PyQt5 import ApplicationContext

from storage import Storage
from ui.libraries_window import LibrariesWindow
from utils import getLibrariesDirectory

import sys

if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext

    store = Storage.getInstance()
    store.setApplicationContext(appctxt)
    store.getLibraryManager().load(getLibrariesDirectory())

    window = LibrariesWindow()
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)