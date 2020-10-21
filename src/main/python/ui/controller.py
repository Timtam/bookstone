from typing import List

from py_singleton import singleton

from storage import Storage
from ui.window import Window


@singleton
class WindowController:

    _window_stack: List[Window] = []

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
            Storage().getApplicationContext().app.exit()
