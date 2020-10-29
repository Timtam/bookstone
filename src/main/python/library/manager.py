import hashlib
import json
import os
import os.path
import queue
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional, TextIO, cast

import natsort
from PyQt5.QtCore import QObject, pyqtSignal

from backend import Backend
from utils import getSupportedFileExtensions

from .constants import INDEXING, PROGRESS
from .library import Library
from .node import Node

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
    _library_hashes: List[bytes]

    def __init__(self) -> None:

        super().__init__()

        self._cancel_indexing = False
        self._indexing = False
        self._libraries = []
        self._library_hashes = []

        self.indexingStarted.connect(lambda: self._set_indexing(True))
        self.indexingFinished.connect(lambda: self._set_indexing(False))

    def addLibrary(self, lib: Library) -> None:
        self._libraries.append(lib)
        self._library_hashes.append(b"")

    def getLibraries(self) -> List[Library]:

        return natsort.natsorted(self._libraries[:], key=lambda l: l.getUUID())

    def removeLibrary(self, lib: Library) -> None:

        i: int = self._libraries.index(lib)

        del self._libraries[i]
        del self._library_hashes[i]

    def load(self, directory: str) -> None:

        if not os.path.exists(directory) or not os.path.isdir(directory):
            return

        libraries: List[str] = os.listdir(directory)
        lib: str
        libfile: TextIO

        for lib in libraries:

            libpath: str = os.path.join(directory, lib)

            with open(libpath, "r") as libfile:

                data: str = libfile.read()

                try:
                    ser: Dict[str, Any] = json.loads(data)
                except JSONDecodeError:
                    continue

                l: Library = Library()
                l.deserialize(ser)
                self._libraries.append(l)

                hash = hashlib.sha256()
                hash.update(data.encode("utf-8"))
                self._library_hashes.append(hash.digest())

    def save(self, directory: str) -> None:

        file: str
        libfile: TextIO

        if not os.path.exists(directory):
            os.makedirs(directory)

        # which files do already exist?

        libfiles: List[str] = []

        try:
            libfiles = os.listdir(directory)
        except FileNotFoundError:
            pass

        i: int
        lib: Library

        for i, lib in enumerate(self._libraries):

            libpath: str = os.path.join(directory, lib.getUUID() + ".json")

            ser: Dict[str, Any] = lib.serialize()
            data: str = json.dumps(ser, indent=2)

            # make sure we don't save if a file with the same content already exists
            if os.path.exists(libpath):

                hash = hashlib.sha256()
                hash.update(data.encode("utf-8"))

                if self._library_hashes[i] == hash.digest():

                    try:
                        libfiles.remove(lib.getUUID() + ".json")
                    except ValueError:
                        pass

                    continue

            with open(libpath, "w") as libfile:

                libfile.write(data)

            try:
                libfiles.remove(lib.getUUID() + ".json")
            except ValueError:
                pass

        # all remaining files in libfiles are no longer available / got removed
        for file in libfiles:
            os.remove(os.path.join(directory, file))

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

                next_path: str = next.getPath()

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

        self.indexingFinished.emit(True)

    def _set_indexing(self, indexing: bool) -> None:
        self._indexing = indexing

    def cancelIndexing(self) -> None:

        if not self._indexing and not self._cancel_indexing:
            return

        self._cancel_indexing = True
