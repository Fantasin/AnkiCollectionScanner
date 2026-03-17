"""
Conceptual orchestration flow:
1. Select deck and get noteIds
2. Load note field content for every noteId(using snapshot)
3. Analyze models used for notes, create a mapping: model-> audio field
3. Detect whether audio exists or not in note fields
4. Create a mapping for local audio: "normalized key" -> filepath ()
5. For each note: if audio file exists -> storeMediaFile and updateNoteFields(API methods) based on audio field for current model
6. 

Return something like : Result[AddAudioReport, AddAudioError]:
"""
from anki_collection_scanner.domain.collection_snapshot import CollectionSnapshot
from anki_collection_scanner.domain.result import Result

from anki_collection_scanner.application.ports.audio_preparation_service_port import AudioPreparationServicePort
from anki_collection_scanner.application.ports.local_audio_repository_port import LocalAudioRepositoryPort
from anki_collection_scanner.application.ports.anki_connect_port import AnkiConnectPort

class AddAudioToDeckUseCase:
    def __init__(
            self,
            audio_preparation_service: AudioPreparationServicePort,
            local_audio_repository: LocalAudioRepositoryPort,
            anki_connect_client: AnkiConnectPort):
        
        if not isinstance(audio_preparation_service, AudioPreparationServicePort):
            raise TypeError("audio_preparation_service must implement AudioPreparationServicePort")
        self.audio_preparation_service = audio_preparation_service

        if not isinstance(local_audio_repository, LocalAudioRepositoryPort):
            raise TypeError("local_audio_repository must implement LocalAudioRepositoryPort")
        self.local_audio_repository = local_audio_repository        

        if not isinstance(anki_connect_client, AnkiConnectPort):
            raise TypeError("anki_connect_client must implement AnkiConnectPort")
        self.anki_connect_client = anki_connect_client

    #TODO: make a proper orchestration with error handling
    #TODO: check for existence of file in a media folder before running update_note_fields
    #implement method for deck selection to avoid writing it manually 
    def add_audio_to_deck(self, deck_name: str):

        deck_note_ids = self.anki_connect_client.get_deck_note_ids(deck_name)

        transfer_objects = self.audio_preparation_service.prepare_audio_transfer_objects(deck_note_ids)
        words = self.audio_preparation_service.extract_word_for_audio_retrieval(transfer_objects)

        audio_files = self.local_audio_repository.get_audio_files(words)

        enriched_objects = self.audio_preparation_service.enrich_transfer_objects_with_audio_files(transfer_objects, audio_files)

        for note_id, transfer_object in enriched_objects.items():
            self.anki_connect_client.store_media_file(transfer_object.audio.filename, transfer_object.audio.base64_data)
            print(f"Note id: {note_id} with filename: {transfer_object.audio.filename} is uploaded to anki_media_folder")
            self.anki_connect_client.update_note_fields(note_id, {transfer_object.audio_field: f"[sound:{transfer_object.audio.filename}]"})
            print(f"Field: {transfer_object.audio_field} is updated with audio: [sound:{transfer_object.audio.filename}]")

        print(f"Audio addition is complete for deck: {deck_name}, number of notes: {len(enriched_objects)}")


        
        
        

    
