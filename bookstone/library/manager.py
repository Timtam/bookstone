import os
import os.path
from typing import Dict, List, Optional, Tuple, cast

import natsort
from PyQt5.QtCore import QObject, QThread

from utils import getLibrariesDirectory
from workers.library_indexing import LibraryIndexingResult, LibraryIndexingWorker

from .book import Book
from .library import Library
from .node import Node

# keeps track of all libraries
# it also manages the indexing process


class LibraryManager(QObject):

    _indexing_state: Dict[Library, Tuple[LibraryIndexingWorker, QThread]]
    _libraries: List[Library]

    def __init__(self) -> None:

        super().__init__()

        self._indexing_state = {}
        self._libraries = []

    def addLibrary(self, lib: Library) -> None:
        self._libraries.append(lib)

    def getLibraries(self) -> List[Library]:
        def key(lib: Library) -> str:
            return lib.uuid

        return natsort.natsorted(self._libraries[:], key=key)

    def removeLibrary(self, lib: Library) -> None:

        i: int = self._libraries.index(lib)

        if lib in self._indexing_state:
            self._indexing_state[lib][1].requestInterruption()
            self._indexing_state[lib][1].quit()
            self._indexing_state[lib][1].wait()
            del self._indexing_state[lib]

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

    def startIndexing(self) -> None:

        lib: Library

        for lib in self._libraries:

            if lib in self._indexing_state:
                continue

            worker: LibraryIndexingWorker = LibraryIndexingWorker(lib)
            thread: QThread = QThread(parent=self)

            worker.moveToThread(thread)

            thread.started.connect(worker.run)
            worker.finished.connect(thread.quit)
            worker.finished.connect(worker.deleteLater)
            thread.finished.connect(thread.deleteLater)

            worker.result.connect(self._receive_indexing_result)

            self._indexing_state[lib] = (
                worker,
                thread,
            )

            thread.start()

    def _receive_indexing_result(self, result: LibraryIndexingResult) -> None:

        del self._indexing_state[result.library]

        lib: Library = result.library

        # comparing both trees
        new_tree: Node = result.tree
        old_tree = lib.getTree()
        current: Node
        new: Node
        path: List[Node] = []
        parent: Optional[Node]
        processed_nodes: List[Node] = []

        for current in new_tree.iterChildren(dirs=False):

            processed_nodes.append(current)

            if not old_tree.findChild(current):

                path.append(current)

                while not old_tree.findChild(cast(Node, current.getParent())):

                    new = Node()
                    new.setName(cast(Node, current.getParent()).getName())
                    new.setDirectory()

                    path.append(new)
                    current = cast(Node, current.getParent())

                parent = old_tree.findChild(cast(Node, current.getParent()))

                while len(path):

                    new = path.pop()

                    cast(Node, parent).addChild(new)
                    parent = new

        # all file nodes still within the tree, but not within the new tree, need to be dropped
        for current in old_tree.iterChildren(dirs=False):

            if current in processed_nodes:
                continue

            parent = current.getParent()

            while parent:

                parent.removeChild(current)

                if sum(1 for child in parent.iterChildren(dirs=False)) == 0:
                    current = parent
                    parent = parent.getParent()
                else:
                    parent = None

        # comparing new to old book analysis results
        books: List[Book] = result.books
        book: Book

        # iterate over all books and remove books with missing paths

        for book in lib.getBooks():
            if not old_tree.findChild(book.path.as_posix()):
                lib.removeBook(book)

        # add all books not in the library

        for book in books:

            if not lib.findBook(book):
                lib.addBook(book)

        lib.save()

    def abortIndexing(self) -> None:

        lib: Library
        threads: Tuple[LibraryIndexingWorker, QThread]

        for lib, threads in self._indexing_state.items():

            threads[1].requestInterruption()
            threads[1].quit()
            threads[1].wait()

        self._indexing_state.clear()
