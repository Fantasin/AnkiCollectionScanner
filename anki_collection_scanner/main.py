
from anki_collection_scanner.application.usecases.sync_collection import SyncCollectionUseCase
from anki_collection_scanner.application.usecases.add_audio_to_deck import AddAudioToDeckUseCase

from anki_collection_scanner.infrastructure.anki_connect import AnkiConnectClient
from anki_collection_scanner.infrastructure.snapshot_repository import JSONSnapshotRepository
from anki_collection_scanner.infrastructure.local_audio_repository import LocalAudioRepository

from anki_collection_scanner.domain.audio_service.audio_preparation_service import AudioPreparationService

from anki_collection_scanner.infrastructure.logging_setup import build_logging

from pathlib import Path

BASE_PROJECT_PATH = Path(__file__).resolve().parents[0]
BASE_AUDIO_SOURCES_PATH = BASE_PROJECT_PATH / "local_audio_static"
INDEX_FILE_PATH = BASE_PROJECT_PATH / "infrastructure" / "index.json"

def main():
    build_logging()
    orchestrator = SyncCollectionUseCase(JSONSnapshotRepository(), AnkiConnectClient())
    orchestrator.execute_sync_collection_use_case()

    repo = JSONSnapshotRepository()
    snapshot = repo.load_snapshot().unwrap()
    audio_prep_service = AudioPreparationService(snapshot)
    local_audio_repo = LocalAudioRepository(INDEX_FILE_PATH)
    local_audio_repo.initialize()
    anki_client = AnkiConnectClient()
    audio_use_case = AddAudioToDeckUseCase(audio_prep_service, local_audio_repo, anki_client)

    result = audio_use_case.add_audio_to_deck("Japanese", snapshot)
    
    if result.is_err():
        print(result.unwrap_err())
    print(result.unwrap().summary())
    



if __name__ == "__main__":
    main()
