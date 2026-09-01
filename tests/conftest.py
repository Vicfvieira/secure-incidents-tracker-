import os

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-key-not-for-production")
os.environ.setdefault("FIELD_ENCRYPTION_KEY", "MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTI=")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.rate_limit import limiter
from app.database import Base, get_db
from app.main import app

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def _reset_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    limiter.reset()
    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def register(client, email, password="Password123", full_name="Test User", role=None, admin_token=None):
    if role is None:
        return client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": full_name},
        )
    headers = {"Authorization": f"Bearer {admin_token}"}
    return client.post(
        "/api/v1/users",
        json={"email": email, "password": password, "full_name": full_name, "role": role},
        headers=headers,
    )


def login(client, email, password="Password123"):
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


@pytest.fixture
def admin_token(client):
    register(client, "admin@example.com")
    return login(client, "admin@example.com")


@pytest.fixture
def reporter_token(client, admin_token):
    register(client, "reporter@example.com")
    return login(client, "reporter@example.com")


@pytest.fixture
def analyst_token(client, admin_token):
    register(client, "analyst@example.com", role="ANALYST", admin_token=admin_token)
    return login(client, "analyst@example.com")
