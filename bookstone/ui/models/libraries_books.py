from enum import IntFlag, auto
from typing import Any, Iterable, List, Optional, Tuple, Union, cast

from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt

from library.book import Book
from library.library import Library


class LibrariesBooksTreeItemType(IntFlag):

    book = auto()
    library = auto()
    root = auto()


class LibrariesBooksTreeItem:

    _children: List["LibrariesBooksTreeItem"]
    _parent: Optional["LibrariesBooksTreeItem"]
    _data: Optional[Union[Library, Book]]
    _type: LibrariesBooksTreeItemType

    def __init__(
        self,
        type: LibrariesBooksTreeItemType,
        parent: Optional["LibrariesBooksTreeItem"] = None,
        data: Optional[Union[Library, Book]] = None,
    ):

        self._type = type
        self._parent = parent
        self._data = data
        self._children = []

    @property
    def parent(self) -> Optional["LibrariesBooksTreeItem"]:
        return self._parent

    def getChild(self, index: int) -> Optional["LibrariesBooksTreeItem"]:

        try:
            return self._children[index]
        except IndexError:
            return None

    @property
    def childCount(self) -> int:
        return len(self._children)

    @property
    def childNumber(self) -> Optional[int]:

        if self._parent:
            return self._parent._children.index(self)
        return None

    def insertChild(self, child: "LibrariesBooksTreeItem", position: int = -1) -> bool:

        if position > len(self._children):
            return False
        elif position < 0:
            position = len(self._children)

        self._children.insert(position, child)

        return True

    def removeChild(self, child: Union["LibrariesBooksTreeItem", int]) -> bool:

        if isinstance(child, int):
            try:
                del self._children[child]
            except IndexError:
                return False
        elif isinstance(child, LibrariesBooksTreeItem):
            try:
                self._children.remove(child)
            except ValueError:
                return False

        return True

    @property
    def columnCount(self) -> int:
        return 4

    @property
    def columnNames(self) -> Tuple[str, ...]:
        return (
            "Title",
            "Author",
            "Series",
            "Entry",
        )

    def getColumnText(self, column: int) -> str:

        if column == 0:
            if self._type == LibrariesBooksTreeItemType.book:
                return cast(Book, self._data).tags["title"].value
            elif self._type == LibrariesBooksTreeItemType.library:
                return cast(Library, self._data).getName()
        elif column == 1:
            if self._type == LibrariesBooksTreeItemType.book:
                return cast(Book, self._data).tags["author"].value
        elif column == 2:
            if self._type == LibrariesBooksTreeItemType.book:
                if cast(Book, self._data).tags["series"].isModified():
                    return cast(Book, self._data).tags["series"].value
        elif column == 3:
            if self._type == LibrariesBooksTreeItemType.book:
                if cast(Book, self._data).tags["entry"].isModified():
                    return cast(Book, self._data).tags["entry"].value

        return ""

    def getAccessibleColumnText(self, column: int) -> str:

        if column > 0 or self._type != LibrariesBooksTreeItemType.book:
            return self.getColumnText(column)

        return ", ".join(
            [
                f"{self.columnNames[c]}: {self.getColumnText(c)}"
                for c in range(self.columnCount)
            ]
        )

    def __eq__(self, other: Any) -> bool:

        if (
            isinstance(other, Library)
            and self._type == LibrariesBooksTreeItemType.library
        ):
            return cast(Library, self._data).uuid == other.uuid
        elif isinstance(other, Book) and self._type == LibrariesBooksTreeItemType.book:
            return cast(Book, self._data).uuid == other.uuid
        elif isinstance(other, LibrariesBooksTreeItem):
            return (
                self._type == LibrariesBooksTreeItemType.root
                and other._type == LibrariesBooksTreeItemType.root
            ) or self == other._data

        return NotImplemented


class LibrariesBooksModel(QAbstractItemModel):

    _root: LibrariesBooksTreeItem

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self._root = LibrariesBooksTreeItem(type=LibrariesBooksTreeItemType.root)

    def update(self, libs: Iterable[Library]) -> None:

        book: Book
        lib: Library
        lib_item: LibrariesBooksTreeItem

        for lib in libs:

            lib_item = LibrariesBooksTreeItem(
                type=LibrariesBooksTreeItemType.library, parent=self._root, data=lib
            )

            self._root.insertChild(lib_item)

            for book in lib.getBooks():
                book_item: LibrariesBooksTreeItem = LibrariesBooksTreeItem(
                    type=LibrariesBooksTreeItemType.book, parent=lib_item, data=book
                )
                lib_item.insertChild(book_item)

    def getItem(self, index: QModelIndex) -> LibrariesBooksTreeItem:

        if index.isValid():

            item = LibrariesBooksTreeItem, index.internalPointer()

            if item:

                return cast(LibrariesBooksTreeItem, item[1])

        return self._root

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return self.getItem(parent).childCount

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return self.getItem(parent).columnCount

    def index(
        self, row: int, column: int, parent: QModelIndex = QModelIndex()
    ) -> QModelIndex:

        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        item = self.getItem(parent)

        child_item = item.getChild(row)

        if child_item:
            return self.createIndex(row, column, child_item)

        return QModelIndex()

    def parent(self, child: QModelIndex) -> QModelIndex:  # type: ignore

        if not child.isValid():
            return QModelIndex()

        item = self.getItem(child)

        parent_item = item.parent

        if parent_item == self._root or not parent_item:
            return QModelIndex()

        return self.createIndex(cast(int, parent_item.childNumber), 0, parent_item)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:

        if not index.isValid():
            return None

        if role not in (
            Qt.DisplayRole,
            Qt.AccessibleTextRole,
        ):
            return None

        item = self.getItem(index)

        if role == Qt.DisplayRole:
            return item.getColumnText(index.column())
        elif role == Qt.AccessibleTextRole:
            return item.getAccessibleColumnText(index.column())

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole
    ) -> str:

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._root.columnNames[section]

        return ""
