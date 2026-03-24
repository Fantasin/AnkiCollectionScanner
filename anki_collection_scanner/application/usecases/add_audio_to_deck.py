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

import logging

from anki_collection_scanner.domain.collection_snapshot.collection_snapshot import CollectionSnapshot
from anki_collection_scanner.domain.result import Result
from datetime import datetime

from anki_collection_scanner.domain.audio_service.audio_service_report import(
    AudioOperationReport,
    AudioOperationSuccess,
    AudioOperationFailure,
    AddAudioError
)

from anki_collection_scanner.application.ports.audio_preparation_service_port import AudioPreparationServicePort
from anki_collection_scanner.application.ports.local_audio_repository_port import LocalAudioRepositoryPort
from anki_collection_scanner.application.ports.anki_connect_port import AnkiConnectPort

logger = logging.getLogger(__name__)

#TODO: consider adding snapshot_repository to constructor to save changes to snapshot
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
    def add_audio_to_deck(self, deck_name: str, snapshot: CollectionSnapshot)-> Result[AudioOperationReport, AddAudioError]:

        report = AudioOperationReport(deck_name)

        try:
            #get deck note_ids
            deck_note_ids = self.anki_connect_client.get_deck_note_ids(deck_name)

            if not deck_note_ids:
                return Result.err(AddAudioError(
                    message=f"Deck {deck_name} is empty",
                    stage = "deck_notes_lookup"
                ))

            #filter notes, create transfer objects and retrieve audio
            transfer_objects = self.audio_preparation_service.prepare_audio_transfer_objects(deck_note_ids)
            words = self.audio_preparation_service.extract_word_for_audio_retrieval(transfer_objects)
            audio_files = self.local_audio_repository.get_audio_files(words)
            enriched_objects = self.audio_preparation_service.enrich_transfer_objects_with_audio_files(transfer_objects, audio_files)

            for word in words:
                if word not in audio_files:
                    affected_notes = [note_id for note_id, obj in transfer_objects.items() if obj.word == word]

                    for note_id in affected_notes:
                        report.skipped.append(
                            AudioOperationFailure(
                                note_id = note_id,
                                word = word,
                                reason = "no_audio_file",
                                details="No audio file for word was found in local audio repository"
                            )
                        )

            #upload files to anki media folder and update
            logger.info("Starting upload to Anki media folder and updating note fields...")
            for note_id, transfer_object in enriched_objects.items():
                if transfer_object.audio is None:
                    continue
                try:

                    #TODO: create a method get_stored_media_files and validate their existence
                    #uploading to anki media folder
                    self.anki_connect_client.store_media_file(transfer_object.audio.filename, transfer_object.audio.base64_data)

                    #updating notes
                    note_data = snapshot.notes[note_id]
                    audio_field = transfer_object.audio_field

                    current_value = note_data.note_fields[audio_field]["value"]
                    audio_tag = f"[sound:{transfer_object.audio.filename}]"

                    if not current_value:
                        updated_value = audio_tag
                    else:
                        updated_value = f"{current_value} {audio_tag}"

                    self.anki_connect_client.update_note_fields(note_id, {audio_field: updated_value})
                    logger.debug("Note %d: '%s' uploaded and field '%s' updated", note_id, transfer_object.audio.filename, audio_field)

                    report.successful.append(
                        AudioOperationSuccess(
                            note_id = note_id,
                            word = transfer_object.word,
                            filename = transfer_object.audio.filename
                        )
                    )
                except Exception as e:
                    logger.exception("Failed to process note %d", note_id)
                    report.failed.append(
                        AudioOperationFailure(
                            note_id = note_id,
                            word = transfer_object.word,
                            reason = "upload_or_update_error",
                            details = str(e)
                        )
                    )
            report.timestamp_end = datetime.now()
            logger.info("Audio addition is complete for deck: %s, number of notes: %d", deck_name, len(enriched_objects))
            return Result.ok(report)
        except Exception as e:
            logger.exception("Audio operation failed")
            return Result.err(
                AddAudioError(
                    message = str(e),
                    stage="orchestration",
                    cause = e
                )
            )


        
        
        

    
