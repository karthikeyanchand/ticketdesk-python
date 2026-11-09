import os
import tempfile

import pytest

_tmp = tempfile.mkdtemp(prefix="ticketdesk-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["STORAGE_DIR"] = f"{_tmp}/attachments"
os.environ["JWT_SECRET"] = "test-secret-not-for-production"

from fastapi.testclient import TestClient  # noqa: E402

import seed  # noqa: E402
from ticketdesk.main import app  # noqa: E402

seed.main()


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


def login(client, email, password=seed.DEMO_PASSWORD):
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture(scope="session")
def acme_admin(client):
    return login(client, "admin@acme.example.com")


@pytest.fixture(scope="session")
def acme_agent(client):
    return login(client, "agent@acme.example.com")


@pytest.fixture(scope="session")
def acme_customer(client):
    return login(client, "cust@acme.example.com")
