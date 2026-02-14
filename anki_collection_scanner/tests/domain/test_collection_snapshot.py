import pytest

from typing import cast
from anki_collection_scanner.domain.collection_snapshot import CollectionSnapshot, DeckSnapshot
from anki_collection_scanner.domain.collection_snapshot import ModelSnapshot, MetadataSnapshot, NoteSnapshot

'''
import all the necessary stuff for tests
write 5-10 basic tests for domain:
- valid/invalid/empty dataclasses creation
- CollectionSnapshot initialization
- rountrip test for to/from dict
- updating methods: 
    - updating models and decks
    - assert on updating proper fields

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
    pass

#deck tests
def test_deck_dataclass_creation():
    deck_snapshot = DeckSnapshot(1731424301417, "AnkiConnectAPI")

    assert deck_snapshot.deck_id == 1731424301417
    assert deck_snapshot.deck_name == "AnkiConnectAPI"
    assert deck_snapshot.note_ids is None

def test_deck_id_empty():
    with pytest.raises(ValueError):
        DeckSnapshot(cast(int, None), "AnkiConnectAPI")

def test_deck_id_none():
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
    pass


#data flow tests
def test_to_from_dict_flow():
    pass

#update tests
def test_update_models():
    pass

def test_update_model_fields():
    pass

def test_update_deck_note_ids():
    pass