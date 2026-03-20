
import re
import logging

from typing import Dict

from anki_collection_scanner.domain.collection_snapshot.collection_snapshot import CollectionSnapshot
from anki_collection_scanner.application.ports.audio_preparation_service_port import AudioPreparationServicePort
from anki_collection_scanner.domain.audio_service.audio_models import AudioFile, AudioTransferObject, CardRole

logger = logging.getLogger(__name__)

AUDIO_PRESENT_PATTERN = r"\[sound:[^\]]+\]"

#TODO: think about how to discover this at runtime
TARGET_FIELDS = {"Kartochki delaem dve srazu": {"Primary field": "Word", "Secondary field": "Furigana", "Audio field": "Furigana"}, 
                 "Basic-1ba65": {"Primary field":"Back", "Secondary field": "Front", "Audio field": "Back"}}


class AudioPreparationService(AudioPreparationServicePort):
    def __init__(self, snapshot: CollectionSnapshot):
        self.snapshot = snapshot

    def prepare_audio_transfer_objects(self, deck_note_ids: list[int]) -> Dict[int, AudioTransferObject]:
        missing_audio_notes = self.find_missing_audio(deck_note_ids)

        transfer_objects = {}

        card_reverse_card_notes = []
        singular_card_notes = []

        for note_id in missing_audio_notes:

            note_data = self.snapshot.notes[note_id]

            if len(note_data.cards) <= 1:
                singular_card_notes.append(note_id)
            else:
                card_reverse_card_notes.append(note_id)
            
        #TODO: add pair discovery process for all of the singular_card_notes here
        for note_id in card_reverse_card_notes:
            transfer_objects[note_id] = self.build_transfer_objects(note_id)

        logger.info("Resulting number of notes: %d", len(transfer_objects))
        return transfer_objects
    
    def enrich_transfer_objects_with_audio_files(self, transfer_objects: Dict[int, AudioTransferObject], audio_files: Dict[str, AudioFile])->Dict[int, AudioTransferObject]:
        enriched_objects = {}

        for note_id, object in transfer_objects.items():
            audio = audio_files.get(object.word)

            if not audio:
                logger.debug("No audio was found for word: %s", object.word)
                continue

            object.audio = audio
            enriched_objects[note_id] = object

        return enriched_objects
    
    def build_transfer_objects(self, note_id: int) -> AudioTransferObject:

        note_data = self.snapshot.notes[note_id]

        source_field, audio_field, word = self.resolve_target_fields(note_data)

        return AudioTransferObject(
            note_id = note_id,
            model_name = note_data.model,
            word = word,
            source_field = source_field,
            audio_field = audio_field,
            role = CardRole.SINGULAR #keep this as default, change for pairs during pair discovery
        )

    #TODO: for current model primary word is always present, for basic model this won't work. Revise later
    def resolve_target_fields(self, note_data):

        model_config = TARGET_FIELDS[note_data.model]

        primary_field = model_config["Primary field"]
        secondary_field = model_config["Secondary field"]
        audio_field = model_config["Audio field"]

        primary_word = note_data.note_fields[primary_field]["value"]

        source_field = primary_field if primary_word else secondary_field
        word = note_data.note_fields[source_field]["value"]

        return source_field, audio_field, word

    def find_missing_audio(self, deck_note_ids: list[int]) -> list[int]:
        missing_audio_notes = []
        for note_id in deck_note_ids:
            note_data = self.snapshot.notes[note_id]

            missing_audio_field = TARGET_FIELDS[note_data.model]["Audio field"]
            field_value = note_data.note_fields[missing_audio_field]["value"]

            match = re.search(AUDIO_PRESENT_PATTERN, field_value)

            if match:
                logger.debug("Found audio match: %s, skipping note", match[0])
                continue

            logger.debug("Audio is missing for note id: %d, model is and field data is %s, adding to missing audio notes", note_id, field_value)
            missing_audio_notes.append(note_id)

        logger.info("Resulting number of missing audio notes: %d", len(missing_audio_notes))
        return missing_audio_notes

    #pass return value to local_audio_repository
    def extract_word_for_audio_retrieval(self, transfer_objects: dict[int, AudioTransferObject]) -> list[str]:
        return [object.word for object in transfer_objects.values()]
    

    def discover_note_pairs(self, note_ids: list[int]):
        pass

test_data  = [
    {"Front": "～はちょっと", "Back": "not so good"},
    {"Front": "起こる", "Back": "おこる (to occur, to happen)"},
    {"Front": "訳", "Back": "わけ (reason, explanation)"},
    {"Front": "褒める", "Back": "ほめる (to praise, хвалить) [sound:95d527446aca5339a5b8e2b62080f6da.mp3]"},
    {"Front": "相手", "Back": "あいて (partner, opponent)"},
    {"Front": "相変わらず", "Back": "あいかわらず (as usual (about behaviour))"},
    {"Front": "まる", "Back": "circle, correct mark"},
    {"Front": "to praise, хвалить", "Back": "褒める（ほめる） [sound:95d527446aca5339a5b8e2b62080f6da.mp3]"},
    {"Front": "to occur, to happen", "Back": "起こる（おこる）"},
    {"Front": "sad", "Back": "悲しい　(かなしい)"},
    {"Front": "reason, explanation", "Back": "訳（わけ）"},
    {"Front": "not so good", "Back": "～はちょっと"},
    {"Front": "circle, correct mark", "Back": "まる"},
    {"Front": "author", "Back": "作家 (さっか)"},
    {"Front": "悲しい", "Back": "かなしい (sad)"},
    {"Front": "作家", "Back": "さっか (author)"},
    {"Front": "孤立", "Back": "こりつ (isolated)"},
    {"Front": "音声あり", "Back": "value without audio [sound:example.mp3]"},
    {"Front": "", "Back": "空 (empty)"},
]
