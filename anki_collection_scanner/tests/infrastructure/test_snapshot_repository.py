import pytest

from anki_collection_scanner.infrastructure.snapshot_repository import JSONSnapshotRepository
from anki_collection_scanner.domain.collection_snapshot.collection_snapshot import CollectionSnapshot
from anki_collection_scanner.domain.domain_exceptions import SnapshotRepositoryError, SnapshotCorruptedError, SnapshotNotFoundError


def test_save_json_file_creation(tmp_path):
    full_path = tmp_path / "snapshot.json"
    repo = JSONSnapshotRepository(full_path)
    snapshot = CollectionSnapshot()

    save_result = repo.save_snapshot(snapshot)
    assert save_result.is_ok(), f"Save failed: {save_result.unwrap_err()}"

    assert full_path.exists()

def test_load_json_wrong_path(tmp_path):
    full_path = tmp_path / "test_error.json"
    repo = JSONSnapshotRepository(full_path)

    result = repo.load_snapshot()

    assert result.is_err()

    error = result.unwrap_err()
    assert isinstance(error, SnapshotNotFoundError)
    assert error.path == full_path



def test_save_load_roundtrip(tmp_path):
    full_path = tmp_path / "snapshot.json"
    repo = JSONSnapshotRepository(full_path)
    snapshot = CollectionSnapshot()
    
    repo.save_snapshot(snapshot)
    result = repo.load_snapshot()

    snapshot = result.unwrap()

    #TODO: add assertion for metadata
    assert snapshot.models == {}
    assert snapshot.decks == {}
    assert snapshot.notes == {}