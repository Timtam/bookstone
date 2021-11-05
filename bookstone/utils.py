import os.path
import sys
from typing import Tuple


def getAppDirectory() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def getConfigDirectory() -> str:
    return os.path.join(getAppDirectory(), "config")


def getLibrariesDirectory() -> str:
    return os.path.join(getConfigDirectory(), "libraries")


def getConfigFile() -> str:
    return os.path.join(getConfigDirectory(), "settings.json")


def getSupportedFileExtensions() -> Tuple[str, ...]:
    return (".mp3", ".mp2", ".mp1", ".ogg", ".wav", ".aiff")
