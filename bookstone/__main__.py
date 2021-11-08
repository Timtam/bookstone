import sys

import utils
from container import Container

if __name__ == "__main__":

    container = Container()

    app = container.application()

    conf_manager = container.configuration_manager()
    conf_manager.load(utils.getConfigFile())

    lib_manager = container.library_manager()

    am = container.audio_manager()
    lib_manager.load()
    am.initialize()

    controller = container.ui.window_controller()
    controller.pushWindow(container.ui.main_window())

    exit_code: int = app.exec_()
    am.uninitialize()
    conf_manager.save(utils.getConfigFile())
    sys.exit(exit_code)
