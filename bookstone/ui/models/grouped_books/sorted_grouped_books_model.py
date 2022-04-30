import warnings
from typing import TYPE_CHECKING, Optional, cast

from natsort import NatsortKeyType, natsort_keygen
from PyQt5.QtCore import QModelIndex, QSortFilterProxyModel

from .grouped_books_item import GroupedBooksItemType

if TYPE_CHECKING:
    from library.book import Book

    from . import GroupedBooksModel
    from .grouped_books_item import GroupedBooksItem


class SortedGroupedBooksModel(QSortFilterProxyModel):

    natsort_key: NatsortKeyType = natsort_keygen()

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:

        model: "GroupedBooksModel" = cast("GroupedBooksModel", self.sourceModel())

        left_item: "GroupedBooksItem" = model.getItem(left)
        right_item: "GroupedBooksItem" = model.getItem(right)
        left_book: Optional["Book"]
        right_book: Optional["Book"]
        left_str: str
        right_str: str

        # assuming that we don't (!) need to compare two different item levels (group and book for example)

        if left_item._type == GroupedBooksItemType.group:
            return str(left_item) < str(right_item)
        elif left_item._type == GroupedBooksItemType.library:
            return True  # don't re-sort libraries
        elif left_item._type == GroupedBooksItemType.book:

            left_book = left_item._library.findBook(left_item._book_path)
            right_book = right_item._library.findBook(right_item._book_path)

            if not left_book or not right_book:
                warnings.warn("book could not be found when sorting")
                return False

            left_str = (
                left_book.tags["author"].value
                + " "
                + left_book.tags["series"].value
                + " "
                + left_book.tags["entry"].value
                + " "
                + left_book.tags["title"].value
                + " "
                + left_book.tags["subtitle"].value
            )
            right_str = (
                right_book.tags["author"].value
                + " "
                + right_book.tags["series"].value
                + " "
                + right_book.tags["entry"].value
                + " "
                + right_book.tags["title"].value
                + " "
                + right_book.tags["subtitle"].value
            )

            return self.natsort_key(left_str) < self.natsort_key(right_str)  # type: ignore

        return False

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        return True
