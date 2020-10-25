import string
from typing import Dict, Iterable, Optional, Tuple

from .tag import Tag
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
        self.standalone = standalone
        self.volume = volume

    def checkValid(self, value: str) -> None:

        placeholders: Iterable[
            Tuple[str, Optional[str], Optional[str], Optional[str]]
        ] = string.Formatter().parse(value)
        p: Tuple[str, Optional[str], Optional[str], Optional[str]]

        for p in placeholders:

            if isinstance(p[1], str) and p[1] not in Tags:
                raise AttributeError(f"invalid tag specified: {p[1]}")

    @property
    def volume(self) -> str:
        return self._volume

    @volume.setter
    def volume(self, value: str) -> None:

        self.checkValid(value)

        self._volume = value

    @property
    def standalone(self) -> str:
        return self._standalone

    @standalone.setter
    def standalone(self, value: str) -> None:

        self.checkValid(value)

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

    def resolveStandalone(self, tags: Iterable[Tag] = Tags) -> str:
        return self._standalone.format(**{t.name: t.value for t in tags})

    def resolveVolume(self, tags: Iterable[Tag] = Tags) -> str:
        return self._volume.format(**{t.name: t.value for t in tags})
