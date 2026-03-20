"""
File: application/usecases/scan_and_enrich_collection_usecase.py
What: Single use case that does the full pipeline (scan + enrich)
Why: Combines current scan_user_collection_first() + enrichment methods into one atomic operation
"""
import logging

from anki_collection_scanner.domain.collection_snapshot.collection_snapshot import CollectionSnapshot
from anki_collection_scanner.application.ports.anki_connect_port import AnkiConnectPort
from anki_collection_scanner.application.ports.snapshot_repository_port import SnapshotRepositoryPort
from anki_collection_scanner.domain.result import Result
from anki_collection_scanner.application.application_exceptions import SyncError

logger = logging.getLogger(__name__)

class SyncCollectionUseCase:
    def __init__(self, snapshot_repository: SnapshotRepositoryPort, anki_connect_client: AnkiConnectPort):
        if not isinstance(snapshot_repository, SnapshotRepositoryPort):
            raise TypeError("snapshot_repository must implement SnapshotRepositoryPort")
        self.snapshot_repository = snapshot_repository
        
        if not isinstance(anki_connect_client, AnkiConnectPort):
            raise TypeError("anki_connect_client must implement AnkiConnectPort")
        self.anki_connect_client = anki_connect_client

    def sync_user_collection(self, snapshot: CollectionSnapshot):

        decks_data, models_data, notes_ids = self.fetch_base_collection_data()
        logger.info("Got data for decks, models and notes")

        self.update_snapshot_base_collection_data(snapshot, decks_data, models_data, notes_ids)
        logger.info("Formed base structure, added decks, models and notes data")

        self.enrich_snapshot(snapshot)
        logger.info("Enriched data: added field models, note field data and deck note count and hash")

    def fetch_base_collection_data(self):
        decks = self.anki_connect_client.get_decks_and_ids()
        models = self.anki_connect_client.get_models_and_ids()
        notes = self.anki_connect_client.get_all_note_ids()

        return decks, models, notes

    def update_snapshot_base_collection_data(self, snapshot: CollectionSnapshot, decks, models, notes):
        snapshot.update_decks(decks)
        snapshot.update_models(models)
        snapshot.update_notes(notes)

    def enrich_snapshot(self, snapshot: CollectionSnapshot):
        self.add_model_field_names(snapshot)
        self.add_note_id_field_data(snapshot)
        self.add_deck_note_count_and_hash(snapshot)

    def add_model_field_names(self, snapshot: CollectionSnapshot):
        for id, model_data in snapshot.models.items():
            field_names = self.anki_connect_client.get_model_field_names(model_data.model_name)
            snapshot.update_model_fields(id, field_names)
    
    def add_note_id_field_data(self, snapshot: CollectionSnapshot):
        note_ids = list(snapshot.notes.keys())
        notes_data = self.anki_connect_client.get_note_id_field_data(note_ids)

        for note in notes_data:
            snapshot.update_note_data(note)

    def add_deck_note_count_and_hash(self, snapshot: CollectionSnapshot):
        for id, deck in snapshot.decks.items():
            note_ids = self.anki_connect_client.get_deck_note_ids(deck.deck_name)
            notes_hash = snapshot.compute_note_hash(note_ids)
            snapshot.update_deck_note_count_and_hash(id, len(note_ids), notes_hash)
    
    #pipeline execution
    def execute_sync_collection_use_case(self)-> Result[CollectionSnapshot, SyncError]:
        snapshot = CollectionSnapshot()

        try:
            self.sync_user_collection(snapshot)

            self.snapshot_repository.save_snapshot(snapshot)
            logger.info("Collection synced successfully")
            return Result.ok(snapshot)

        except Exception as e:
            logger.exception("Collection sync failed")
            return Result.err(SyncError(stage = "SYNC_COLLECTION", message = "Collection sync failed"))