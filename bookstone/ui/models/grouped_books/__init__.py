from typing import TYPE_CHECKING, Any, List, Optional, cast

from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt, QVariant

from library.book import Book
from library.library import Library

from .grouped_books_item import GroupedBooksItem, GroupedBooksItemType
from .groups import Groups

if TYPE_CHECKING:
    from library.manager import LibraryManager


class GroupedBooksModel(QAbstractItemModel):

    _library_manager: "LibraryManager"
    _root: GroupedBooksItem

    def __init__(
        self, library_manager: "LibraryManager", *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

        self._root = GroupedBooksItem(type=GroupedBooksItemType.root)
        self._library_manager = library_manager
        self._library_manager.libraryAdded.connect(self.update)
        self._library_manager.libraryUpdated.connect(self.update)
        self._library_manager.libraryRemoved.connect(lambda l: self.update(l, True))

        self.update()

    def update(self, lib: Optional[Library] = None, removed: bool = False) -> None:

        book: Book
        child_number: int
        lib_item: GroupedBooksItem
        libs: List[Library]

        def getParentItem(parent: GroupedBooksItem, book: Book) -> GroupedBooksItem:

            item: GroupedBooksItem = parent

            for group in [
                Groups[g] for g in parent._library.getGroups() if g in Groups
            ]:

                item = group.getItem(item, book)

            return item

        if lib:
            libs = [lib]
        else:
            libs = self._library_manager.getLibraries()

        self.modelAboutToBeReset.emit()  # type: ignore

        for lib in libs:

            lib_item = GroupedBooksItem(
                type=GroupedBooksItemType.library, parent=self._root, library=lib
            )

            if self._root.getChild(str(lib_item)):

                child_number = cast(
                    int,
                    cast(
                        "GroupedBooksItem", self._root.getChild(str(lib_item))
                    ).childNumber,
                )

                self._root.removeChild(child_number)

            else:

                child_number = -1

            if removed:
                continue

            self._root.insertChild(lib_item, child_number)

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
