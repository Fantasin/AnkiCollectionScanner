
import json

from pathlib import Path
from typing import Dict, Any

from ..domain.collection_snapshot import CollectionSnapshot

PATH_TO_ROOT = Path(__file__).resolve().parents[1]
PATH_TO_FILE = PATH_TO_ROOT / "infrastructure" / "snapshot.json"


class JSONSnapshotRepository:
    def __init__(self, file_path = PATH_TO_FILE):
        self.file_path: Path = file_path

    def save_snapshot(self, snapshot: CollectionSnapshot):
        try: 
            data_to_save = snapshot.to_dict()
            with self.file_path.open("w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            print("Snapshot's data was saved to a file successfully")
        except FileNotFoundError:
            raise RuntimeError (f"File doesn't exist on provided path: {self.file_path}")
        except json.JSONDecodeError:
            raise RuntimeError (f"JSON structure is corrupted on provided path: {self.file_path}")
        
    def load_snapshot(self) -> CollectionSnapshot:
        if self.file_path.is_file():
            with self.file_path.open("r", encoding="utf-8") as f:
                json_data = json.load(f)

            print("Passing data to a CollectionSnapshot object")
            return CollectionSnapshot().from_dict(json_data)
        else:
            print("File doesn't exist, creating blank structure for a collection snapshot")
            return CollectionSnapshot()
            