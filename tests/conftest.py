import os
from typing import Generator
import uuid

import pytest
from dotenv import load_dotenv
from tests.utils.api_client import APIClient

load_dotenv()

##############################################
# API FIXTURES
##############################################

@pytest.fixture(scope="session")
def api_base_url() -> str:
    return os.getenv("API_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def api_client(api_base_url) -> Generator[APIClient, None, None]:
    api_client = APIClient(api_base_url)
    yield api_client
    api_client.session.close()

@pytest.fixture(scope="module")
def reset_db(api_client):
    assert "localhost" in api_client.base_url or "127.0.0.1" in api_client.base_url, \
        f"refusing to reset a non-local environment: {api_client.base_url}"
    res = api_client.post("/api/test/reset")
    assert res.status_code == 200, (
        "reset failed - is the SUT running with APP_ENV=test? "
        f"got {res.status_code}"
    )
    return res.json()

@pytest.fixture(scope="module")
def admin_token(api_client, reset_db) -> str:
    res = api_client.post("/api/auth/login", body={
        "email": "admin@shoplite.com", "password": "admin12345",
    })
    assert res.status_code == 200, res.text
    return res.json()["access_token"]

@pytest.fixture(scope="module")
def user_token(api_client, reset_db) -> str:
    res = api_client.post("/api/auth/login", body={
        "email": "user@shoplite.com", "password": "user12345",
    })
    assert res.status_code == 200, res.text
    return res.json()["access_token"]

@pytest.fixture
def fresh_user(api_client):
    def _make() -> str:
        email = f"u{uuid.uuid4().hex[:10]}@shoplite.com"
        reg = api_client.post("/api/auth/register", body= {
            "email": email, "password": "pass12345",
        })
        assert reg.status_code == 201, reg.text

        res = api_client.post("/api/auth/login", body= {
            "email": email, "password": "pass12345",
        })

        return res.json()["access_token"]
    return _make




##############################################
# UI FIXTURES
##############################################