
from anki_collection_scanner.application.usecases.sync_collection import SyncCollectionUseCase
from anki_collection_scanner.infrastructure.anki_connect import AnkiConnectClient
from anki_collection_scanner.infrastructure.snapshot_repository import JSONSnapshotRepository
from anki_collection_scanner.infrastructure.logging_setup import build_logging


def main():
    build_logging()
    orchestrator = SyncCollectionUseCase(JSONSnapshotRepository(), AnkiConnectClient())
    orchestrator.execute_sync_collection_use_case()


if __name__ == "__main__":
    main()
