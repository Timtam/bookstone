from dataclasses import dataclass
from typing import Optional

from library.book import Book

from .grouped_books_item import GroupedBooksItem, GroupedBooksItemType


@dataclass
class Group:

    tag: str
    replacement_text: str = ""

    def getItem(self, parent: GroupedBooksItem, book: Book) -> GroupedBooksItem:

        group_item: Optional[GroupedBooksItem]
        group_name: str

        if book.tags[self.tag].isModified() or self.replacement_text == "":
            group_name = book.tags[self.tag].value
        else:
            group_name = self.replacement_text

        group_item = parent.getChild(f"group:{parent._library.uuid};{group_name}")

        if not group_item:

            group_item = GroupedBooksItem(
                type=GroupedBooksItemType.group,
                library=parent._library,
                group_name=group_name,
                parent=parent,
            )

            parent.insertChild(group_item)

        return group_item
