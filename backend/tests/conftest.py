import os
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

# Use a temporary in-memory-ish file DB for tests
TEST_DB = Path(tempfile.gettempdir()) / "semyainfo_test.sqlite"
if TEST_DB.exists():
    TEST_DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["JWT_SECRET"] = "test-secret"


@pytest.fixture(scope="session")
def client():
    from main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def editor_token(client):
    resp = client.post(
        "/api/auth/login",
        json={"email": "editor@semyainfo.dev", "password": "editor123"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def admin_token(client):
    resp = client.post(
        "/api/auth/login",
        json={"email": "admin@semyainfo.dev", "password": "admin123"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}