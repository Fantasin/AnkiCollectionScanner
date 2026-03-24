
import json
import logging

from pathlib import Path
from typing import Dict, Any

from anki_collection_scanner.domain.collection_snapshot.collection_snapshot import CollectionSnapshot
from anki_collection_scanner.domain.result import Result
from anki_collection_scanner.domain.domain_exceptions import SnapshotRepositoryError, SnapshotCorruptedError, SnapshotNotFoundError
from anki_collection_scanner.application.ports.snapshot_repository_port import SnapshotRepositoryPort

PATH_TO_ROOT = Path(__file__).resolve().parents[1]
PATH_TO_FILE = PATH_TO_ROOT / "infrastructure" / "snapshot.json"

logger = logging.getLogger(__name__)

class JSONSnapshotRepository(SnapshotRepositoryPort):
    def __init__(self, file_path = PATH_TO_FILE):
        self.file_path: Path = file_path

    def save_snapshot(self, snapshot: CollectionSnapshot) -> Result[None, SnapshotRepositoryError]:
        try: 
            data_to_save = snapshot.to_dict()
            with self.file_path.open("w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            logger.info("Snapshot saved to %s", self.file_path)
            return Result.ok(None)
        except OSError as e:
            logger.exception("I/O error while saving snapshot")
            return Result.err(SnapshotRepositoryError(f"I/O error: {e}"))
        except Exception as e:
            logger.exception("Unexpected error when saving snapshot")
            return Result.err(SnapshotRepositoryError(f"Unexpected error: {e}"))
    
    #TODO: move decision on creating a blank snapshot to orchestrator if a file doesn't exist
    def load_snapshot(self)-> Result[CollectionSnapshot, SnapshotRepositoryError]:

        if not self.file_path.is_file():
            logger.warning("Snapshot file not found: %s", self.file_path)
            return Result.err(SnapshotNotFoundError(self.file_path))
        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                json_data = json.load(f)

            snapshot = CollectionSnapshot.from_dict(json_data)
            logger.info("Snapshot loaded successfully")
            return Result.ok(snapshot)
        except json.JSONDecodeError:
            logger.error("Snapshot file contains invalid JSON: %s", self.file_path)
            return Result.err(SnapshotCorruptedError(self.file_path))
        except Exception as e:
            logger.exception("Unexpected error when loading snapshot")
            return Result.err(SnapshotRepositoryError(f"Unexpected error: {e}"))

            