"""Module for keeping track of files added to anki media folder. Only audio for now, potentially any media file that anki supports"""
from pathlib import Path

class MediaCacheRepository:
    def __init__(self, path) -> None:
        self.path = Path(path)
        self._cache = self._load()
    
    def _load(self):
        pass

    def save(self):
        pass

    def contains(self, filename):
        pass

    def add(self, filename):
        pass