import posixpath
import queue
import warnings
from dataclasses import dataclass
from typing import Dict, List, Optional, Pattern

import fs
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

from exceptions import ThreadStoppedError
from library.book import Book
from library.library import Library
from library.node import Node
from library.tag_collection import TagCollection
from library.tag_matching import Patterns, getPatternDepth, matchPattern
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
    status: pyqtSignal = pyqtSignal(str)

    def __init__(self, library: Library):

        super().__init__()
        self.library = library

    @pyqtSlot()
    def run(self) -> None:

        try:

            self.status.emit("Started.")

            tree: Node = self.indexFolderStructure(self.library)

            books: List[Book] = self.indexBooks(self.library, tree)

            self.status.emit("Finished.")

            self.result.emit(
                LibraryIndexingResult(library=self.library, tree=tree, books=books)
            )

            self.finished.emit()

        except ThreadStoppedError:
            self.status.emit("Aborted.")
            pass

    def indexFolderStructure(self, lib: Library) -> Node:

        node_count: int = 0
        tree: Node = Node()
        tree.setDirectory()

        open: queue.Queue[Node] = queue.Queue()

        open.put(tree)

        with fs.open_fs(lib.getPath()) as f:

            while not open.empty():

                if QThread.currentThread().isInterruptionRequested():
                    raise ThreadStoppedError()

                next: Node = open.get()

                next_path: str = next.getPath()

                dir_list: List[str] = f.listdir(next_path)

                for dir in dir_list:

                    node_count += 1

                    new: Node = Node()
                    new.setName(dir)

                    if f.isdir(next_path + "/" + dir):
                        new.setDirectory()
                    else:
                        new.setFile()

                    if new.isFile():

                        # check file extensions
                        _, ext = posixpath.splitext(new.getName())

                        if not ext.lower() in getSupportedFileExtensions():
                            del new
                            continue

                    next.addChild(new)

                    if new.isDirectory():
                        open.put(new)

                    self.status.emit(f"{node_count} nodes indexed.")

            return tree

    def indexBooks(self, lib: Library, tree: Node) -> List[Book]:

        book_map: Dict[Book, Node] = {}
        book: Book
        i: int
        match: Optional[TagCollection]
        next: Node
        pattern: Pattern[str]

        for pattern in Patterns:

            for next in tree.iterChildren(depth=getPatternDepth(pattern), files=False):

                if next in book_map.values():
                    warnings.warn(
                        "path was matched multiple times, will use first match only"
                    )
                    continue

                match = matchPattern(pattern, next.getPath())

                if match:
                    book = Book(next.getPath(), match)

                    book_map[book] = next

        # iterate over all books in the dict
        # if the book is already part of the tree of another book, remove it
        # this might happen whenever a path is detected as a book
        # although e.g. their subpaths were also recognized as books already

        books: List[Book] = list(book_map.keys())
        book_nodes: List[Node] = list(book_map.values())
        i = 0
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
