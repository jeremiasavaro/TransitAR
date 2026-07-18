import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(app_instance):
    """Provides a TestClient for the FastAPI app, using an in-memory SQLite database for testing."""
    with TestClient(app_instance) as c:
        yield c
