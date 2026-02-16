
import logging

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime

logger = logging.getLogger(__name__)

#TODO: decide on a structure for note_id dict to include field contents
#TODO: add methods for updating note_id data
#TODO: add methods for updating note_ids list for every deck

@dataclass
class ModelSnapshot:
    model_id: int 
    model_name: str
    model_field_names: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.validate()

    def validate(self):
        if not self.model_id or self.model_id == "":
            raise ValueError(f"Model id: {self.model_id} is 'None' or empty")
        if self.model_name == None or self.model_name == "":
            raise ValueError(f"Model name: {self.model_name} is 'None' or empty")
        
        #TODO: add validation for field_names after implemeting the logic for it


@dataclass
class DeckSnapshot:
    deck_id: int
    deck_name: str
    note_ids: Optional[list[int]] = None

    def __post_init__(self):
        self.validate()

    def validate(self):
        if not self.deck_id or self.deck_id == "":
            raise ValueError(f"Model id: {self.deck_id} is 'None' or empty")
        if self.deck_name == None or self.deck_name == "":
            raise ValueError(f"Model name: {self.deck_name} is 'None' or empty")
        
        #TODO: add validation for note_ids after implemeting the logic for it

@dataclass
class NoteSnapshot:
    note_id: int
    model: str = ''
    cards: list[int] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    note_fields: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.validate()

    def validate(self):
        if not self.note_id or self.note_id == "":
            raise ValueError(f"Model id: {self.note_id} is 'None' or empty")
        
        #TODO: add validation for note_fields after implemeting the logic for it


#TODO: create to_dict() method to convert data for json (otherwise datetime type will create issues at json.dump())
#TODO: create validate method for metadata
#TODO: add hash/checksum field to metadata
@dataclass
class MetadataSnapshot:
    version: float = 1.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CollectionSnapshot:
    def __init__(self) -> None:
        self.models: Dict[int, ModelSnapshot] = {}
        self.decks: Dict[int, DeckSnapshot] = {}
        self.notes: Dict[int, NoteSnapshot] = {}
        self.metadata: MetadataSnapshot = MetadataSnapshot()

    #convertion to dict from whole dataclasses
    def to_dict(self) -> Dict[str, Any]:
        return{
            "meta": asdict(self.metadata),
            "models": {key: asdict(value) for key, value in self.models.items()},
            "decks": {key: asdict(value) for key, value in self.decks.items()},
            "notes": {key: asdict(value) for key, value in self.notes.items()}
        }
    #accepts json data and parses it back to snapshot data structure
    @classmethod
    def from_dict(cls, json_data: Dict[str, Any]):
        snapshot = cls()

        snapshot.models = {int(key): ModelSnapshot(**value) for key, value in json_data["models"].items()}
        snapshot.decks = {int(key): DeckSnapshot(**value) for key, value in json_data["decks"].items()}
        snapshot.notes = {int(key): NoteSnapshot(**value) for key, value in json_data["notes"].items()}
        snapshot.metadata = MetadataSnapshot(**json_data["meta"])

        return snapshot

    def update_models(self, models: Dict[str, int]):
        if not models:
            logger.warning("No models to ingest...")
            return
        
        #TODO: this implementation rewrites models completely. Fix to proper update
        self.models = {id: ModelSnapshot(model_id = id, model_name = model_name) for model_name, id in models.items()}


    def update_decks(self, decks: Dict[str, Any]):
        if not decks or decks == {}:
            logger.warning("No models to ingest...")
            return
        
        self.decks = {id: DeckSnapshot(deck_id = id, deck_name = deck_name) for deck_name, id in decks.items()}


    def update_notes(self, note_ids: list[int]):
        if not note_ids:
            logger.warning("No notes to ingest")
            return
        
        self.notes = {note_id: NoteSnapshot(note_id = note_id) for note_id in note_ids}

    
    def update_model_fields(self, model_id: int, fields_list: list[str]):

        if model_id not in self.models:
            raise KeyError(f"Model: {model_id} not found in models")

        if not fields_list:
            logger.warning("No fields are present for model: %s", model_id)
            return
        
        self.models[model_id].model_field_names = fields_list

    def update_deck_note_ids(self, deck_id: int, deck_note_ids: list[int]):

        if deck_id not in self.decks:
            raise KeyError(f"Deck id: {deck_id} is not in decks")

        if not deck_note_ids:
            logger.warning("No notes are present in the deck: %s", deck_id)
            return
        
        self.decks[deck_id].note_ids = deck_note_ids

    #consider making NoteFieldSnapshot a separate dataclass. Optionally break it down even more to retrieve reading, img code... 
    def update_note_data(self, note_data: Dict[str, Any]):

        if not note_data:
            logger.warning("Note data doesn't exist or is empty")
            return
        
        #update all the fields for a note except for noteId
        self.notes[note_data["noteId"]].model = note_data["modelName"]
        self.notes[note_data["noteId"]].cards = note_data["cards"]
        self.notes[note_data["noteId"]].tags = note_data["tags"]
        self.notes[note_data["noteId"]].note_fields = note_data["fields"]
        

"""snapshot = CollectionSnapshot()
snapshot.update_note_data(note_data)

print(snapshot.notes)"""