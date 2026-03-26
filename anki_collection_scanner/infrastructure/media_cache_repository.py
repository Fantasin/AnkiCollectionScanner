"""Persist a lightweight cache of media filenames already added to Anki.

This module provides a small JSON-backed repository that tracks filenames that
have already been pushed to the Anki media collection. The current
implementation stores filenames as dictionary keys with ``True`` as the value.
That makes membership checks inexpensive and keeps the on-disk format simple.

The repository is intended for use as an optimization layer around calls such
as ``storeMediaFile``. It can help skip repeated uploads for files that were
already processed by this application, but it should not be treated as the
source of truth for what exists in the Anki media folder.

Example:
    >>> from anki_collection_scanner.infrastructure.media_cache_repository import MediaCacheRepository
    >>> cache = MediaCacheRepository()
    >>> if not cache.contains("example.mp3"):
    ...     # Upload the file to Anki first.
    ...     cache.add("example.mp3")

Bulk insert example:
    >>> cache = MediaCacheRepository()
    >>> cache.add_bulk(["audio1.mp3", "audio2.mp3"])
"""

import json

from pathlib import Path

_MEDIA_CACHE = Path(__file__).resolve().parents[0] / "media_cache.json"

class MediaCacheRepository:
    def __init__(self, path: Path | str = _MEDIA_CACHE) -> None:
        self.path = Path(path)
        self._cache = self._load()
    
    def _load(self) -> dict[str, bool]:
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._cache, f, ensure_ascii=False, indent=4)

    def contains(self, filename: str) -> bool:
        if filename in self._cache:
            return True
        return False

    def add(self, filename: str) -> None:
        self._cache[filename] = True
        self.save()

    def add_bulk(self, filenames: list[str]) -> None:
        for filename in filenames:
            self._cache[filename] = True
        self.save()
    
    def remove(self, filename: str) -> None:
        if filename in self._cache:
            del self._cache[filename]
            self.save()
            
    def clear(self) -> None:
        self._cache = {}
        self.save()

