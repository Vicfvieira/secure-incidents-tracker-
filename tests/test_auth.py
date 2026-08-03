from tests.conftest import login, register


def test_first_registered_user_becomes_admin(client):
    resp = register(client, "first@example.com")
    assert resp.status_code == 201
    assert resp.json()["role"] == "ADMIN"


def test_second_self_registered_user_becomes_reporter(client):
    register(client, "first@example.com")
    resp = register(client, "second@example.com")
    assert resp.status_code == 201
    assert resp.json()["role"] == "REPORTER"


def test_duplicate_email_registration_rejected(client):
    register(client, "dup@example.com")
    resp = register(client, "dup@example.com")
    assert resp.status_code == 409


def test_login_success_returns_jwt(client):
    register(client, "user@example.com", password="StrongPass1")
    resp = client.post(
        "/api/v1/auth/login", json={"email": "user@example.com", "password": "StrongPass1"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password_rejected(client):
    register(client, "user@example.com", password="StrongPass1")
    resp = client.post(
        "/api/v1/auth/login", json={"email": "user@example.com", "password": "WrongPass"}
    )
    assert resp.status_code == 401


def test_login_unknown_email_rejected(client):
    resp = client.post(
        "/api/v1/auth/login", json={"email": "nobody@example.com", "password": "whatever"}
    )
    assert resp.status_code == 401


def test_protected_endpoint_requires_token(client):
    resp = client.get("/api/v1/incidents")
    assert resp.status_code == 401


def test_protected_endpoint_rejects_garbage_token(client):
    resp = client.get("/api/v1/incidents", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401
