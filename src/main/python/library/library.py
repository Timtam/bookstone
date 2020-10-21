import uuid
from typing import Any, Dict, List, Optional, Type, cast

from backend import Backend
from backends import Backends

from .book import Book
from .node import Node


class Library:

    _backend: Optional[Backend]
    _books: List[Book]
    _name: str
    _tree: Node
    _uuid: str

    def __init__(self) -> None:

        self._backend = None
        self._books = []
        self._uuid = str(uuid.uuid4())
        self._name = ""
        self._tree = Node()

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
            "books": [b.serialize() for b in self._books],
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

            self._books.append(book_obj)

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
        return self._books[:]
