from abc import ABC, abstractmethod
from typing import Dict

from anki_collection_scanner.application.field_config import FieldConfig


class FieldConfigRepositoryPort(ABC):
    @abstractmethod
    def save(self, config: Dict[str, FieldConfig]) -> None:
        """Persists field configs keyed by model name"""
        pass

    @abstractmethod
    def load(self) -> Dict[str, FieldConfig]:
        """Loads persisted field configs keyed by model name"""
        pass
