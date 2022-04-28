import json
import os
import uuid
import warnings
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional, TextIO, Type, TypeVar, Union

import utils

from .book import Book
from .node import Node

T = TypeVar("T", bound="Library")


class Library:

    _books: Dict[str, Book]
    _name: str
    _path: str
    _tree: Node
    _uuid: uuid.UUID

    def __init__(self) -> None:

        self._books = {}
        self._uuid = uuid.uuid4()
        self._name = ""
        self._tree = Node()
        self._path = ""

    @classmethod
    def fromFile(cls: Type[T], file: str) -> Optional[T]:

        libfile: TextIO
        libpath: str = os.path.join(utils.getLibrariesDirectory(), file)

        with open(libpath, "r") as libfile:

            data: str = libfile.read()

            try:
                ser: Dict[str, Any] = json.loads(data)
            except JSONDecodeError:
                warnings.warn(f"invalid json data found in {libpath}")
                return None

        l: T = cls()
        l.deserialize(ser)

        return l

    def serialize(self) -> Dict[str, Any]:

        return {
            "name": self._name,
            "path": self._path,
            "uuid": str(self._uuid),
            "tree": self._tree.serialize(),
            "books": [b.serialize() for b in self._books.values()],
        }

    def deserialize(self, serialized: Dict[str, Any]) -> None:

        self._uuid = uuid.UUID(serialized.get("uuid", ""))
        self._name = serialized.get("name", "")
        self._path = serialized.get("path", "")

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

    def getBooks(self) -> List[Book]:
        return list(self._books.values())

    def save(self) -> None:

        libfile: TextIO

        if not os.path.exists(utils.getLibrariesDirectory()):
            os.makedirs(utils.getLibrariesDirectory())

        libpath: str = self.getFileName()

        ser: Dict[str, Any] = self.serialize()
        data: str = json.dumps(ser, indent=2)

        with open(libpath, "w") as libfile:
            libfile.write(data)

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
