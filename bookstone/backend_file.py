from abc import ABC, abstractmethod


class BackendFile(ABC):
    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def read(self, bytes: int = 0) -> bytes:
        pass

    @abstractmethod
    def seek(self, byte: int, whence: int = 0) -> int:
        pass

    @abstractmethod
    def tell(self) -> int:
        pass
