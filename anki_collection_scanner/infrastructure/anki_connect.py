"""
Docstring for anki_collection_scanner.infrastructure.anki_connect
List of API methods used:
- modelNamesAndIds: get_models_and_ids
- deckNamesAndIds: get_decks_and_ids
- modelFieldNames: get_model_structure
- findNotes: get_deck_note_ids
"""

import requests
import logging

from typing import Dict, Any

logger = logging.getLogger(__name__)

ANKI_CONNECT_URL = "http://127.0.0.1:8765"

class AnkiConnectClient:
    def __init__(self):
        self.url: str = ANKI_CONNECT_URL
        self.version: int = 6

    def _invoke_request(self, payload):
        
        r = requests.post(url = self.url, json = payload)
        r.raise_for_status()

        data = r.json()
        logger.debug("Received raw response data", data)

        if not data["error"] == None:
            raise RuntimeError(f"API error occured: {data["error"]}")
        
        logger.debug("Response data is valid, returning...")
        return data["result"]
    

    def get_decks_and_ids(self) -> Dict[str, Any]:
        return {
            "action": "deckNamesAndIds",
            "version": self.version
        }

    def get_models_and_ids(self) -> Dict[str, Any]:
        return {
            "action": "modelNamesAndIds",
            "version": self.version
        }

    def get_model_field_names(self, model_name: str) -> Dict[str, Any]:
        return {
            "action": "modelFieldNames",
            "version": self.version,
            "params": {
                "modelName": model_name
            }
        }

    def get_deck_note_ids(self, deck_name: str) -> Dict[str, Any]:
        return {
            "action": "findNotes",
            "version": self.version,
            "params": {
                "query": f"deck:{deck_name}"
            }
        }
    
    def get_all_note_ids(self) -> Dict[str, Any]:
        return {
            "action": "findNotes",
            "version": self.version,
            "params": {
                "query": ""
            }
        }
    
    def get_note_id_field_data(self, note_ids: list[int]) -> Dict[str, Any]:
        return {            
            "action": "notesInfo",
            "version": self.version,
            "params": {
                "notes": note_ids
            }}




"""client = AnkiConnectClient()
payload = client.get_deck_note_ids("Monolingual::Immersion")
data = client._invoke_request(payload)
print(len(data))"""





