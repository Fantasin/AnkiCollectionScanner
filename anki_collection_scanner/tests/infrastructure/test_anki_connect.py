import pytest
import requests

from unittest.mock import patch, MagicMock

from anki_collection_scanner.infrastructure.anki_connect import AnkiConnectClient

#invoke request tests
def test_invoke_request_success():
    client = AnkiConnectClient()

    fake_response = MagicMock()

    fake_response.raise_for_status.return_value = None

    fake_response.json.return_value = {
        "result": {"deck1": 123},
        "error": None
    }

    with patch("anki_collection_scanner.infrastructure.anki_connect.requests.post", return_value = fake_response) as mock_post:

        payload = {"action": "testPipeline", "version": 6}

        result = client._invoke_request(payload)

    
    assert result == {"deck1": 123}

    mock_post.assert_called_once_with(
        url = client.url,
        json = payload
    )

def test_invoke_request_http_error():
    client = AnkiConnectClient()

    fake_response = MagicMock()

    fake_response.raise_for_status.side_effect = requests.HTTPError("test error")

    with patch("anki_collection_scanner.infrastructure.anki_connect.requests.post", return_value = fake_response):

        payload = {"action": "testHTTPError", "version": 6}

        with pytest.raises(requests.HTTPError):
            client._invoke_request(payload)



def test_invoke_request_error():
    client = AnkiConnectClient()
    fake_response = MagicMock()

    fake_response.raise_for_status.return_value = None

    fake_response.json.return_value = {
        "result": None,
        "error" : "Test error occured"
    }

    with patch("anki_collection_scanner.infrastructure.anki_connect.requests.post", return_value = fake_response) as mock_post:
        payload = {"action": "testPipelineError", "version": 6}

        with pytest.raises(RuntimeError) as exc:
            client._invoke_request(payload)        

        assert "Test error occured" in str(exc.value) #TODO: research why is it needed exactly

    mock_post.assert_called_once_with(
        url = client.url,
        json = payload
    )


#payload construction tests
def test_get_decks_and_ids():
    client = AnkiConnectClient() #6 is a default version value

    payload = client.get_decks_and_ids()

    assert payload == {
            "action": "deckNamesAndIds",
            "version": 6
        }

def test_get_models_and_ids():
    client = AnkiConnectClient()

    payload = client.get_models_and_ids()

    assert payload == {
            "action": "modelNamesAndIds",
            "version": 6
        }

def test_get_model_field_names():
    client = AnkiConnectClient()

    payload = client.get_model_field_names("Anime sentence cards")

    assert payload == {
            "action": "modelFieldNames",
            "version": 6,
            "params": {
                "modelName": "Anime sentence cards"
            }
        }

def test_get_deck_note_ids():
    client = AnkiConnectClient()

    payload = client.get_deck_note_ids("Outdated Decks")

    assert payload == {
            "action": "findNotes",
            "version": 6,
            "params": {
                "query": '"deck:Outdated Decks"'
            }
        }
    
def test_get_all_note_ids():
    client = AnkiConnectClient()

    payload = client.get_all_note_ids()

    assert payload == {
            "action": "findNotes",
            "version": 6,
            "params": {
                "query": ""
            }
        }
    
def test_get_note_id_field_data():
    client = AnkiConnectClient()

    payload = client.get_note_id_field_data([1592036539578, 1592036547354])

    assert payload == {            
            "action": "notesInfo",
            "version": 6,
            "params": {
                "notes": [1592036539578, 1592036547354]
            }}