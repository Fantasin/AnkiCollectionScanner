import pytest


@pytest.fixture(scope="session")
def test_config():
    return {
        "anki_url": "http://localhost:8765",
        "test_mode": True,
    }
