import os.path
from typing import Tuple

from storage import Storage


def getAppDirectory() -> str:
    return Storage().getApplicationContext()._resource_locator._dirs[0]


def getConfigDirectory() -> str:
    return os.path.join(getAppDirectory(), "config")


def getLibrariesDirectory() -> str:
    return os.path.join(getConfigDirectory(), "libraries")


def getConfigFile() -> str:
    return os.path.join(getConfigDirectory(), "settings.json")


def getSupportedFileExtensions() -> Tuple[str, ...]:
    return (".mp3", ".mp2", ".mp1", ".ogg", ".wav", ".aiff")
