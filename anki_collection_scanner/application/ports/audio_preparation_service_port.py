

from typing import Dict
from abc import ABC, abstractmethod

from anki_collection_scanner.domain.audio_models import AudioFile, AudioTransferObject

class AudioPreparationServicePort(ABC):
    @abstractmethod
    def prepare_audio_transfer_objects(self, deck_note_ids: list[int]) -> Dict[int, AudioTransferObject]:
        pass

    @abstractmethod
    def enrich_transfer_objects_with_audio_files(self, transfer_objects: Dict[int, AudioTransferObject], audio_files: Dict[str, AudioFile])-> Dict[int, AudioTransferObject]:
        pass

    @abstractmethod
    def extract_word_for_audio_retrieval(self, transfer_objects: dict[int, AudioTransferObject])-> list[str]:
        pass

