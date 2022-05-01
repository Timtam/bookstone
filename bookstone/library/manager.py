import os
import os.path
from dataclasses import dataclass
from typing import Dict, List, Optional, cast

from PyQt5.QtCore import QObject, QThread

from utils import getLibrariesDirectory
from workers.library_indexing import LibraryIndexingResult, LibraryIndexingWorker

from .book import Book
from .library import Library
from .node import Node

# stores all indexing state related information


@dataclass
class IndexingState:
    thread: Optional[QThread]
    worker: Optional[LibraryIndexingWorker]
    last_status: str = "Waiting."


# keeps track of all libraries
# it also manages the indexing process


class LibraryManager(QObject):

    _indexing_states: Dict[Library, IndexingState]
    _libraries: List[Library]

    def __init__(self) -> None:

        super().__init__()

        self._indexing_states = {}
        self._libraries = []

    def addLibrary(self, lib: Library) -> None:
        self._libraries.append(lib)
        self._indexing_states[lib] = IndexingState(thread=None, worker=None)

    def getLibraries(self) -> List[Library]:
        return self._libraries[:]

    def removeLibrary(self, lib: Library) -> None:

        i: int = self._libraries.index(lib)
        thread: QThread

        if lib in self._indexing_states:
            if self._indexing_states[lib].thread:
                thread = cast(QThread, self._indexing_states[lib].thread)
                thread.requestInterruption()
                thread.quit()
                thread.wait()
            del self._indexing_states[lib]

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
                self.addLibrary(l)

    def startIndexing(self, lib: Optional[Library] = None) -> None:

        libs: List[Library]

        if lib:
            libs = [lib]
        else:
            libs = self._libraries

        for lib in libs:

            if self._indexing_states[lib].thread:
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

            self._indexing_states[lib].thread = thread
            self._indexing_states[lib].worker = worker

            thread.start()

    def _receive_indexing_result(self, result: LibraryIndexingResult) -> None:

        lib: Library = result.library
        new_tree: Node = result.tree

        self._indexing_states[lib].thread = None
        self._indexing_states[lib].worker = None

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

        lib.save()

    def abortIndexing(self, lib: Optional[Library] = None) -> None:

        libs: List[Library]
        thread: QThread

        if lib:
            libs = [lib]
        else:
            libs = self._libraries

        for lib in libs:

            if not self._indexing_states[lib].thread:
                continue

            thread = cast(QThread, self._indexing_states[lib].thread)

            thread.requestInterruption()
            thread.quit()
            thread.wait()

            self._indexing_states[lib].thread = None
            self._indexing_states[lib].worker = None

    def _indexing_status(self, lib: Library, msg: str) -> None:
        self._indexing_states[lib].last_status = msg

    def getIndexingStatus(self, lib: Library) -> str:
        return self._indexing_states[lib].last_status

    def isIndexing(self, lib: Library) -> bool:
        return self._indexing_states[lib].thread is not None
