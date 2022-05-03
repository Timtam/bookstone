import json
from typing import IO, Any, Dict

import fs
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication

from library.library import Library
from utils import getLibrariesDirectory


class LibrarySaverWorker(QObject):

    application: QApplication
    finished: pyqtSignal = pyqtSignal()
    library: Library

    def __init__(self, application: QApplication, library: Library) -> None:

        super().__init__()

        self.application = application
        self.library = library

    @pyqtSlot()
    def run(self) -> None:

        ser: Dict[str, Any] = self.library.serialize()
        data: str = json.dumps(ser, indent=2)

        with fs.open_fs("temp://bookstone") as temp_fs:

            temp_file: IO[str] = temp_fs.open(f"{self.library.uuid}.json", mode="w")

            chunk_size: int = 1024 * 1024
            offset: int = 0

            while offset < len(data):

                if QThread.currentThread().isInterruptionRequested():
                    return

                self.application.processEvents()  # type: ignore

                temp_file.write(data[offset : offset + chunk_size])

                offset += chunk_size

            temp_file.close()

            local_fs: fs.osfs.OSFS = fs.osfs.OSFS(getLibrariesDirectory(), create=True)

            fs.move.move_file(
                temp_fs,
                f"{self.library.uuid}.json",
                local_fs,
                f"{self.library.uuid}.json",
            )

            local_fs.close()

        self.finished.emit()
