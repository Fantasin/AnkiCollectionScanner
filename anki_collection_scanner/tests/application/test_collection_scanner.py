
import pytest
from unittest.mock import Mock

from anki_collection_scanner.application.usecases.sync_collection import SyncCollectionUseCase
from anki_collection_scanner.application.application_exceptions import SyncError
from anki_collection_scanner.application.ports.anki_connect_port import AnkiConnectPort
from anki_collection_scanner.application.ports.snapshot_repository_port import SnapshotRepositoryPort
from anki_collection_scanner.domain.collection_snapshot import CollectionSnapshot


#TODO: add tests on failed pipeline during every step: fetch base, update base, enrich

def test_execute_sync_collection_success():
    repo = Mock(spec = SnapshotRepositoryPort)
    anki_client = Mock(spec = AnkiConnectPort)

    usecase = SyncCollectionUseCase(repo, anki_client)
    usecase.sync_user_collection = Mock()

    result = usecase.execute_sync_collection_use_case()

    assert result.is_ok()

def test_execute_sync_collection_use_case_sync_error_repo():

    repo = Mock(spec = SnapshotRepositoryPort)
    anki_client = Mock(spec = AnkiConnectPort)

    repo.save_snapshot.side_effect = Exception("Test exception raised")

    usecase = SyncCollectionUseCase(repo, anki_client)

    result = usecase.execute_sync_collection_use_case()
    error = result.unwrap_err()

    assert isinstance(error, SyncError)
    assert error.stage == "SYNC_COLLECTION"
    assert "Collection sync failed" in error.message

def test_execute_sync_collection_use_case_sync_error_anki_client():
    repo = Mock(spec = SnapshotRepositoryPort)
    anki_client = Mock(spec = AnkiConnectPort)

    anki_client.get_decks_and_ids.side_effect = Exception("Test exception raise")

    usecase = SyncCollectionUseCase(repo, anki_client)

    result = usecase.execute_sync_collection_use_case()
    error = result.unwrap_err()

    assert isinstance(error, SyncError)
    assert error.stage == "SYNC_COLLECTION"
    assert "Collection sync failed" in error.message

def test_add_model_field_names():
    anki_client = Mock(spec=AnkiConnectPort)
    repo = Mock(spec=SnapshotRepositoryPort)

    usecase = SyncCollectionUseCase(repo, anki_client)

    snapshot = CollectionSnapshot()

    snapshot.models = {
        1: Mock(model_name="Basic"),
        2: Mock(model_name="Cloze"),
    }

    anki_client.get_model_field_names.side_effect = [
        ["Front", "Back"],
        ["Text"]
    ]

    snapshot.update_model_fields = Mock()

    usecase.add_model_field_names(snapshot)

    assert anki_client.get_model_field_names.call_count == 2
    snapshot.update_model_fields.assert_any_call(1, ["Front", "Back"])
    snapshot.update_model_fields.assert_any_call(2, ["Text"])

def test_add_note_id_field_data():
    anki_client = Mock(spec = AnkiConnectPort)
    repo = Mock(spec = SnapshotRepositoryPort)

    usecase = SyncCollectionUseCase(repo, anki_client)

    snapshot = CollectionSnapshot()

    snapshot.notes = {
        10:Mock(),
        20:Mock()
        }
    
    notes_data = [
        {"id": 10, "fields": {"Front": "Hello"}},
        {"id": 20, "fields": {"Front": "World"}},
    ]

    anki_client.get_note_id_field_data.return_value = notes_data

    snapshot.update_note_data = Mock()

    usecase.add_note_id_field_data(snapshot)

    anki_client.get_note_id_field_data.assert_called_once_with([10, 20])
    assert snapshot.update_note_data.call_count == 2

def test_add_deck_note_count_and_hash():
    anki_client = Mock(spec = AnkiConnectPort)
    repo = Mock(spec = SnapshotRepositoryPort)

    usecase = SyncCollectionUseCase(repo, anki_client)

    snapshot = CollectionSnapshot()

    snapshot.decks = {
        12:Mock(deck_name = "Japansese"),
        21:Mock(deck_name = "Italki")
    }

    anki_client.get_deck_note_ids.side_effect = [[112, 221, 312], [212,55]]

    snapshot.compute_note_hash = Mock(side_effect = ["hash1", "hash2"])
    snapshot.update_deck_note_count_and_hash = Mock()

    usecase.add_deck_note_count_and_hash(snapshot)

    assert anki_client.get_deck_note_ids.call_count == 2
    snapshot.update_deck_note_count_and_hash.assert_any_call(12, 3, "hash1")
    snapshot.update_deck_note_count_and_hash.assert_any_call(21, 2, "hash2")


def test_sync_user_collection_happy_path():
    anki_client = Mock(spec = AnkiConnectPort)
    repo = Mock(spec = SnapshotRepositoryPort)
    snapshot = Mock()

    use_case = SyncCollectionUseCase(repo, anki_client)

    # Mock base data fetch
    anki_client.get_decks_and_ids.return_value = {"Default": 1}
    anki_client.get_models_and_ids.return_value = {"Basic": 2}
    anki_client.get_all_note_ids.return_value = [101, 102]

    # Mock enrichment internals (so we isolate orchestration only)
    use_case.add_model_field_names = Mock()
    use_case.add_note_id_field_data = Mock()
    use_case.add_deck_note_count_and_hash = Mock()

    use_case.sync_user_collection(snapshot)

    # Verify fetch stage
    anki_client.get_decks_and_ids.assert_called_once()
    anki_client.get_models_and_ids.assert_called_once()
    anki_client.get_all_note_ids.assert_called_once()

    # Verify snapshot base updates
    snapshot.update_decks.assert_called_once_with({"Default": 1})
    snapshot.update_models.assert_called_once_with({"Basic": 2})
    snapshot.update_notes.assert_called_once_with([101, 102])

    # Verify enrichment stage
    use_case.add_model_field_names.assert_called_once_with(snapshot)
    use_case.add_note_id_field_data.assert_called_once_with(snapshot)
    use_case.add_deck_note_count_and_hash.assert_called_once_with(snapshot)

    
def test_sync_stops_if_fetch_fails():
    anki_client = Mock(spec = AnkiConnectPort)
    repo = Mock(spec = SnapshotRepositoryPort)
    snapshot = Mock()

    use_case = SyncCollectionUseCase(repo, anki_client)

    anki_client.get_decks_and_ids.side_effect = RuntimeError("fetch failed")

    with pytest.raises(RuntimeError):
        use_case.sync_user_collection(snapshot)

    # Should stop immediately
    anki_client.get_models_and_ids.assert_not_called()
    anki_client.get_all_note_ids.assert_not_called()
    snapshot.update_decks.assert_not_called()


def test_sync_stops_if_update_fails():
    anki_client = Mock(spec = AnkiConnectPort)
    repo = Mock(spec = SnapshotRepositoryPort)
    snapshot = Mock()

    use_case = SyncCollectionUseCase(repo, anki_client)

    anki_client.get_decks_and_ids.return_value = {"Default": 1}
    anki_client.get_models_and_ids.return_value = {"Basic": 2}
    anki_client.get_all_note_ids.return_value = [101]

    snapshot.update_decks.side_effect = RuntimeError("update failed")

    with pytest.raises(RuntimeError):
        use_case.sync_user_collection(snapshot)

    # Enrichment should never run
    assert not hasattr(use_case, "add_model_field_names") or \
        not getattr(use_case.add_model_field_names, "called", False)
    

def test_sync_stops_if_enrichment_fails():
    anki_client = Mock(spec = AnkiConnectPort)
    repo = Mock(spec = SnapshotRepositoryPort)
    snapshot = Mock()

    use_case = SyncCollectionUseCase(repo, anki_client)

    anki_client.get_decks_and_ids.return_value = {"Default": 1}
    anki_client.get_models_and_ids.return_value = {"Basic": 2}
    anki_client.get_all_note_ids.return_value = [101]

    use_case.add_model_field_names = Mock(side_effect=RuntimeError("enrich failed"))
    use_case.add_note_id_field_data = Mock()
    use_case.add_deck_note_count_and_hash = Mock()

    with pytest.raises(RuntimeError):
        use_case.sync_user_collection(snapshot)

    # Later enrichment steps should not run
    use_case.add_note_id_field_data.assert_not_called()
    use_case.add_deck_note_count_and_hash.assert_not_called()