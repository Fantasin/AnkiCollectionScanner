import pytest
import requests

from unittest.mock import patch, MagicMock, Mock

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

    client._invoke_request = Mock(return_value = {"Default": 1})

    result = client.get_decks_and_ids()

    client._invoke_request.assert_called_once_with({
        "action": "deckNamesAndIds",
        "version": 6
    })

    assert result == {"Default": 1}

def test_get_models_and_ids():
    client = AnkiConnectClient()

    client._invoke_request = Mock(return_value = {"Japanese12": 13})

    result = client.get_models_and_ids()

    client._invoke_request.assert_called_once_with({
            "action": "modelNamesAndIds",
            "version": 6
        }
    )
    assert result == {"Japanese12": 13}

def test_get_model_field_names():
    client = AnkiConnectClient()

    client._invoke_request = Mock(return_value = ["Front", "Back", "Audio"])

    result = client.get_model_field_names("Anime sentence cards")

    client._invoke_request.assert_called_once_with(
        {
            "action": "modelFieldNames",
            "version": 6,
            "params": {
                "modelName": "Anime sentence cards"
            }  
        }
    )
    assert result == ["Front", "Back", "Audio"]


def test_get_deck_note_ids():
    client = AnkiConnectClient()

    client._invoke_request = Mock(return_value = [282, 434, 313])

    result = client.get_deck_note_ids("Outdated Decks")

    client._invoke_request.assert_called_once_with(
        {
            "action": "findNotes",
            "version": 6,
            "params": {
                "query": '"deck:Outdated Decks"'
            }
        }
    )
    assert result == [282, 434, 313]
    
    
    
def test_get_all_note_ids():
    client = AnkiConnectClient()

    client._invoke_request = Mock(return_value = [282, 434, 313])

    result = client.get_all_note_ids()
    client._invoke_request.assert_called_once_with(
        {
            "action": "findNotes",
            "version": 6,
            "params": {
                "query": ""
            }
        }
    )
    assert result == [282, 434, 313]

    
def test_get_note_id_field_data():
    client = AnkiConnectClient()

    client._invoke_request = Mock(return_value = [
        {
            "noteId": 1,
            "modelName": "Basic",
            "fields": {
                "Front": {"value": "Q1", "order": 0},
                "Back": {"value": "A1", "order": 1}
            },
            "tags": [],
            "cards": []
        }
    ])

    result = client.get_note_id_field_data([1483959289817])

    client._invoke_request.assert_called_once_with({            
            "action": "notesInfo",
            "version": 6,
            "params": {
                "notes": [1483959289817]
            }})
    assert result == [
        {
            "noteId": 1,
            "modelName": "Basic",
            "fields": {
                "Front": {"value": "Q1", "order": 0},
                "Back": {"value": "A1", "order": 1}
            },
            "tags": [],
            "cards": []
        }
    ]