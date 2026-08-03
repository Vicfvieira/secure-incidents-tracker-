from tests.conftest import register
from tests.test_incidents import auth


def test_reporter_cannot_create_users(client, reporter_token):
    resp = client.post(
        "/api/v1/users",
        json={"email": "new@example.com", "password": "Password123", "full_name": "New", "role": "ANALYST"},
        headers=auth(reporter_token),
    )
    assert resp.status_code == 403


def test_reporter_cannot_list_users(client, reporter_token):
    resp = client.get("/api/v1/users", headers=auth(reporter_token))
    assert resp.status_code == 403


def test_admin_can_create_and_list_users(client, admin_token):
    resp = register(client, "new-analyst@example.com", role="ANALYST", admin_token=admin_token)
    assert resp.status_code == 201
    assert resp.json()["role"] == "ANALYST"

    resp = client.get("/api/v1/users", headers=auth(admin_token))
    assert resp.status_code == 200
    emails = [u["email"] for u in resp.json()]
    assert "new-analyst@example.com" in emails
    assert "admin@example.com" in emails


def test_read_me_returns_current_user(client, analyst_token):
    resp = client.get("/api/v1/users/me", headers=auth(analyst_token))
    assert resp.status_code == 200
    assert resp.json()["role"] == "ANALYST"
