
from anki_collection_scanner.application.collection_scanner import SnapshotOrchestrator
from anki_collection_scanner.infrastructure.anki_connect import AnkiConnectClient
from anki_collection_scanner.infrastructure.snapshot_repository import JSONSnapshotRepository
from anki_collection_scanner.infrastructure.logging_setup import build_logging


def main():
    build_logging()
    orchestrator = SnapshotOrchestrator(JSONSnapshotRepository(), AnkiConnectClient())
    orchestrator.orchestrated_pipeline()


if __name__ == "__main__":
    main()
