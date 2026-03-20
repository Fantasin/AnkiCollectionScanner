import pytest

from unittest.mock import Mock
from anki_collection_scanner.application.usecases.sync_collection import SyncCollectionUseCase
from anki_collection_scanner.application.ports.anki_connect_port import AnkiConnectPort
from anki_collection_scanner.application.ports.snapshot_repository_port import SnapshotRepositoryPort
from anki_collection_scanner.domain.collection_snapshot.collection_snapshot import CollectionSnapshot

@pytest.fixture
def snapshot():
    return CollectionSnapshot()

@pytest.fixture
def mock_repo():
    return Mock(spec = SnapshotRepositoryPort)

@pytest.fixture
def mock_anki_client():
    return Mock(spec = AnkiConnectPort)

@pytest.fixture
def sync_use_case(mock_repo, mock_anki_client):
    return SyncCollectionUseCase(mock_repo, mock_anki_client)