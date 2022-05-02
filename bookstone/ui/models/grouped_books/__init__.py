from typing import Any, Iterable, List, Optional, cast

from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt, QVariant

from library.book import Book
from library.library import Library

from .group import Group
from .grouped_books_item import GroupedBooksItem, GroupedBooksItemType

groups: List[Group] = [
    Group(
        tag="author",
        enabled=True,
    ),
    Group(
        tag="series",
        replacement_text="(no series)",
        enabled=True,
    ),
]


class GroupedBooksModel(QAbstractItemModel):

    _root: GroupedBooksItem

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self._root = GroupedBooksItem(type=GroupedBooksItemType.root)

    def update(self, libs: Iterable[Library]) -> None:

        book: Book
        lib: Library
        lib_item: GroupedBooksItem

        def getParentItem(parent: GroupedBooksItem, book: Book) -> GroupedBooksItem:

            item: GroupedBooksItem = parent

            for group in groups:

                if group.enabled:
                    item = group.getItem(item, book)

            return item

        self.modelAboutToBeReset.emit()  # type: ignore

        for lib in libs:

            lib_item = GroupedBooksItem(
                type=GroupedBooksItemType.library, parent=self._root, library=lib
            )

            self._root.insertChild(lib_item)

            for book in lib.getBooks():

                parent: GroupedBooksItem = getParentItem(lib_item, book)

                book_item: GroupedBooksItem = GroupedBooksItem(
                    type=GroupedBooksItemType.book,
                    parent=parent,
                    library=lib,
                    book_path=book.path,
                )
                parent.insertChild(book_item)

        self.modelReset.emit()  # type: ignore

    def getItem(self, index: QModelIndex) -> GroupedBooksItem:

        if index.isValid():

            item = index.internalPointer()

            if item:

                return cast(GroupedBooksItem, item)

        return self._root

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return self.getItem(parent).childCount

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return self.getItem(parent).columnCount

    def index(
        self, row: int, column: int, parent: QModelIndex = QModelIndex()
    ) -> QModelIndex:

        # don't return an index for children of other columns than column 0
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parent_item: Optional[GroupedBooksItem] = self.getItem(parent)

        assert parent_item is not None

        child_item: Optional[GroupedBooksItem] = parent_item.getChild(row)

        if child_item:
            return self.createIndex(row, column, child_item)

        return QModelIndex()

    def parent(self, child: QModelIndex) -> QModelIndex:  # type: ignore

        if not child.isValid():
            return QModelIndex()

        child_item: Optional[GroupedBooksItem] = self.getItem(child)

        assert child_item is not None

        parent_item: Optional[GroupedBooksItem] = child_item.parent

        if parent_item == self._root or not parent_item:
            return QModelIndex()

        return self.createIndex(cast(int, parent_item.childNumber), 0, parent_item)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:

        if not index.isValid():
            return QVariant()

        if role not in (
            Qt.DisplayRole,
            Qt.AccessibleTextRole,
        ):
            return QVariant()

        item: Optional[GroupedBooksItem] = self.getItem(index)

        assert item is not None

        if role == Qt.DisplayRole:
            return item.getColumnText(index.column())
        elif role == Qt.AccessibleTextRole:
            return item.getAccessibleColumnText(index.column())

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole
    ) -> Any:

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._root.columnNames[section]

        return QVariant()
