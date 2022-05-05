import os
import uuid
from typing import Any, Dict, List, Optional, Union

import utils

from .book import Book
from .node import Node


class Library:

    _books: Dict[str, Book]
    _groups: List[str]
    _name: str
    _path: str
    _tree: Node
    _uuid: uuid.UUID

    def __init__(self) -> None:

        self._books = {}
        self._groups = []
        self._uuid = uuid.uuid4()
        self._name = ""
        self._tree = Node()
        self._path = ""

    def serialize(self) -> Dict[str, Any]:

        return {
            "name": self._name,
            "path": self._path,
            "uuid": str(self._uuid),
            "tree": self._tree.serialize(),
            "books": [b.serialize() for b in self._books.values()],
            "groups": self._groups,
        }

    def deserialize(self, serialized: Dict[str, Any]) -> None:

        self._uuid = uuid.UUID(serialized.get("uuid", ""))
        self._name = serialized.get("name", "")
        self._path = serialized.get("path", "")
        self._groups = serialized.get("groups", [])

        tree: Dict[str, Any] = serialized.get("tree", {})

        if tree:
            self._tree.deserialize(tree)

        books: List[Dict[str, Any]] = serialized.get("books", [])
        book: Dict[str, Any]

        for book in books:

            book_obj: Book = Book()
            book_obj.deserialize(book)

            self._books[book_obj.path] = book_obj

    @property
    def uuid(self) -> str:
        return str(self._uuid)

    def __eq__(self, lib: Any) -> bool:
        if isinstance(lib, Library):
            return self._uuid == lib._uuid
        elif isinstance(lib, str):
            return str(self._uuid) == lib
        return NotImplemented

    def getName(self) -> str:
        return self._name

    def setName(self, name: str) -> None:
        self._name = name

    def getPath(self) -> str:
        return self._path

    def setPath(self, path: str) -> None:
        self._path = path

    def getTree(self) -> Node:
        return self._tree

    def setTree(self, tree: Node) -> None:
        self._tree = tree

    def getBooks(self) -> List[Book]:
        return list(self._books.values())

    def getFileName(self) -> str:
        return os.path.join(utils.getLibrariesDirectory(), str(self._uuid) + ".json")

    def addBook(self, book: Book) -> None:
        self._books[book.path] = book

    def findBook(self, book: Union[Book, str]) -> Optional[Book]:

        if isinstance(book, Book):
            return self._books.get(book.path, None)
        elif isinstance(book, str):
            return self._books.get(book, None)

        return None

    def removeBook(self, book: Book) -> None:
        del self._books[book.path]

    def __hash__(self) -> int:
        return self._uuid.int

    def setBooks(self, books: List[Book]) -> None:

        self._books.clear()

        for b in books:
            self._books[b.path] = b

    def getGroups(self) -> List[str]:
        return self._groups[:]

    def setGroups(self, groups: List[str]) -> None:
        self._groups = groups[:]
