from tests.conftest import register


def test_login_is_rate_limited_after_five_attempts_per_minute(client):
    register(client, "ratelimit@example.com", password="CorrectPass123")

    for _ in range(5):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "ratelimit@example.com", "password": "WrongPass"},
        )
        assert resp.status_code == 401

    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "ratelimit@example.com", "password": "WrongPass"},
    )
    assert resp.status_code == 429


def test_rate_limit_applies_even_to_correct_credentials(client):
    register(client, "ratelimit2@example.com", password="CorrectPass123")

    for _ in range(5):
        client.post(
            "/api/v1/auth/login",
            json={"email": "ratelimit2@example.com", "password": "CorrectPass123"},
        )

    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "ratelimit2@example.com", "password": "CorrectPass123"},
    )
    assert resp.status_code == 429
