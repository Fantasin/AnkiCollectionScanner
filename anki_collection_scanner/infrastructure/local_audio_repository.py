"""
Handles local scanning, finds audio file and scans it, transforms it to base64

creates mapping for word-> filename, doesn't know anything about anki (save mapping to index.json and rely upon it on reruns)
Suggested structure: word: {"nhk":"path1343.ddd", "forvo": "path313,dsd"...}

"""
import json
import os 
import base64

from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict
from typing import Optional, List

from anki_collection_scanner.application.ports.local_audio_repository_port import LocalAudioRepositoryPort
from anki_collection_scanner.domain.audio_models import AudioFile

BASE_PROJECT_PATH = Path(__file__).resolve().parents[1]
BASE_AUDIO_SOURCES_PATH = BASE_PROJECT_PATH / "local_audio_static"
#INDEX_FILE_PATH = BASE_PROJECT_PATH / "infrastructure" / "index.json"

JPOD_INDEX_FILE_PATH = BASE_AUDIO_SOURCES_PATH / "jpod_files" / "index.json"
JPOD_AUDIO_FILE_PATH = BASE_AUDIO_SOURCES_PATH / "jpod_files" / "audio"

@dataclass(frozen=True)
class AudioSourceConfig:
    name: str
    index_path: Optional[Path]
    audio_path: Path
    search_type: str
    priority: int

SOURCES: list[AudioSourceConfig] = [
    AudioSourceConfig(
        name="shinmeikai",
        search_type="json",
        index_path=Path("shinmeikai8_files/index.json"),
        audio_path=Path("shinmeikai8_files/media"),
        priority=1,
    ),
    AudioSourceConfig(
        name="nhk",
        search_type="json",
        index_path=Path("nhk16_files/index.json"),
        audio_path=Path("nhk16_files/audio"),
        priority=2,
    ),
    AudioSourceConfig(
        name="jpod",
        search_type="json",
        index_path=Path("jpod_files/index.json"),
        audio_path=Path("jpod_files/audio"),
        priority=3,
    ),
    AudioSourceConfig(
        name="forvo",
        search_type="filenames",
        index_path=None,
        audio_path=Path("forvo_files"),
        priority=4,
    ),
]

SOURCE_PRIORITY = {s.name: s.priority for s in SOURCES}

@dataclass
class AudioCandidate:
    word: str
    source: str
    path: Path

AudioIndex = dict[str, list[AudioCandidate]]

class LocalAudioRepository(LocalAudioRepositoryPort):
    def __init__(self, index_path: Path):
        self.index_path = index_path
        self.index = {}

    def initialize(self):
        if not self.index_path.exists():
            print("creating index.json")
            create_index_json(SOURCES, self.index_path)

        self.index = load_index_from_json(self.index_path)
        print("loaded index.json")

    def find_audio_file_candidates(self, word: str) -> List[AudioCandidate]:
        return self.index.get(word, [])

    def select_best_candidate(self, candidates: List[AudioCandidate]) -> AudioCandidate | None:
        if not candidates:
            return None
    
        return min(candidates, key = lambda c: SOURCE_PRIORITY[c.source])

    def load_audio_file(self, candidate: AudioCandidate) -> bytes:
        FULL_FILE_PATH = BASE_AUDIO_SOURCES_PATH / candidate.path

        with open(FULL_FILE_PATH, "rb") as f:
            return f.read()

    def encode_audio_file(self, audio_bytes: bytes) -> str:
        return base64.b64encode(audio_bytes).decode("utf-8")

    def build_audio_file(self, candidate: AudioCandidate)-> AudioFile:
        
        audio_bytes = self.load_audio_file(candidate)
        b64_encoded_audio = self.encode_audio_file(audio_bytes)

        filename = f"{candidate.word}_{candidate.source}.mp3"

        audio_file = AudioFile(
            filename = filename,
            base64_data = b64_encoded_audio
        )

        return audio_file

    #MAIN METHOD TO BE EXPOSED IN ORCHESTRATION
    def get_audio_files(self, words: list[str]) -> dict[str, AudioFile]:
        audio_files = {}
        for word in words:
            candidates = self.find_audio_file_candidates(word)
            best_candidate = self.select_best_candidate(candidates)

            if not best_candidate:
                print(f"Candidate was not found for word: {word}, skipping to next word...")
                continue

            audio_file = self.build_audio_file(best_candidate)
            audio_files[word] = audio_file
        
        return audio_files

def create_index_json(sources: list[AudioSourceConfig], index_file_path: Path):
    index = defaultdict(list)

    for source in sources:
        scanner = SCANNERS.get(source.name)

        if not scanner:
            print(f"Scanner doesn't exist for source: {source.name}, skipping...")
            continue

        index_path = source.index_path
        audio_path = source.audio_path

        if source.search_type == "json":
            scanner(index_path, audio_path, source.name, index)
        else:
            scanner(audio_path, source.name, index)

        print(f"Scan for source: {source.name} is complete")

    data_to_json = index_to_json(index)
    save_index_to_json(data_to_json, index_file_path)
    print("Saved index to json")

def index_to_json(index: AudioIndex):

    result = {}

    for word, candidates in index.items():

        result[word] = []

        for c in candidates:

            data = asdict(c)
            data["path"] = str(c.path)

            result[word].append(data)

    return result

def read_json_file(file_path):
    if not file_path.is_file():
        raise ValueError(f"{file_path} is not a valid file")

    with open(file_path, "r", encoding = "utf-8") as f:
        json_data = json.load(f)
    return json_data

def save_index_to_json(index, index_file_path: Path):
    with open(index_file_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print("saved to file")

#convert json data back to datastructure
def load_index_from_json(index_path):
    
    json_data = read_json_file(index_path)
    
    index = defaultdict(list)

    for word, audio_candidates in json_data.items():
        for candidate in audio_candidates:
            candidate = AudioCandidate(
                word = word,
                source = candidate["source"],
                path = Path(candidate["path"])
            )
            index[word].append(candidate)

    return index
#forvo
def scan_source_filenames(audio_path, source, index):
    BASE_AUDIO_PATH = BASE_AUDIO_SOURCES_PATH / audio_path

    for root, dirs, files in os.walk(BASE_AUDIO_PATH):
        for file in files:

            if not file.endswith(".mp3"):
                continue

            full_path = Path(root, file)
            relative_path = full_path.relative_to(BASE_AUDIO_SOURCES_PATH)

            word = Path(file).stem

            candidate = AudioCandidate(
                word = word,
                source = source,
                path = relative_path
            )
            index[word].append(candidate)

#jpod and shinmeikai
def scan_source_headwords(index_path, audio_path, source, index):
    
    FULL_INDEX_PATH = BASE_AUDIO_SOURCES_PATH / index_path
    file_data = read_json_file(FULL_INDEX_PATH)

    for word, files in file_data["headwords"].items():
        for file in files:
            candidate = AudioCandidate(
                word,
                source,
                path = Path(audio_path) / file
            )
            index[word].append(candidate)


#nhk
def scan_source_nhk(index_path, audio_path, source, index):
    FULL_INDEX_PATH = BASE_AUDIO_SOURCES_PATH / index_path
    file_data = read_json_file(FULL_INDEX_PATH)

    for entry in file_data:
        kanji_list = entry.get("kanji", [])

        for accent in entry.get("accents", []):

            audio_file = accent.get("soundFile")

            if not audio_file:
                continue

            for word in kanji_list:
                candidate = AudioCandidate(
                    word,
                    source,
                    path = Path(audio_path) / Path(audio_file)
                )

                index[word].append(candidate)

#constant to figure out what function for each source to call during index buildup
SCANNERS = {
    "shinmeikai": scan_source_headwords,
    "nhk": scan_source_nhk,
    "jpod": scan_source_headwords,
    "forvo": scan_source_filenames
}




    

