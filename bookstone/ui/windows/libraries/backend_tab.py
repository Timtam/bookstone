import re
from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Type, TypeVar

from PyQt5.QtWidgets import QWidget

if TYPE_CHECKING:

    from ui.windows.library_window.details_dialog import DetailsDialog

T = TypeVar("T", bound="BackendTab")


class BackendTab(QWidget):

    _PATH_REGEX_: re.Pattern

    parent: "DetailsDialog"

    def __init__(self, parent: "DetailsDialog", *args: Any, **kwargs: Any) -> None:

        super().__init__(*args, **kwargs)

        self.parent = parent

    def isValid(self) -> bool:
        return True

    @staticmethod
    @abstractmethod
    def getName() -> str:
        pass

    @abstractmethod
    def getPath(self) -> str:
        pass

    @abstractmethod
    def setPath(self, path: str) -> None:
        pass

    @classmethod
    def matchesPath(cls: Type[T], path: str) -> bool:
        return bool(cls._PATH_REGEX_.match(path))
