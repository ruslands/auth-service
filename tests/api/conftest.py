import pytest
from app.main import app
from fastapi.testclient import TestClient

pytest.test_username = "test@test.com"
pytest.test_password = "rQwRzdLsVszPmoY"
pytest.expires_at = 0


@pytest.fixture(scope="session")
def test_client():
    with TestClient(app) as client:
        yield client
