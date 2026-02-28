"""
Define contracts for anki_connect dependencies
"""
from typing import Dict, Any
from abc import ABC, abstractmethod

class AnkiConnectPort(ABC):
    @abstractmethod
    def get_decks_and_ids(self) -> Dict[str, Any]:
        """Returns decks and ids from user's anki collection"""
        pass

    @abstractmethod
    def get_models_and_ids(self)-> Dict[str, Any]:
        """Returns models and ids from user's anki collection"""
        pass

    @abstractmethod
    def get_model_field_names(self, model_name: str)-> list[str]:
        """Returns models field names for a specific model"""
        pass

    @abstractmethod
    def get_deck_note_ids(self, deck_name: str)-> list[int]:
        """Returns note ids for a specific deck"""
        pass
    
    @abstractmethod
    def get_all_note_ids(self)-> list[int]:
        """Returns all note ids for a user's collection"""
        pass

    @abstractmethod
    def get_note_id_field_data(self, note_ids: list[int])-> list[Dict[str, Any]]:
        """Returns field data for a list of note ids"""
        pass