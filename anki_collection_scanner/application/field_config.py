
from dataclasses import dataclass

@dataclass
class FieldConfig:
    primary_field: str
    secondary_field: str
    audio_field: str