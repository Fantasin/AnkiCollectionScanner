import pytest

from anki_collection_scanner.infrastructure.snapshot_repository import JSONSnapshotRepository
from anki_collection_scanner.domain.collection_snapshot import CollectionSnapshot


def test_save_json_file_creation(tmp_path):
    full_path = tmp_path / "snapshot.json"
    repo = JSONSnapshotRepository(full_path)
    snapshot = CollectionSnapshot()

    repo.save_snapshot(snapshot)

    assert full_path.exists()

def test_load_json_empty(tmp_path):
    full_path = tmp_path / "snapshot.json"
    repo = JSONSnapshotRepository(full_path)

    snapshot = repo.load_snapshot()

    #TODO: add assertion for metadata
    assert snapshot.models == {}
    assert snapshot.decks == {}
    assert snapshot.notes == {}


def test_save_load_roundtrip(tmp_path):
    full_path = tmp_path / "snapshot.json"
    repo = JSONSnapshotRepository(full_path)
    snapshot = CollectionSnapshot()
    
    repo.save_snapshot(snapshot)
    snapshot = repo.load_snapshot()

    #TODO: add assertion for metadata
    assert snapshot.models == {}
    assert snapshot.decks == {}
    assert snapshot.notes == {}