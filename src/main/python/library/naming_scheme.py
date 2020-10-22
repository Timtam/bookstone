import functools
import string
from typing import Any, Dict, Iterable, Optional, Tuple

from .tags import Tags


class NamingScheme:

    # not associated with a series
    _standalone: str

    # contained within a series of books
    _volume: str

    # is this naming scheme available by default?
    _default: bool

    name: str

    def __init__(
        self, name: str, standalone: str, volume: str, default: bool = False
    ) -> None:

        self._default = default

        self.name = name
        self.standalone = standalone  # type: ignore
        self.volume = volume  # type: ignore

    def checkValid(f: Any) -> Any:
        def decorator(self, f: Any) -> Any:
            @functools.wraps(f)
            def check(self, value: str) -> Any:

                placeholders: Iterable[
                    Tuple[str, Optional[str], Optional[str], Optional[str]]
                ] = string.Formatter().parse(value)
                p: Tuple[str, Optional[str], Optional[str], Optional[str]]

                for p in placeholders:

                    if isinstance(p[1], str) and p[1] not in Tags:
                        raise AttributeError(f"invalid tag specified: {p[1]}")

                return f(self, value)

            return check

        return decorator

    @property
    def volume(self) -> str:
        return self._volume

    @volume.setter  # type: ignore
    @checkValid
    def volume(self, value: str) -> None:
        self._volume = value

    @property
    def standalone(self) -> str:
        return self._standalone

    @standalone.setter  # type: ignore
    @checkValid
    def standalone(self, value: str) -> None:
        self._standalone = value

    @property
    def default(self) -> bool:
        return self._default

    def serialize(self) -> Dict[str, str]:

        return {
            "name": self.name,
            "standalone": self._standalone,
            "volume": self._volume,
        }
