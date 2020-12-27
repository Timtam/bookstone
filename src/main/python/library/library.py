import json
import os
import pathlib
import uuid
import warnings
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional, TextIO, Type, TypeVar, Union, cast

from backend import Backend
from backends import Backends
from configuration_manager import ConfigurationManager
from utils import getLibrariesDirectory

from .book import Book
from .naming_scheme import NamingScheme
from .node import Node

T = TypeVar("T", bound="Library")


class Library:

    _backend: Optional[Backend]
    _books: Dict[str, Book]
    _name: str
    _naming_scheme: Optional[NamingScheme]
    _tree: Node
    _uuid: str

    def __init__(self) -> None:

        self._backend = None
        self._books = {}
        self._uuid = str(uuid.uuid4())
        self._name = ""
        self._naming_scheme = None
        self._tree = Node()

    @classmethod
    def fromFile(cls: Type[T], file: str) -> Optional[T]:

        libfile: TextIO
        libpath: str = os.path.join(getLibrariesDirectory(), file)

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

    def getBackend(self) -> Optional[Backend]:
        return self._backend

    def setBackend(self, backend: Backend) -> None:
        self._backend = backend

        if self._tree is not None:
            self._tree.setBackend(self._backend)

        if self._name == "":
            self._name = backend.getPath()

    def serialize(self) -> Dict[str, Any]:

        return {
            "name": self._name,
            "backendName": cast(Backend, self._backend).getName(),
            "backend": cast(Backend, self._backend).serialize(),
            "uuid": self._uuid,
            "tree": cast(Node, self._tree).serialize(),
            "books": [b.serialize() for b in self._books.values()],
            "naming_scheme": cast(NamingScheme, self._naming_scheme).name,
        }

    def deserialize(self, serialized: Dict[str, Any]) -> None:

        b: Type[Backend]
        name: str = serialized.get("backendName", "")

        backend: Optional[Backend] = None

        for b in Backends:
            if b.getName() == name:
                backend = b()
                break

        if not backend:
            raise IOError("backend with name {name} not found".format(name=name))

        ser: Dict[str, Any] = serialized.get("backend", {})

        if not ser:
            raise IOError("no backend data supplied")

        backend.deserialize(ser)

        self._backend = backend
        self._tree.setBackend(self._backend)
        self._uuid = serialized.get("uuid", "")
        self._name = serialized.get("name", "")

        if not self._uuid:
            raise IOError("no valid UUID found")

        tree: Dict[str, Any] = serialized.get("tree", {})

        if tree:
            self._tree.deserialize(tree)

        books: List[Dict[str, Any]] = serialized.get("books", [])
        book: Dict[str, Any]

        for book in books:

            book_obj: Book = Book()
            book_obj.deserialize(book)

            self._books[book_obj.path.as_posix()] = book_obj

        scheme_s: str = serialized.get("naming_scheme", "")

        if not scheme_s:

            warnings.warn(
                f"library '{self._name}' has no naming scheme. Will use the default naming scheme instead."
            )

            self._naming_scheme = cast(
                List[NamingScheme], ConfigurationManager().namingSchemes
            )[0]

        else:

            scheme_idx: int = cast(List[NamingScheme], ConfigurationManager().namingSchemes).index(scheme_s)  # type: ignore

            self._naming_scheme = cast(
                List[NamingScheme], ConfigurationManager().namingSchemes
            )[scheme_idx]

    def getUUID(self) -> str:
        return self._uuid

    def __eq__(self, lib: Any) -> bool:
        if isinstance(lib, Library):
            return self._uuid == lib._uuid
        elif isinstance(lib, str):
            return self._uuid == lib
        return NotImplemented

    def getName(self) -> str:
        return self._name

    def setName(self, name: str) -> None:
        self._name = name

    def getTree(self) -> Node:
        return self._tree

    def getBooks(self) -> List[Book]:
        return list(self._books.values())

    def getNamingScheme(self) -> Optional[NamingScheme]:
        return self._naming_scheme

    def setNamingScheme(self, scheme: NamingScheme) -> None:
        self._naming_scheme = scheme

    def save(self) -> None:

        libfile: TextIO

        if not os.path.exists(getLibrariesDirectory()):
            os.makedirs(getLibrariesDirectory())

        libpath: str = self.getFileName()

        ser: Dict[str, Any] = self.serialize()
        data: str = json.dumps(ser, indent=2)

        with open(libpath, "w") as libfile:
            libfile.write(data)

    def getFileName(self) -> str:
        return os.path.join(getLibrariesDirectory(), self.getUUID() + ".json")

    def addBook(self, book: Book) -> None:
        self._books[book.path.as_posix()] = book

    def findBook(self, book: Union[Book, str, pathlib.Path]) -> Optional[Book]:

        if isinstance(book, Book):
            return self._books.get(cast(Book, book).path.as_posix(), None)
        elif isinstance(book, str):
            return self._books.get(cast(str, book), None)
        elif isinstance(book, pathlib.Path):
            return self._books.get(cast(pathlib.Path, book).as_posix(), None)

        return None

    def removeBook(self, book: Book) -> None:
        del self._books[book.path.as_posix()]
