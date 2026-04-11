
import re
import logging
from bs4 import BeautifulSoup

from typing import Dict, Optional

from anki_collection_scanner.domain.collection_snapshot.collection_snapshot import CollectionSnapshot
from anki_collection_scanner.application.ports.audio_preparation_service_port import AudioPreparationServicePort
from anki_collection_scanner.application.field_config import FieldConfig
from anki_collection_scanner.domain.audio_service.audio_models import AudioFile, AudioTransferObject, CardRole


logger = logging.getLogger(__name__)

AUDIO_PRESENT_PATTERN = r"\[sound:[^\]]+\]"
JP_SYMBOLS_PATTERN = r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u3400-\u4DBF]"

#TODO: think about how to discover this at runtime


class AudioPreparationService(AudioPreparationServicePort):
    def __init__(self):
        pass

    #TODO: bugs to get rid of: pass only one transfer object, update pair card after, revise updating card to not delete existing content
    def prepare_audio_transfer_objects(self, deck_note_ids: list[int], snapshot: CollectionSnapshot, target_fields: Dict[str, FieldConfig]) -> Dict[int, AudioTransferObject]:
        missing_audio_notes = self.find_missing_audio(snapshot, target_fields, deck_note_ids)

        transfer_objects = {}

        card_reverse_card_notes = []
        singular_card_notes = []

        for note_id in missing_audio_notes:

            note_data = snapshot.notes[note_id]

            if len(note_data.cards) <= 1:
                card_reverse_card_notes.append(note_id)
            else:
                singular_card_notes.append(note_id)

        pairs = self.find_matches(snapshot, target_fields, card_reverse_card_notes)

        for word, note_id_pair in pairs.items():
            card_id, rev_card_id = note_id_pair
            transfer_objects[card_id] = self.build_transfer_objects(snapshot, target_fields, card_id, CardRole.PAIR_FORWARD, rev_card_id, word)
            transfer_objects[rev_card_id] = self.build_transfer_objects(snapshot, target_fields, rev_card_id, CardRole.PAIR_REVERSE, card_id, word)
                 
        for note_id in singular_card_notes:
            transfer_objects[note_id] = self.build_transfer_objects(snapshot, target_fields, note_id, CardRole.SINGULAR)

        logger.info("Resulting number of notes: %d", len(transfer_objects))
        return transfer_objects
    
    def enrich_transfer_objects_with_audio_files(self, transfer_objects: Dict[int, AudioTransferObject], audio_files: Dict[str, AudioFile])->Dict[int, AudioTransferObject]:
        enriched_objects = {}

        for note_id, object in transfer_objects.items():
            audio = audio_files.get(object.word)

            if not audio:
                continue

            object.audio = audio
            enriched_objects[note_id] = object
        
        logger.info("Number of enriched objects: %d", len(enriched_objects))

        return enriched_objects
    
    #TODO: adjust this function to handle object creation based on CardRole + add optional pair_id to parameters
    def build_transfer_objects(self, snapshot: CollectionSnapshot, target_fields: Dict[str, FieldConfig], note_id: int, role: CardRole, pair_id: Optional[int] = None, word: Optional[str] = None) -> AudioTransferObject:

        note_data = snapshot.notes[note_id]

        if role == CardRole.SINGULAR:
            source_field, audio_field, word = self.resolve_target_fields_singular_card(note_data, target_fields)
        elif role in (CardRole.PAIR_FORWARD, CardRole.PAIR_REVERSE):
            source_field, audio_field = self.resolve_target_fields_pair(note_data, role, target_fields)

            if word is None:
                word = note_data.note_fields[source_field]["value"]

        assert word is not None #workaround, TODO: fix

        return AudioTransferObject(
            note_id = note_id,
            model_name = note_data.model,
            word = word,
            source_field = source_field,
            audio_field = audio_field,
            role = role, #keep this as default, change for pairs during pair discovery
            pair_id = pair_id
        )

    #TODO: for current model primary word is always present, for basic model this won't work. Revise later
    def resolve_target_fields_singular_card(self, note_data, target_fields: Dict[str, FieldConfig]):

        model_config = target_fields[note_data.model]

        primary_field = model_config.primary_field
        secondary_field = model_config.secondary_field
        audio_field = model_config.audio_field

        primary_word = note_data.note_fields[primary_field]["value"]

        source_field = primary_field if primary_word else secondary_field
        word = note_data.note_fields[source_field]["value"]

        return source_field, audio_field, word
    
    def resolve_target_fields_pair(self, note_data, role: CardRole, target_fields: Dict[str, FieldConfig]):
        model_config = target_fields[note_data.model]

        if role == CardRole.PAIR_FORWARD:
            source_field = model_config.primary_field
        else:
            source_field = model_config.secondary_field
        audio_field = model_config.audio_field

        return source_field, audio_field

    def find_missing_audio(self, snapshot: CollectionSnapshot, target_fields: Dict[str, FieldConfig], deck_note_ids: list[int]) -> list[int]:
        missing_audio_notes = []
        for note_id in deck_note_ids:
            note_data = snapshot.notes[note_id]

            missing_audio_field = target_fields[note_data.model].audio_field
            field_value = note_data.note_fields[missing_audio_field]["value"]

            match = re.search(AUDIO_PRESENT_PATTERN, field_value)

            if match:
                continue

            missing_audio_notes.append(note_id)

        logger.info("Resulting number of missing audio notes: %d", len(missing_audio_notes))
        return missing_audio_notes

    #pass return value to local_audio_repository
    def extract_word_for_audio_retrieval(self, transfer_objects: dict[int, AudioTransferObject]) -> list[str]:
        return [obj.word for obj in transfer_objects.values() if obj.role is not CardRole.PAIR_REVERSE]
    
    def categorize_notes(self, data: dict[int, dict]):
        jp_text_pattern = re.compile(JP_SYMBOLS_PATTERN)

        cards = {}
        reverse_cards = {}

        for id, note in data.items():

            cleaned_front = clean_extra_text(note["Front"])
            cleaned_back = clean_extra_text(note["Back"])

            new_note = {"Front": cleaned_front, "Back": cleaned_back}

            if find_jp_text(cleaned_front, jp_text_pattern):
                cards[id] = new_note
            elif find_jp_text(cleaned_back, jp_text_pattern):
                reverse_cards[id] = new_note
            else:
                logger.warning("Could not classify note (no JP text found), skipping: %s", note)
        logger.debug("Categorized notes: %d forward cards, %d reverse cards", len(cards), len(reverse_cards))

        return cards, reverse_cards

    def find_matches(self, snapshot: CollectionSnapshot, target_fields: Dict[str, FieldConfig], note_ids: list[int]) -> dict[str, tuple[int, int]]:
        data = {}

        for note_id in note_ids:
            note_data = snapshot.notes[note_id]
            front = target_fields[note_data.model].primary_field
            back = target_fields[note_data.model].secondary_field

            data[note_id] = {
                "Front": note_data.note_fields[front]["value"],
                "Back": note_data.note_fields[back]["value"],
            }

        cards, reverse_cards = self.categorize_notes(data)

        used_reverse = set()
        pairs = {}

        for card_id, card in cards.items():
            jp_word = card["Front"]

            for rev_id, rev_card in reverse_cards.items():
                if rev_id in used_reverse:
                    continue
                if jp_word in rev_card["Back"]:
                    logger.debug("Pair matched: '%s' (card %d) <-> (rev_card %d)", jp_word, card_id, rev_id)
                    pairs[jp_word] = (card_id, rev_id)
                    used_reverse.add(rev_id)
                    break
        return pairs



#helper functions for stripping extra symbols when searching
def find_jp_text(dict_field: str, jp_pattern) -> bool:
    return bool(jp_pattern.search(dict_field))

def clean_extra_text(dict_field: str) -> str:
    soup = BeautifulSoup(dict_field, 'html.parser')
    text = soup.get_text(separator="", strip = True) #remove html tags
    text = text.replace('\u3000', '') #remove whitespace character
    return text

