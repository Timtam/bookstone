from dataclasses import dataclass
from typing import Optional

from library.book import Book

from .grouped_books_item import GroupedBooksItem, GroupedBooksItemType


@dataclass
class Group:

    tag: str
    enabled: bool = False

    def getItem(self, parent: GroupedBooksItem, book: Book) -> GroupedBooksItem:

        group_item: Optional[GroupedBooksItem]

        group_item = parent.getChild(
            "group:" + parent._library.uuid + ";" + book.tags[self.tag].value
        )

        if not group_item:

            group_item = GroupedBooksItem(
                type=GroupedBooksItemType.group,
                library=parent._library,
                group_name=book.tags[self.tag].value,
                parent=parent,
            )

            parent.insertChild(group_item)

        return group_item
