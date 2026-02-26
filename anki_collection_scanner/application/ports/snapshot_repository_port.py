"""
Define contracts for snapshot_repository dependencies
"""

from abc import ABC, abstractmethod

from anki_collection_scanner.domain.result import Result
from anki_collection_scanner.domain.collection_snapshot import CollectionSnapshot
from anki_collection_scanner.domain.exceptions import  SnapshotRepositoryError


class SnapshotRepositoryPort(ABC):
    @abstractmethod
    def save_snapshot(self, snapshot: CollectionSnapshot)-> Result[None, SnapshotRepositoryError]:
        """Saves collection snapshot"""
        pass

    @abstractmethod
    def load_snapshot(self) -> Result[CollectionSnapshot, SnapshotRepositoryError]:
        """Loads collection snapshot"""
        pass
