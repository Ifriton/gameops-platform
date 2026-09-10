import os

import pytest
from fastapi.testclient import TestClient

# app.main exposes the ASGI application at import time and therefore fails closed
# unless its required key is configured.
os.environ.setdefault("GAMEOPS_API_KEY", "test-import-key")

from app.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402

API_KEY = "test-api-key"


@pytest.fixture
def client(tmp_path):
    settings = Settings(
        app_env="test",
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        gameops_api_key=API_KEY,
        log_level="WARNING",
    )
    with TestClient(create_app(settings)) as test_client:
        yield test_client


@pytest.fixture
def auth_headers():
    return {"X-API-Key": API_KEY}


@pytest.fixture
def server_payload():
    return {"name": "rp-server-01", "region": "us-east", "max_players": 128}
