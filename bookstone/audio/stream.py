from Bass4Py.bass import OutputDevice, Stream

from backend_file import BackendFile


class AudioStream:

    _obj: BackendFile
    _stream: Stream

    def __init__(self, obj: BackendFile, device: OutputDevice) -> None:

        self._obj = obj
        self._stream = device.CreateStreamFromFileObj(obj)

    def close(self) -> None:
        self._stream.Free()
