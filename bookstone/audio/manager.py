import os.path
from typing import Optional

from PyQt5.QtCore import QObject, QThread

from workers.playback_worker import PlaybackWorker

os.add_dll_directory(os.getcwd())

from Bass4Py.bass import BASS, OutputDevice  # noqa: E402


class AudioManager(QObject):

    _bass: BASS
    _device: Optional[OutputDevice]
    _worker: PlaybackWorker
    _worker_thread: QThread

    def __init__(self) -> None:

        super().__init__()

        self._bass = BASS()
        self._device = None

    def initialize(self) -> None:

        self._device = self._bass.GetOutputDevice(-1)
        self._device.Init(44100, 0, -1)

        self._worker = PlaybackWorker()
        self._worker_thread = QThread(parent=self)
        self._worker.moveToThread(self._worker_thread)

        self._worker_thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._worker_thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker_thread.finished.connect(self._worker_thread.deleteLater)

        self._worker_thread.start()

    def uninitialize(self) -> None:

        self._worker_thread.requestInterruption()
        self._worker_thread.quit()
        self._worker_thread.wait()

    """
    def openStream(self, node: Node) -> AudioStream:

        device: OutputDevice = self._device

        backend: Backend = cast(Backend, node.getBackend())

        obj: BackendFile = backend.openFile(
            os.path.join(backend.getPath(), node.getPath())
        )

        return AudioStream(obj, device)
    """
