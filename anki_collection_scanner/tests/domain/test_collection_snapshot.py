import pytest

from typing import cast
from anki_collection_scanner.domain.collection_snapshot import CollectionSnapshot, DeckSnapshot
from anki_collection_scanner.domain.collection_snapshot import ModelSnapshot, MetadataSnapshot, NoteSnapshot

'''
TODO: critically think about what test data might crash the program, design tests accordingly
TODO: use parametrized tests if I need to run same test logic with different input
TODO: use fixtures when I need a reusable setup
TODO: use pytest.raises(ValueError): when failing(explicit fail)
'''

#snapshot tests
def test_empty_snapshot_creation():
    snapshot = CollectionSnapshot()

    assert snapshot.decks == {}
    assert snapshot.models == {}
    assert snapshot.notes == {}
    assert isinstance(snapshot.metadata, MetadataSnapshot)
    assert snapshot.metadata.version == 1.0
    assert snapshot.metadata.updated_at is None
    assert snapshot.metadata.created_at is None

#model tests
def test_model_dataclass_creation():
    model_snapshot = ModelSnapshot(1353588026860, "Geography")

    assert model_snapshot.model_id == 1353588026860
    assert model_snapshot.model_name == "Geography"
    assert model_snapshot.model_field_names == []

def test_model_id_none():
    with pytest.raises(ValueError):
        ModelSnapshot(cast(int, None), "Geography")

def test_model_id_empty():
    with pytest.raises(ValueError):
        ModelSnapshot(cast(int, ""), "Geography")

def test_model_name_none():
    with pytest.raises(ValueError):
        ModelSnapshot(1353588026860, cast(str, None))

def test_model_name_empty():
    with pytest.raises(ValueError):
        ModelSnapshot(1353588026860, "")

#deck tests
def test_deck_dataclass_creation():
    deck_snapshot = DeckSnapshot(1731424301417, "AnkiConnectAPI")

    assert deck_snapshot.deck_id == 1731424301417
    assert deck_snapshot.deck_name == "AnkiConnectAPI"
    assert deck_snapshot.note_count is None


def test_deck_id_none():
    with pytest.raises(ValueError):
        DeckSnapshot(cast(int, None), "AnkiConnectAPI")

def test_deck_id_empty():
    with pytest.raises(ValueError):
        DeckSnapshot(cast(int, ""), "AnkiConnectAPI")

def test_deck_name_none():
    with pytest.raises(ValueError):
        DeckSnapshot(1731424301417, cast(str, None))

def test_deck_name_empty():
    with pytest.raises(ValueError):
        DeckSnapshot(1731424301417, "")

#note tests
def test_note_dataclass_creation():
    note_snapshot = NoteSnapshot(1645514410825)

    assert note_snapshot.note_id == 1645514410825
    assert note_snapshot.model == ""
    assert note_snapshot.cards == []
    assert note_snapshot.tags == []
    assert note_snapshot.note_fields == {}

def test_note_id_none():
    with pytest.raises(ValueError):
        NoteSnapshot(cast(int, None))

def test_note_id_empty():
    with pytest.raises(ValueError):
        NoteSnapshot(cast(int, ""))

#data flow tests
def test_to_from_dict_flow():
    snapshot = CollectionSnapshot()

        # --- Add model ---
    snapshot.models[1] = ModelSnapshot(
        model_id=1,
        model_name="Basic",
        model_field_names=["Front", "Back"]
    )

    # --- Add deck ---
    snapshot.decks[10] = DeckSnapshot(
        deck_id=10,
        deck_name="Default",
        note_count=100
    )

    # --- Add note ---
    snapshot.notes[100] = NoteSnapshot(
        note_id=100,
        note_fields={"Front": "Hello", "Back": "World"}
    )

    json_data = snapshot.to_dict()

    assert isinstance(json_data, dict)
    assert {"meta", "models", "decks", "notes"} <= json_data.keys()
    
    snapshot2 = CollectionSnapshot.from_dict(json_data)

    assert isinstance(snapshot2, CollectionSnapshot)
    assert snapshot2.to_dict() == json_data

    assert 1 in snapshot2.models
    assert snapshot2.models[1].model_name == "Basic"

    assert 10 in snapshot2.decks
    assert snapshot2.decks[10].note_count == 100

    assert 100 in snapshot2.notes
    fields = snapshot2.notes[100].note_fields
    assert fields["Front"] == "Hello"
    assert fields["Back"] == "World"
    
def test_empty_roundtrip_flow():
    snapshot = CollectionSnapshot()
    json_data = snapshot.to_dict()
    assert CollectionSnapshot.from_dict(json_data).to_dict() == json_data

#update tests
def test_update_models():
    snapshot = CollectionSnapshot()
    models = {'12434324': 1692619332364, 'Anime sentence cards': 1693824375768, 'AnkiConnectAPI_test': 1731513977329}

    snapshot.update_models(models)

    for name, model_id in models.items():
        assert model_id in snapshot.models
        
        model = snapshot.models[model_id]
        assert model.model_id == model_id
        assert model.model_name == name

    assert len(snapshot.models) == len(models)

def test_update_models_empty():
    snapshot = CollectionSnapshot()
    snapshot.update_models({})

    assert snapshot.models == {}

def test_update_model_fields():
    snapshot = CollectionSnapshot()
    models = {'12434324': 1692619332364}
    model_fields = ['Sentence', 'Screenshot', 'Furigana', 'Pitch Accent', 'New words']

    snapshot.update_models(models)
    snapshot.update_model_fields(1692619332364, model_fields)

    assert snapshot.models[1692619332364].model_field_names == model_fields
    
def test_update_model_fields_empty():
    snapshot = CollectionSnapshot()

    with pytest.raises(KeyError):
        snapshot.update_model_fields(1692619332364, ["Front", "Back"])


def test_update_deck_note_count_and_hash():
    snapshot = CollectionSnapshot()

    decks = {'Monolingual': 1744028003906}
    note_ids = 200

    snapshot.update_decks(decks)
    snapshot.update_deck_note_count_and_hash(1744028003906, 200, "hash")

    assert snapshot.decks[1744028003906].note_count == note_ids

def test_update_deck_note_ids_empty():
    snapshot = CollectionSnapshot()

    with pytest.raises(KeyError):
        snapshot.update_deck_note_count_and_hash(1744027989515, 200, "hash")


def test_update_notes():
    snapshot = CollectionSnapshot()
    note_ids = [1744028123348, 1744028196910, 1744028410569]

    snapshot.update_notes(note_ids)

    for note_id in note_ids:
        assert note_id in snapshot.notes
        
        note = snapshot.notes[note_id]
        assert note.note_id == note_id

    assert len(snapshot.notes) == len(note_ids)

def test_update_notes_empty():
    snapshot = CollectionSnapshot()
    snapshot.update_notes([])

    assert snapshot.notes == {}

#TODO: add  updating note data tests, metadata tests