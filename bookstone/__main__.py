import cProfile
import pstats

from PyQt5.QtWidgets import QSplashScreen

import utils
from container import Container


def main() -> None:

    container = Container()

    app = container.application()

    splash_screen = QSplashScreen()

    splash_screen.show()

    splash_screen.showMessage("Loading configuration...")

    app.processEvents()  # type: ignore

    conf_manager = container.configuration_manager()
    conf_manager.load(utils.getConfigFile())

    lib_manager = container.library_manager()

    am = container.audio_manager()

    splash_screen.showMessage("Loading libraries...")

    app.processEvents()  # type: ignore

    lib_manager.load()

    splash_screen.showMessage("Initializing audio...")

    app.processEvents()  # type: ignore

    am.initialize()

    window = container.ui.main_window()

    controller = container.ui.window_controller()
    controller.pushWindow(window)
    splash_screen.finish(window)

    app.exec_()
    lib_manager.unload()
    am.uninitialize()
    conf_manager.save(utils.getConfigFile())


def run_profile(code: str) -> None:

    cProfile.runctx(code, globals(), locals(), "Profile.prof")

    s = pstats.Stats("Profile.prof")
    s.strip_dirs().sort_stats("time").print_stats()


if __name__ == "__main__":

    main()
    # run_profile("main()")
