from typing import Any, cast

from PyQt5.QtCore import QRunnable

from .signal_handler import SignalHandler


class PriorizableThread(QRunnable):

    _cancel: bool = False
    _index: int = -1
    _priority: int = -1
    signals: SignalHandler

    def __init__(self) -> None:

        super().__init__()

        self.signals = SignalHandler()

    def cancel(self) -> None:
        self._cancel = True

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, PriorizableThread):
            return NotImplemented

        if self._priority == cast(PriorizableThread, other)._priority:
            return self._index < cast(PriorizableThread, other)._index
        return self._priority < cast(PriorizableThread, other)._priority

    def __gt__(self, other: Any) -> bool:

        if not isinstance(other, PriorizableThread):
            return NotImplemented

        if self._priority == cast(PriorizableThread, other)._priority:
            return self._index > cast(PriorizableThread, other)._index
        return self._priority > cast(PriorizableThread, other)._priority

    def __le__(self, other: Any) -> bool:

        if not isinstance(other, PriorizableThread):
            return NotImplemented

        if self._priority == cast(PriorizableThread, other)._priority:
            return self._index <= cast(PriorizableThread, other)._index
        return self._priority <= cast(PriorizableThread, other)._priority

    def __ge__(self, other: Any) -> bool:

        if not isinstance(other, PriorizableThread):
            return NotImplemented

        if self._priority == cast(PriorizableThread, other)._priority:
            return self._index >= cast(PriorizableThread, other)._index
        return self._priority >= cast(PriorizableThread, other)._priority

    def __eq__(self, other: Any) -> bool:

        if not isinstance(other, PriorizableThread):
            return NotImplemented
        return self._index == cast(PriorizableThread, other)._index

    def __ne__(self, other: Any) -> bool:
        if not isinstance(other, PriorizableThread):
            return NotImplemented
        return self._index != cast(PriorizableThread, other)._index

    @property
    def priority(self) -> int:
        return self._priority

    @priority.setter
    def priority(self, value: int) -> None:

        if self._priority >= 0:
            raise ValueError("priority can only be set once")

        self._priority = value

    @property
    def index(self) -> int:
        return self._index

    @index.setter
    def index(self, value: int) -> None:

        if self._index >= 0:
            raise ValueError("index can only be set once")

        self._index = value
