
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class AudioOperationSuccess:
    note_id: int
    word: str
    filename: str
    timestamp: datetime = field(default_factory = datetime.now)

@dataclass
class AudioOperationFailure:
    note_id: int
    word: str
    reason: str #no_audio_found, pattern_not_identified, api_error, unknown_error etc
    details: str #error message
    timestamp: datetime = field(default_factory = datetime.now)

@dataclass
class AudioOperationReport:
    deck_name: str
    successful: List[AudioOperationSuccess] = field(default_factory=list)
    skipped: List[AudioOperationFailure] = field(default_factory=list)
    failed: List[AudioOperationFailure] = field(default_factory=list)
    timestamp_start: datetime = field(default_factory = datetime.now)
    timestamp_end: Optional[datetime] = None

    @property
    def total_processed(self) -> int:
        """Total notes attempted"""
        return len(self.successful) + len(self.skipped) + len(self.failed)
    
    @property
    def success_rate(self)-> float:
        """Percentage of notes that got audio"""
        if self.total_processed == 0:
            return 0.0
        return (len(self.successful) / self.total_processed) * 100
    
    def summary(self)-> str:
        return(
            f"Deck: {self.deck_name}: "
            f"{len(self.successful)} successful, "
            f"{len(self.failed)} failed "
            f"{len(self.skipped)} skipped"
            f"({self.success_rate:.1f}% success rate)"
        )
    
@dataclass
class AddAudioError:
    message: str
    stage: str #field_discovery, file_lookup, upload, update...
    cause: Optional[Exception] = None

    def __str__(self):
        if self.cause:
            return f"[{self.stage}] {self.message}: {self.cause}"
        return f"[{self.stage}] {self.message}"