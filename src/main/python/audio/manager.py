import os
import os.path
from typing import Optional, cast

from py_singleton import singleton

from backend import Backend
from backend_file import BackendFile
from library.node import Node

os.add_dll_directory(os.getcwd())

from Bass4Py.bass import BASS, OutputDevice  # noqa: E402

from .stream import AudioStream  # noqa: E402


@singleton
class AudioManager:

    _bass: BASS
    _device: Optional[OutputDevice]

    def __init__(self) -> None:

        self._bass = BASS()
        self._device = None

    def initialize(self) -> None:

        self._device = self._bass.GetOutputDevice(-1)
        self._device.Init(44100, 0, -1)

    def openStream(self, node: Node) -> AudioStream:

        device: OutputDevice = self._device

        backend: Backend = cast(Backend, node.getBackend())

        obj: BackendFile = backend.openFile(
            os.path.join(backend.getPath(), node.getPath())
        )

        return AudioStream(obj, device)
