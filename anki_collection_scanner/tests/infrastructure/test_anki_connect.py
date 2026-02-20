import pytest

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
    pass

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


#Payload construction tests
    def test_get_decks_and_ids():
        pass

    def test_get_models_and_ids():
        pass

    def test_get_model_field_names():
        pass

    def test_get_deck_note_ids():
        pass
    
    def test_get_all_note_ids():
        pass
    
    def test_get_note_id_field_data():
        pass