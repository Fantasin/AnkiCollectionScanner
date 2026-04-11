
from abc import ABC, abstractmethod

class MediaCacheRepositoryPort(ABC):
    @abstractmethod
    def add(self, filename: str) -> None:
        pass

    @abstractmethod
    def contains(self, filename: str) -> bool:
        pass