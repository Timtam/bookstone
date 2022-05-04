import json
import os
import os.path
import warnings
from dataclasses import dataclass
from json.decoder import JSONDecodeError
from typing import TYPE_CHECKING, Any, Dict, List, Optional, TextIO, cast

from dependency_injector.providers import Factory
from PyQt5.QtCore import QObject, QThread, pyqtSignal

from utils import getLibrariesDirectory
from workers.library_indexing import LibraryIndexingResult, LibraryIndexingWorker

from .library import Library
from .node import Node

if TYPE_CHECKING:
    from workers.library_saver import LibrarySaverWorker


# stores all indexing state related information


@dataclass
class LibraryState:
    indexing_thread: Optional[QThread] = None
    indexing_worker: Optional[LibraryIndexingWorker] = None
    saver_thread: Optional[QThread] = None
    saver_worker: Optional["LibrarySaverWorker"] = None
    last_indexing_status: str = "Waiting."


# keeps track of all libraries
# it also manages the indexing process


class LibraryManager(QObject):

    _library_states: Dict[Library, LibraryState]
    _libraries: List[Library]
    _library_indexing_worker_factory: Factory[LibraryIndexingWorker]
    _library_saver_worker_factory: Factory["LibrarySaverWorker"]

    libraryAdded: pyqtSignal = pyqtSignal(Library)
    libraryRemoved: pyqtSignal = pyqtSignal(Library)
    libraryUpdated: pyqtSignal = pyqtSignal(Library)

    def __init__(
        self,
        library_indexing_worker_factory: Factory[LibraryIndexingWorker],
        library_saver_worker_factory: Factory["LibrarySaverWorker"],
    ) -> None:

        super().__init__()

        self._library_states = {}
        self._libraries = []
        self._library_indexing_worker_factory = library_indexing_worker_factory
        self._library_saver_worker_factory = library_saver_worker_factory

    def addLibrary(self, lib: Library) -> None:
        self._libraries.append(lib)
        self._library_states[lib] = LibraryState()
        self.libraryAdded.emit(lib)

    def getLibraries(self) -> List[Library]:
        return self._libraries[:]

    def removeLibrary(self, lib: Library) -> None:

        i: int = self._libraries.index(lib)
        thread: QThread

        if lib in self._library_states:
            if self._library_states[lib].indexing_thread:
                thread = cast(QThread, self._library_states[lib].indexing_thread)
                thread.requestInterruption()
                thread.quit()
                thread.wait()
            if self._library_states[lib].saver_thread:
                thread = cast(QThread, self._library_states[lib].saver_thread)
                thread.requestInterruption()
                thread.quit()
                thread.wait()
            del self._library_states[lib]

        if os.path.exists(lib.getFileName()):
            os.remove(lib.getFileName())

        del self._libraries[i]
        self.libraryRemoved.emit(lib)

    def load(self) -> None:

        if not os.path.exists(getLibrariesDirectory()) or not os.path.isdir(
            getLibrariesDirectory()
        ):
            return

        libraries: List[str] = os.listdir(getLibrariesDirectory())

        for lib in libraries:

            libfile: TextIO
            libpath: str = os.path.join(getLibrariesDirectory(), lib)

            with open(libpath, "r") as libfile:

                data: str = libfile.read()

                try:
                    ser: Dict[str, Any] = json.loads(data)
                except JSONDecodeError:
                    warnings.warn(f"invalid json data found in {libpath}")
                    continue

            l: Library = Library()
            l.deserialize(ser)

            self.addLibrary(l)

        self.startIndexing()

    def startIndexing(self, lib: Optional[Library] = None) -> None:

        libs: List[Library]

        if lib:
            libs = [lib]
        else:
            libs = self._libraries

        for lib in libs:

            if self._library_states[lib].indexing_thread:
                continue

            worker: LibraryIndexingWorker = self._library_indexing_worker_factory(
                library=lib
            )
            thread: QThread = QThread(parent=self)

            worker.moveToThread(thread)

            thread.started.connect(worker.run)
            worker.finished.connect(thread.quit)
            worker.finished.connect(worker.deleteLater)
            thread.finished.connect(thread.deleteLater)

            worker.result.connect(self._receive_indexing_result)
            worker.status.connect(self._indexing_status)

            self._library_states[lib].indexing_thread = thread
            self._library_states[lib].indexing_worker = worker

            thread.start()

    def _receive_indexing_result(self, result: LibraryIndexingResult) -> None:

        lib: Library = result.library
        new_tree: Node

        self._library_states[lib].indexing_thread = None
        self._library_states[lib].indexing_worker = None

        if not result.tree:
            return

        new_tree = result.tree

        # we will simply replace the old tree with the new one
        lib.setTree(new_tree)

        # and the old books with the new ones

        lib.setBooks(result.books)

        self.libraryUpdated.emit(lib)

        self.save(lib)

    def abortIndexing(self, lib: Optional[Library] = None) -> None:

        libs: List[Library]
        thread: QThread

        if lib:
            libs = [lib]
        else:
            libs = self._libraries

        for lib in libs:

            if not self._library_states[lib].indexing_thread:
                continue

            thread = cast(QThread, self._library_states[lib].indexing_thread)

            thread.requestInterruption()
            thread.quit()
            thread.wait()

            self._library_states[lib].indexing_thread = None
            self._library_states[lib].indexing_worker = None

    def _indexing_status(self, lib: Library, msg: str) -> None:
        self._library_states[lib].last_indexing_status = msg

    def getIndexingStatus(self, lib: Library) -> str:
        return self._library_states[lib].last_indexing_status

    def isIndexing(self, lib: Library) -> bool:
        return self._library_states[lib].indexing_thread is not None

    def unload(self) -> None:

        self.abortIndexing()

        for lib in self._libraries:
            if lib not in self._library_states:
                continue

            if self._library_states[lib].saver_thread:
                thread = cast(QThread, self._library_states[lib].saver_thread)
                thread.requestInterruption()
                thread.quit()
                thread.wait()

                self._library_states[lib].saver_thread = None
                self._library_states[lib].saver_worker = None

    def save(self, lib: Library) -> None:

        if self._library_states[lib].saver_thread:
            return

        worker: LibrarySaverWorker = self._library_saver_worker_factory(library=lib)
        thread: QThread = QThread(parent=self)

        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        worker.finished.connect(lambda: self._saver_finished(lib))

        self._library_states[lib].saver_thread = thread
        self._library_states[lib].saver_worker = worker

        thread.start()

    def _saver_finished(self, lib: Library) -> None:

        self._library_states[lib].saver_thread = None
        self._library_states[lib].saver_worker = None
