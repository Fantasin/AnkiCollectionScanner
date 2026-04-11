
from dataclasses import dataclass
from typing import Optional
from enum import Enum


@dataclass
class AudioFile:
    filename: str
    base64_data: str

class CardRole(Enum):
    SINGULAR = "singular"
    PAIR_FORWARD = "forward"
    PAIR_REVERSE = "reverse"
 
@dataclass
class AudioTransferObject:
    #parameters at the stage of discovery
    note_id: int
    model_name: str
    word: str 
    source_field: str
    audio_field: str

    role: CardRole
    pair_id: Optional[int] = None
    
    #enrichment after getting audio data
    audio: Optional[AudioFile] = None


