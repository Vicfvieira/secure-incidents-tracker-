from sqlalchemy import text

from tests.conftest import test_engine
from tests.test_incidents import SAMPLE_INCIDENT, create_incident


def test_description_and_indicators_are_encrypted_at_rest(client, reporter_token):
    incident_id = create_incident(client, reporter_token).json()["id"]

    with test_engine.connect() as conn:
        row = conn.execute(
            text("SELECT description, indicators FROM incidents WHERE id = :id"), {"id": incident_id}
        ).one()

    raw_description, raw_indicators = row
    assert SAMPLE_INCIDENT["description"] not in raw_description
    for ioc in SAMPLE_INCIDENT["indicators"]:
        assert ioc not in raw_indicators
    # Fernet ciphertext is base64 and always starts with this version byte prefix.
    assert raw_description.startswith("gAAAAA")
    assert raw_indicators.startswith("gAAAAA")


def test_api_transparently_decrypts_fields(client, reporter_token):
    resp = create_incident(client, reporter_token)
    body = resp.json()
    assert body["description"] == SAMPLE_INCIDENT["description"]
    assert body["indicators"] == SAMPLE_INCIDENT["indicators"]
