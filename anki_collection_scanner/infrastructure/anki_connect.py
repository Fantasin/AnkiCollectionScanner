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

from anki_collection_scanner.application.ports.anki_connect_port import AnkiConnectPort

logger = logging.getLogger(__name__)

ANKI_CONNECT_URL = "http://127.0.0.1:8765"

class AnkiConnectClient(AnkiConnectPort):
    def __init__(self):
        self.url: str = ANKI_CONNECT_URL
        self.version: int = 6

    #generic invoke method
    def _invoke_request(self, payload):
        
        r = requests.post(url = self.url, json = payload)
        r.raise_for_status()

        data = r.json()
        logger.debug("Received raw response data for action: %s", payload["action"])

        if data["error"] is not None:
            raise RuntimeError(f"API error occured: {data['error']}")
        
        return data["result"]
    

    def get_decks_and_ids(self) -> Dict[str, Any]:
        payload = {
            "action": "deckNamesAndIds",
            "version": self.version
        }
        return self._invoke_request(payload)

    def get_models_and_ids(self) -> Dict[str, Any]:
        payload = {
            "action": "modelNamesAndIds",
            "version": self.version
        }
        return self._invoke_request(payload)

    def get_model_field_names(self, model_name: str) -> list[str]:
        payload=  {
            "action": "modelFieldNames",
            "version": self.version,
            "params": {
                "modelName": model_name
            }
        }
        return self._invoke_request(payload)

    def get_deck_note_ids(self, deck_name: str) -> list[int]:
        payload = {
            "action": "findNotes",
            "version": self.version,
            "params": {
                "query": f'"deck:{deck_name}"' #double quote to avoid the bug where deck name contains a space
            }
        }
    
        return self._invoke_request(payload)
    
    def get_all_note_ids(self) -> list[int]:
        payload = {
            "action": "findNotes",
            "version": self.version,
            "params": {
                "query": ""
            }
        }
        return self._invoke_request(payload)
    
    def get_note_id_field_data(self, note_ids: list[int]) -> list[Dict[str, Any]]:
        payload = {            
            "action": "notesInfo",
            "version": self.version,
            "params": {
                "notes": note_ids
            }}
    
        return self._invoke_request(payload)
    
    def store_media_file(self, filename: str, base64_data: str):
        payload = {
            "action": "storeMediaFile",
            "version": self.version,
            "params": {
            "filename": filename,
            "data": base64_data,
            "deleteExisting": False
        }}
        return self._invoke_request(payload)
    
    def update_note_fields(self, note_id: int, fields: Dict[str, str]):
        payload = {
        "action": "updateNoteFields",
        "version": self.version,
        "params": {
            "note": {
                "id": note_id,
                "fields": fields
            }
        }}
        return self._invoke_request(payload)


"""client = AnkiConnectClient()
data = client.update_note_fields(1770757208180, {"Furigana": "test test"})"""






