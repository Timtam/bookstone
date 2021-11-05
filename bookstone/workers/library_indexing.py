import os.path
import queue
from dataclasses import dataclass
from typing import Dict, List, Optional, cast

from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

from backend import Backend
from exceptions import ThreadStoppedError
from library.book import Book
from library.library import Library
from library.naming_scheme import NamingScheme
from library.node import Node
from library.tag_collection import TagCollection
from utils import getSupportedFileExtensions


@dataclass
class LibraryIndexingResult:

    library: Library
    tree: Node
    books: List[Book]


class LibraryIndexingWorker(QObject):

    finished: pyqtSignal = pyqtSignal()
    library: Library
    result: pyqtSignal = pyqtSignal(LibraryIndexingResult)

    def __init__(self, library: Library):

        super().__init__()
        self.library = library

    @pyqtSlot()
    def run(self) -> None:

        try:

            tree: Node = self.indexFolderStructure(self.library)

            books: List[Book] = self.indexBooks(self.library, tree)

            self.result.emit(
                LibraryIndexingResult(library=self.library, tree=tree, books=books)
            )

            self.finished.emit()

        except ThreadStoppedError:
            pass

    def indexFolderStructure(self, lib: Library) -> Node:

        tree: Node = Node()
        tree.setDirectory()

        backend: Backend = cast(Backend, lib.getBackend())

        open: queue.Queue[Node] = queue.Queue()

        open.put(tree)

        while not open.empty():

            if QThread.currentThread().isInterruptionRequested():
                raise ThreadStoppedError()

            next: Node = open.get()

            next_path: str = next.getPath().as_posix()

            dir_list: List[str] = backend.listDirectory(next_path)

            for dir in dir_list:

                new: Node = Node()
                new.setName(dir)

                if backend.isDirectory(os.path.join(next_path, dir)):
                    new.setDirectory()
                else:
                    new.setFile()

                if new.isFile():

                    # check file extensions
                    _, ext = os.path.splitext(new.getName())

                    if not ext.lower() in getSupportedFileExtensions():
                        del new
                        continue

                next.addChild(new)

                if new.isDirectory():
                    open.put(new)

        return tree

    def indexBooks(self, lib: Library, tree: Node) -> List[Book]:

        book_map: Dict[Book, Node] = {}
        book: Book
        match: Optional[TagCollection]
        next: Node
        ns: NamingScheme = cast(NamingScheme, lib.getNamingScheme())

        # process all volumes

        for next in tree.iterChildren(
            depth=ns.getDepth(ns.volume.getPattern()), files=False
        ):

            match = ns.volume.match(next.getPath().as_posix())

            if match:
                book = Book(next.getPath(), match)

                book_map[book] = next

        # process all standalones

        for next in tree.iterChildren(
            depth=ns.getDepth(ns.standalone.getPattern()), files=False
        ):

            match = ns.standalone.match(next.getPath().as_posix())

            if match:
                book = Book(next.getPath(), match)

                book_map[book] = next

        # iterate over all books in the dict
        # if the book is already part of the tree of another book, remove it
        # this might happen whenever a path is detected as a book
        # although e.g. their subpaths were also recognized as books already

        books: List[Book] = list(book_map.keys())
        book_nodes: List[Node] = list(book_map.values())
        i: int = 0
        j: int = 0

        while i < len(book_map):

            for j in range(len(book_map)):

                if QThread.currentThread().isInterruptionRequested():
                    raise ThreadStoppedError()

                if i == j:
                    continue

                if book_nodes[i].isParentOf(book_nodes[j]):
                    del book_map[books[i]]
                    del books[i]
                    del book_nodes[i]
                    break

            else:
                i += 1

        return books
