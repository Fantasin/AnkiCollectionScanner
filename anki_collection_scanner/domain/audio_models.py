
from dataclasses import dataclass
from typing import Optional


@dataclass
class AudioFile:
    filename: str
    base64_data: str

@dataclass
class AudioTransferObject:
    #parameters at the stage of discovery
    note_id: int
    model_name: str
    word: str 

    source_field: str
    audio_field: str
    
    #enrichment after getting audio data
    audio: Optional[AudioFile] = None


