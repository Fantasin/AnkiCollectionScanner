
from typing import Dict
from abc import ABC, abstractmethod

from anki_collection_scanner.domain.audio_models import AudioFile

class LocalAudioRepositoryPort:
    @abstractmethod
    def get_audio_files(self, words: list[str]) -> dict[str, AudioFile]:
        pass