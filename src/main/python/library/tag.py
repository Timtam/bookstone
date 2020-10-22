import copy
from typing import Any, cast

import regex


class Tag:

    value: str
    _name: str
    _default: str
    _pattern: regex.Regex

    def __init__(self, name: str, value: str = "", pattern: str = "") -> None:

        self._name = name
        self.value = value
        self._default = value
        self._pattern = regex.compile(f"(?P<{self._name}>{pattern})")

    def isModified(self) -> bool:
        return self.value != self._default

    def serialize(self) -> str:
        return self.value

    def deserialize(self, serialized: str) -> None:
        self.value = serialized

    @property
    def name(self) -> str:
        return self._name

    @property
    def default(self) -> str:
        return self._default

    @property
    def pattern(self) -> regex.Regex:
        return self._pattern

    def __str__(self) -> str:
        return "Tag[{name}] = {value}".format(name=self._name, value=self.value)

    def __repr__(self) -> str:
        return str(self)

    def __call__(self) -> "Tag":

        return copy.copy(self)

    def __eq__(self, other: Any) -> bool:

        if isinstance(other, Tag):
            return (
                self._name == cast(Tag, other)._name
                and self.value == cast(Tag, other).value
            )
        elif isinstance(other, str):
            return self._name == other

        return NotImplemented
