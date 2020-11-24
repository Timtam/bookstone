import os
import os.path
import queue
from typing import List, Optional, cast

import natsort
from PyQt5.QtCore import QObject, pyqtSignal

from backend import Backend
from utils import getLibrariesDirectory, getSupportedFileExtensions

from .constants import INDEXING, PROGRESS
from .library import Library
from .naming_scheme import NamingScheme
from .node import Node
from .tag_collection import TagCollection

# keeps track of all libraries
# it also manages the library indexing process and communicates the progress for the ui to display


class LibraryManager(QObject):

    # qt signals
    # used for communication with ui elements while indexing libraries

    # indexing operation started
    indexingStarted: pyqtSignal = pyqtSignal()
    # indexing operation finished
    # parameter: success
    indexingFinished: pyqtSignal = pyqtSignal(bool)
    # name of the library now going to be indexed
    indexingLibrary: pyqtSignal = pyqtSignal(str)
    # sent whenever something changes when indexing
    # parameter is a tuple
    # first parameter is an int (INDEXING enum)
    # second parameter is an int (PROGRESS enum)
    # all following parameters depend on the progress enum
    indexingProgress: pyqtSignal = pyqtSignal(tuple)

    _cancel_indexing: bool
    _indexing: bool
    _libraries: List[Library]

    def __init__(self) -> None:

        super().__init__()

        self._cancel_indexing = False
        self._indexing = False
        self._libraries = []

        self.indexingStarted.connect(lambda: self._set_indexing(True))
        self.indexingFinished.connect(lambda: self._set_indexing(False))

    def addLibrary(self, lib: Library) -> None:
        self._libraries.append(lib)

    def getLibraries(self) -> List[Library]:

        return natsort.natsorted(self._libraries[:], key=lambda l: l.getUUID())

    def removeLibrary(self, lib: Library) -> None:

        i: int = self._libraries.index(lib)

        if os.path.exists(lib.getFileName()):
            os.remove(lib.getFileName())

        del self._libraries[i]

    def load(self) -> None:

        if not os.path.exists(getLibrariesDirectory()) or not os.path.isdir(
            getLibrariesDirectory()
        ):
            return

        libraries: List[str] = os.listdir(getLibrariesDirectory())

        for lib in libraries:

            l: Optional[Library] = Library.fromFile(lib)

            if l:
                self._libraries.append(l)

    def index(self) -> None:

        _: str
        dir: str
        ext: str
        lib: Library

        self.indexingStarted.emit()

        for lib in self._libraries:

            self.indexingLibrary.emit(lib.getName())

            tree: Node = cast(Node, lib.getTree())
            tree.setNotIndexed()

            backend: Backend = cast(Backend, lib.getBackend())

            open: queue.Queue[Node] = queue.Queue()

            open.put(tree)

            while not open.empty():

                if self._cancel_indexing:
                    self.indexingFinished.emit(False)
                    return

                next: Node = open.get()

                self.indexingProgress.emit(
                    (
                        INDEXING.READING,
                        PROGRESS.UPDATE_MAXIMUM,
                        1,
                    )
                )

                self.indexingProgress.emit(
                    (
                        INDEXING.READING,
                        PROGRESS.VALUE,
                        1,
                    )
                )

                next_path: str = next.getPath().as_posix()

                dir_list: List[str] = backend.listDirectory(next_path)

                self.indexingProgress.emit(
                    (
                        INDEXING.READING,
                        PROGRESS.UPDATE_MAXIMUM,
                        len(dir_list),
                    )
                )

                for dir in dir_list:

                    if self._cancel_indexing:
                        self.indexingFinished.emit(False)
                        return

                    self.indexingProgress.emit(
                        (
                            INDEXING.READING,
                            PROGRESS.VALUE,
                            1,
                        )
                    )

                    new: Optional[Node] = tree.findChild(os.path.join(next_path, dir))

                    if new is None:
                        new = Node()
                        new.setName(dir)

                    if backend.isDirectory(os.path.join(next_path, dir)):
                        new.setDirectory()
                    else:
                        new.setFile()

                    if new.isFile():

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

            ns: NamingScheme = cast(NamingScheme, lib.getNamingScheme())

            # process all volumes

            for next in tree.iterChildren(
                depth=ns.getDepth(ns.volume.getPattern()), files=False
            ):

                print(next.getPath().as_posix())

                match: Optional[TagCollection] = ns.volume.match(
                    next.getPath().as_posix()
                )

                print(match)

        self.indexingFinished.emit(True)

    def _set_indexing(self, indexing: bool) -> None:
        self._indexing = indexing

    def cancelIndexing(self) -> None:

        if not self._indexing and not self._cancel_indexing:
            return

        self._cancel_indexing = True
