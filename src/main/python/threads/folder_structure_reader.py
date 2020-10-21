import copy
import os.path
import queue
from typing import List, Optional, cast

from PyQt5.QtCore import pyqtSlot

from backend import Backend
from library.library import Library
from library.node import Node
from utils import getSupportedFileExtensions

from .priorizable_thread import PriorizableThread


class FolderStructureReaderThread(PriorizableThread):

    _library: Library
    priority: int

    def __init__(self, library: Library) -> None:

        super().__init__()

        self._library = library
        self.priority = 0

    @pyqtSlot()
    def run(self) -> None:

        lib: Library = self._library

        # self.signals.statusChanged.emit(lib, 'Starting index operation')

        tree: Node = copy.deepcopy(lib.getTree())

        tree.setNotIndexed()

        backend: Backend = cast(Backend, lib.getBackend())

        open: queue.Queue = queue.Queue()

        open.put(tree)

        while not open.empty():

            if self._cancel:
                self.signals.finished.emit(False)
                return

            next: Node = open.get()

            next_path: str = next.getPath()

            # self.signals.statusChanged.emit(lib, 'Processing {path}'.format(path=next_path))

            dir_list: List[str] = backend.listDirectory(next_path)
            dir: str

            for dir in dir_list:

                if self._cancel:
                    self.signals.finished.emit(False)
                    return

                new: Optional[Node] = tree.findChild(os.path.join(next_path, dir))

                if new is None:
                    new = Node()
                    new.setName(dir)

                if backend.isDirectory(os.path.join(next_path, dir)):
                    new.setDirectory()
                else:
                    new.setFile()

                if new.isFile():

                    _: str
                    ext: str

                    # check file extensions
                    _, ext = os.path.splitext(new.getName())

                    if not ext.lower() in getSupportedFileExtensions():
                        if new.getParent() is not None:
                            next.removeChild(new)
                        continue
                    else:
                        new.setIndexed()

                if next.findChild(new) is None:
                    next.addChild(new)

                if new.isDirectory():
                    open.put(new)

            next.setIndexed()

        tree.clean()

        self.signals.result.emit(
            (
                lib,
                tree,
            )
        )

        self.signals.finished.emit(True)
