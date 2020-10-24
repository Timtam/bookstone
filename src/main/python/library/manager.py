import gc
import hashlib
import json
import os
import os.path
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, TextIO, Tuple

import natsort
from PyQt5.QtCore import QObject, pyqtSignal

from storage import Storage
from threads.folder_structure_reader import FolderStructureReaderThread
from threads.priorizable_thread import PriorizableThread
from threads.thread_pool import ThreadPool
from utils import getLibrariesDirectory

from .library import Library
from .node import Node


# keeps track of all libraries
# it also manages the library indexing process by enqueuing threads where necessary
class LibraryManager(QObject):

    indexingFinished: pyqtSignal = pyqtSignal(bool)
    # indexerResult = pyqtSignal(Library, Node)
    indexingStarted: pyqtSignal = pyqtSignal()
    # indexerStatusChanged = pyqtSignal(Library, str)
    _libraries: List[Library]
    _library_hashes: List[bytes]

    def __init__(self) -> None:

        QObject.__init__(self)

        self._libraries = []
        self._library_hashes = []

        Storage().getThreadPool().signals.threadFinished.connect(self._thread_finished)

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

    def isIndexing(self) -> bool:
        return (
            Storage().getThreadPool().currentThreadCount > 0
            or Storage().getThreadPool().waitingThreadCount > 0
        )

    def startIndexing(self) -> bool:

        if self.isIndexing():
            return False

        pool: ThreadPool = Storage().getThreadPool()
        lib: Library

        for lib in self._libraries:
            thread: FolderStructureReaderThread = FolderStructureReaderThread(lib)

            thread.signals.result.connect(self._thread_result)

            pool.enqueue(thread)

        self.indexingStarted.emit()

        return True

    def cancelIndexing(self) -> None:

        if not self.isIndexing():
            return

        Storage().getThreadPool().cancelAll()

    def _thread_result(self, params: Tuple[Library, Node]) -> None:

        child: Node
        lib: Library
        tree: Node

        lib, tree = params

        # self.indexerResult.emit(lib, tree)

        if lib in self._libraries:

            old_tree: Node = lib.getTree()
            old_tree.removeAllChildren()
            gc.collect()

            for child in tree.getChildren():
                old_tree.addChild(child)

    def _thread_finished(self, thread: PriorizableThread, success: bool) -> None:

        pool: ThreadPool = Storage().getThreadPool()

        if pool.currentThreadCount == 0 and pool.waitingThreadCount == 0:

            self.save(getLibrariesDirectory())

            self.indexingFinished.emit(success)

    def _indexer_status_changed(self, lib: Library, msg: str) -> None:
        self.indexerStatusChanged.emit(lib, msg)
