from typing import TYPE_CHECKING, Any, Optional

from PyQt5.QtWidgets import QWidget

from backend import Backend

if TYPE_CHECKING:

    from ui.windows.library_window.details_dialog import DetailsDialog


class BackendTab(QWidget):

    backend: Optional[Backend]
    parent: "DetailsDialog"

    def __init__(
        self,
        parent: "DetailsDialog",
        backend: Optional[Backend],
        *args: Any,
        **kwargs: Any
    ) -> None:

        super().__init__(*args, **kwargs)

        self.parent = parent
        self.backend = backend

    def isValid(self) -> bool:
        return True

    def getBackend(self) -> Backend:
        pass

    @staticmethod
    def getName() -> str:
        pass
