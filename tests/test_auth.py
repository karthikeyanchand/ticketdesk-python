from .conftest import login


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_login_rejects_bad_password(client):
    resp = client.post("/auth/login", json={"email": "admin@acme.example.com", "password": "nope-nope-nope"})
    assert resp.status_code == 401


def test_me(client, acme_agent):
    me = client.get("/users/me", headers=acme_agent).json()
    assert me["email"] == "agent@acme.example.com"
    assert me["role"] == "agent"


def test_signup_creates_admin(client):
    resp = client.post("/auth/signup", json={"org_name": "Initech", "org_slug": "initech",
                                             "email": "boss@initech.example.com", "password": "long-enough-pw"})
    assert resp.status_code == 201
    headers = login(client, "boss@initech.example.com", "long-enough-pw")
    assert client.get("/users/me", headers=headers).json()["role"] == "admin"


def test_forgot_password_does_not_leak_existence(client):
    a = client.post("/auth/forgot-password", json={"email": "admin@acme.example.com"})
    b = client.post("/auth/forgot-password", json={"email": "nobody@acme.example.com"})
    assert a.status_code == b.status_code == 202
    assert a.json() == b.json()
