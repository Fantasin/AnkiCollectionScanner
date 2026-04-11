
from anki_collection_scanner.application.usecases.sync_collection import SyncCollectionUseCase
from anki_collection_scanner.application.usecases.add_audio_to_deck import AddAudioToDeckUseCase

from anki_collection_scanner.infrastructure.anki_connect import AnkiConnectClient
from anki_collection_scanner.infrastructure.snapshot_repository import JSONSnapshotRepository
from anki_collection_scanner.infrastructure.local_audio_repository import LocalAudioRepository
from anki_collection_scanner.infrastructure.media_cache_repository import MediaCacheRepository
from anki_collection_scanner.infrastructure.field_config_repository import FieldConfigRepository

from anki_collection_scanner.domain.audio_service.audio_preparation_service import AudioPreparationService

from anki_collection_scanner.infrastructure.logging_setup import build_logging

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_PROJECT_PATH = Path(__file__).resolve().parents[0]
BASE_AUDIO_SOURCES_PATH = BASE_PROJECT_PATH / "local_audio_static"
INDEX_FILE_PATH = BASE_PROJECT_PATH / "infrastructure" / "index.json"

#preparing app with dependency injection. Useful for GUI
def build_app():
    sync_collection_use_case = SyncCollectionUseCase(JSONSnapshotRepository(), AnkiConnectClient())

    audio_prep_service = AudioPreparationService() 
    local_audio_repo = LocalAudioRepository(INDEX_FILE_PATH)
    local_audio_repo.initialize()
    anki_client = AnkiConnectClient()
    media_cache_repo = MediaCacheRepository()
    field_config_repo = FieldConfigRepository()
    audio_use_case = AddAudioToDeckUseCase(audio_prep_service, local_audio_repo, anki_client, media_cache_repo)

    return {
        "sync_collection_use_case": sync_collection_use_case,
        "audio_use_case": audio_use_case,
        "snapshot_repository": sync_collection_use_case.snapshot_repository,
        "field_config_repository": field_config_repo
    }

def sync_on_startup(sync_collection_use_case: SyncCollectionUseCase):
    result = sync_collection_use_case.execute_sync_collection_use_case()

    if result.is_err():
        return {
            "success": False,
            "error": result.unwrap_err()
        }
    return {
        "success": True,
        "snapshot": result.unwrap()
    }

def sync_on_shutdown(sync_collection_use_case: SyncCollectionUseCase):
    try:
        result = sync_collection_use_case.execute_sync_collection_use_case()

        if result.is_err():
            logger.error("Shutdown sync failed: %s", result.unwrap_err())

    except Exception as e:
        logger.exception("Unexpected shutdown sync error: %s", e)

def sync_manual(sync_collection_use_case: SyncCollectionUseCase):
    result = sync_collection_use_case.execute_sync_collection_use_case()

    if result.is_err():
        return {
            "success": False,
            "error": result.unwrap_err()
        }
    return {
        "success": True,
        "snapshot": result.unwrap()
    }
    
def main():
    build_logging()
    app_dependencies = build_app()
    from anki_collection_scanner.gui.app import App
    App(app_dependencies).run()

if __name__ == "__main__":
    main()
