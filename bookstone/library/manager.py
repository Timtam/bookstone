import json
import os
import os.path
import warnings
from dataclasses import dataclass
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional, TextIO, cast

from PyQt5.QtCore import QObject, QThread

from utils import getLibrariesDirectory
from workers.library_indexing import LibraryIndexingResult, LibraryIndexingWorker
from workers.library_saver import LibrarySaverWorker

from .book import Book
from .library import Library
from .node import Node

# stores all indexing state related information


@dataclass
class LibraryState:
    indexing_thread: Optional[QThread] = None
    indexing_worker: Optional[LibraryIndexingWorker] = None
    saver_thread: Optional[QThread] = None
    saver_worker: Optional[LibrarySaverWorker] = None
    last_indexing_status: str = "Waiting."


# keeps track of all libraries
# it also manages the indexing process


class LibraryManager(QObject):

    _library_states: Dict[Library, LibraryState]
    _libraries: List[Library]

    def __init__(self) -> None:

        super().__init__()

        self._library_states = {}
        self._libraries = []

    def addLibrary(self, lib: Library) -> None:
        self._libraries.append(lib)
        self._library_states[lib] = LibraryState()

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

    def startIndexing(self, lib: Optional[Library] = None) -> None:

        libs: List[Library]

        if lib:
            libs = [lib]
        else:
            libs = self._libraries

        for lib in libs:

            if self._library_states[lib].indexing_thread:
                continue

            worker: LibraryIndexingWorker = LibraryIndexingWorker(lib)
            thread: QThread = QThread(parent=self)

            worker.moveToThread(thread)

            thread.started.connect(worker.run)
            worker.finished.connect(thread.quit)
            worker.finished.connect(worker.deleteLater)
            thread.finished.connect(thread.deleteLater)

            worker.result.connect(self._receive_indexing_result)
            worker.status.connect(
                lambda msg: self._indexing_status(cast(Library, lib), msg)
            )

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

        # comparing new to old book analysis results
        books: List[Book] = result.books
        book: Book

        # iterate over all books and remove books with missing paths

        for book in lib.getBooks():
            if not new_tree.findChild(book.path):
                lib.removeBook(book)

        # add all books not in the library

        for book in books:

            if not lib.findBook(book):
                lib.addBook(book)

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

        worker: LibrarySaverWorker = LibrarySaverWorker(lib)
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
