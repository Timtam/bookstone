from enum import IntFlag, auto
from typing import Any, Dict, List, Optional, Tuple, Union

from library.book import Book
from library.library import Library


class GroupedBooksItemType(IntFlag):

    book = auto()
    library = auto()
    root = auto()
    group = auto()


class GroupedBooksItem:

    _children_dict: Dict[str, "GroupedBooksItem"]
    _children_list: List["GroupedBooksItem"]
    _parent: Optional["GroupedBooksItem"]
    _library: Library
    _book_path: str
    _group_name: str
    _type: GroupedBooksItemType

    def __init__(
        self,
        type: GroupedBooksItemType,
        parent: Optional["GroupedBooksItem"] = None,
        library: Optional[Library] = None,
        book_path: Optional[str] = None,
        group_name: Optional[str] = None,
    ):

        self._type = type
        self._parent = parent
        self._children_dict = {}
        self._children_list = []

        if library:
            self._library = library
        if book_path is not None:
            self._book_path = book_path
        if group_name:
            self._group_name = group_name

    def __str__(self) -> str:

        if self._type == GroupedBooksItemType.root:
            return "root"
        elif self._type == GroupedBooksItemType.library:
            return f"lib:{self._library.uuid}"
        elif self._type == GroupedBooksItemType.book:
            return f"book:{self._library.uuid};{self._book_path}"
        elif self._type == GroupedBooksItemType.group:
            return f"group:{self._library.uuid};{self._group_name}"

        return NotImplemented

    @property
    def parent(self) -> Optional["GroupedBooksItem"]:
        return self._parent

    def getChild(self, index: Union[int, str]) -> Optional["GroupedBooksItem"]:

        try:
            if isinstance(index, str):
                return self._children_dict[index]
            elif isinstance(index, int):
                return self._children_list[index]
        except (IndexError, KeyError):
            return None

    @property
    def childCount(self) -> int:
        return len(self._children_dict)

    @property
    def childNumber(self) -> Optional[int]:

        if self._parent:
            return self._parent._children_list.index(self)
        return None

    def insertChild(self, child: "GroupedBooksItem", position: int = -1) -> bool:

        if position > len(self._children_dict):
            return False
        elif position < 0:
            position = len(self._children_dict)

        self._children_list.insert(position, child)
        self._children_dict[str(child)] = child

        return True

    def removeChild(self, child: Union["GroupedBooksItem", int]) -> bool:

        child_index: int
        child_str: str

        if isinstance(child, int):
            child_index = child
            child_str = str(self._children_list[child])
        elif isinstance(child, GroupedBooksItem):
            child_str = str(child)
            child_index = self._children_list.index(child)

        try:
            del self._children_dict[child_str]
            del self._children_list[child_index]
        except IndexError:
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

        book: Optional[Book]

        if column == 0:
            if self._type == GroupedBooksItemType.book:
                book = self._library.findBook(self._book_path)
                return book.tags["title"].value if book else "Unknown Book"
            elif self._type == GroupedBooksItemType.library:
                return self._library.getName()
            elif self._type == GroupedBooksItemType.group:
                return self._group_name
        elif column == 1:
            if self._type == GroupedBooksItemType.book:
                book = self._library.findBook(self._book_path)
                return book.tags["author"].value if book else "Unknown Book"
        elif column == 2:
            if self._type == GroupedBooksItemType.book:
                book = self._library.findBook(self._book_path)
                if book and book.tags["series"].isModified():
                    return book.tags["series"].value
                elif not book:
                    return "Unknown Book"
        elif column == 3:
            if self._type == GroupedBooksItemType.book:
                book = self._library.findBook(self._book_path)
                if book and book.tags["entry"].isModified():
                    return book.tags["entry"].value
                elif not book:
                    return "Unknown Book"

        return ""

    def getAccessibleColumnText(self, column: int) -> str:

        if column > 0 or self._type != GroupedBooksItemType.book:
            return self.getColumnText(column)

        return ", ".join(
            [
                f"{self.columnNames[c]}: {self.getColumnText(c)}"
                for c in range(self.columnCount)
                if self.getColumnText(c)
            ]
        )

    def __eq__(self, other: Any) -> bool:

        if isinstance(other, Library) and self._type == GroupedBooksItemType.library:
            return self._library.uuid == other.uuid
        elif isinstance(other, Book) and self._type == GroupedBooksItemType.book:
            return other == self._library.findBook(self._book_path)
        elif isinstance(other, GroupedBooksItem):
            return (
                (
                    self._type == GroupedBooksItemType.root
                    and other._type == GroupedBooksItemType.root
                )
                or (
                    self._type == GroupedBooksItemType.library
                    and other._type == GroupedBooksItemType.library
                    and self._library == other._library
                )
                or (
                    self._type == GroupedBooksItemType.book
                    and other._type == GroupedBooksItemType.book
                    and self._library == other._library
                    and self._book_path == other._book_path
                )
                or (
                    self._type == GroupedBooksItemType.group
                    and other._type == GroupedBooksItemType.group
                    and self._library == other._library
                    and self._group_name == other._group_name
                )
            )

        return NotImplemented
