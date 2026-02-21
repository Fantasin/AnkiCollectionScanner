
from ..infrastructure.anki_connect import AnkiConnectClient
from ..infrastructure.snapshot_repository import JSONSnapshotRepository
from ..domain.collection_snapshot import CollectionSnapshot

#TODO: add logging, implement proper orcherstation for the whole pipeline

class SnapshotOrchestrator:
    def __init__(self, snapshot_repository, anki_connect_client):
        self.snapshot_repository: JSONSnapshotRepository = snapshot_repository
        self.anki_connect_client: AnkiConnectClient = anki_connect_client

    def scan_user_collection(self):
        pass
    def update_snapshot_artifact(self):
        pass

    def models_add_field_names(self, snapshot: CollectionSnapshot):

        for id, model in snapshot.models.items():
            payload = self.anki_connect_client.get_model_field_names(model.model_name)
            field_names = self.anki_connect_client._invoke_request(payload)

            snapshot.update_model_fields(id, field_names)

        return snapshot
    
    def deck_add_note_id_count_and_hash(self, snapshot: CollectionSnapshot):
        for id, deck in snapshot.decks.items():
            payload = self.anki_connect_client.get_deck_note_ids(deck.deck_name)
            deck_note_ids = self.anki_connect_client._invoke_request(payload)

            
            notes_hash = snapshot.compute_note_hash(deck_note_ids)
            snapshot.update_deck_note_count_and_hash(id, len(deck_note_ids), notes_hash)
    
    def notes_add_field_data(self, snapshot: CollectionSnapshot):
            
            snapshot_note_ids = list(snapshot.notes.keys())

            payload = self.anki_connect_client.get_note_id_field_data(snapshot_note_ids)
            notes_field_data = self.anki_connect_client._invoke_request(payload)

            for note_data in notes_field_data:
                snapshot.update_note_data(note_data)

            return snapshot
    

    def test_pipeline(self):
        snapshot = CollectionSnapshot()

        #base data for models and decks
        models_payload = self.anki_connect_client.get_models_and_ids()
        models_data = self.anki_connect_client._invoke_request(models_payload)
        decks_payload = self.anki_connect_client.get_decks_and_ids()
        decks_data = self.anki_connect_client._invoke_request(decks_payload)
        note_ids_payload = self.anki_connect_client.get_all_note_ids()
        note_ids_data = self.anki_connect_client._invoke_request(note_ids_payload)

        #add data to decks and models
        snapshot.update_decks(decks_data) 
        snapshot.update_models(models_data)
        snapshot.update_notes(note_ids_data)
        

        #add data for model field names, note data and note count
        self.models_add_field_names(snapshot)
        self.notes_add_field_data(snapshot)
        self.deck_add_note_id_count_and_hash(snapshot)

        #save to json
        self.snapshot_repository.save_snapshot(snapshot)
    
    def test_load(self):

        snapshot = self.snapshot_repository.load_snapshot()

        return snapshot
    
    def test_note_upd(self):
        snapshot = self.snapshot_repository.load_snapshot()

        models_payload = self.anki_connect_client.get_note_id_field_data([1769964960519])
        models_data = self.anki_connect_client._invoke_request(models_payload)

        

        snapshot.update_note_data(models_data[0])
        print(snapshot.notes[1769964960519])
    



orchestrator = SnapshotOrchestrator(JSONSnapshotRepository(), AnkiConnectClient())

#orchestrator.test_pipeline()
#snapshot = orchestrator.test_load()



