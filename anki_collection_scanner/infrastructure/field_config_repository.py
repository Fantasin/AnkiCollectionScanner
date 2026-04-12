
import json
import logging

from pathlib import Path
from typing import Dict

from dataclasses import asdict

from anki_collection_scanner.application.field_config import FieldConfig
from anki_collection_scanner.application.ports.field_config_repository_port import FieldConfigRepositoryPort
import sys

if getattr(sys, 'frozen', False):
    _FIELD_CONFIGS = Path(sys.executable).parent / "field_configs.json"
else:
    _FIELD_CONFIGS = Path(__file__).resolve().parents[0] / "field_configs.json"

logger = logging.getLogger(__name__)

class FieldConfigRepository(FieldConfigRepositoryPort):
    def __init__(self, file_path: Path = _FIELD_CONFIGS):
        self.file_path = file_path

    def save(self, config: Dict[str, FieldConfig]) -> None:
        serialized_config = {name: asdict(field_conf) for name, field_conf in config.items()}
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(serialized_config, f, ensure_ascii=False, indent=4)

    def load(self) -> Dict[str, FieldConfig]:
        if self.file_path.exists():
            with open(self.file_path, "r", encoding="utf-8") as f:
                raw_data =  json.load(f)
            return {name: FieldConfig(**values) for name, values in raw_data.items()}
        return {}


