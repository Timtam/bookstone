from typing import List

from fbs_runtime.application_context.PyQt5 import ApplicationContext

from library.manager import LibraryManager
from ui.window import Window


class WindowController:

    _context: ApplicationContext
    _library_manager: LibraryManager
    _window_stack: List[Window] = []

    def __init__(self, context: ApplicationContext, library_manager: LibraryManager):
        self._context = context
        self._library_manager = library_manager

    def pushWindow(self, window: Window) -> None:

        self._window_stack.append(window)
        window.closed.connect(self.popWindow)

        try:
            self._window_stack[-2].hide()
        except IndexError:
            pass

        window.show()

    def popWindow(self) -> None:

        current: Window = self._window_stack[-1]
        current.hide()
        current.deleteLater()

        del self._window_stack[-1]

        try:
            self._window_stack[-1].show()
        except IndexError:
            self._library_manager.abortIndexing()
            self._context.app.exit()
