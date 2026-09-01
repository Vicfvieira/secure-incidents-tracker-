def auth(token):
    return {"Authorization": f"Bearer {token}"}


SAMPLE_INCIDENT = {
    "title": "Suspeita de Phishing no RH",
    "description": "E-mail com anexo malicioso enviado para o setor de RH. Contém dados de funcionários.",
    "severity": "HIGH",
    "type": "PHISHING",
    "indicators": ["malicious-link.com", "192.168.1.50"],
}


def create_incident(client, token, payload=None):
    return client.post("/api/v1/incidents", json=payload or SAMPLE_INCIDENT, headers=auth(token))


def test_reporter_can_create_incident(client, reporter_token):
    resp = create_incident(client, reporter_token)
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == SAMPLE_INCIDENT["title"]
    assert body["status"] == "OPEN"
    assert body["indicators"] == SAMPLE_INCIDENT["indicators"]


def test_reporter_only_sees_own_incidents(client, reporter_token, analyst_token):
    create_incident(client, reporter_token)
    create_incident(client, analyst_token, {**SAMPLE_INCIDENT, "title": "Other incident"})

    resp = client.get("/api/v1/incidents", headers=auth(reporter_token))
    assert resp.status_code == 200
    body = resp.json()
    titles = [i["title"] for i in body["items"]]
    assert titles == [SAMPLE_INCIDENT["title"]]
    assert body["total"] == 1


def test_analyst_sees_all_incidents(client, reporter_token, analyst_token):
    create_incident(client, reporter_token)
    create_incident(client, analyst_token, {**SAMPLE_INCIDENT, "title": "Other incident"})

    resp = client.get("/api/v1/incidents", headers=auth(analyst_token))
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) == 2
    assert body["total"] == 2


def test_reporter_cannot_view_other_reporters_incident(client, reporter_token, admin_token):
    from tests.conftest import login, register

    register(client, "other-reporter@example.com")
    other_token = login(client, "other-reporter@example.com")
    incident_id = create_incident(client, other_token).json()["id"]

    resp = client.get(f"/api/v1/incidents/{incident_id}", headers=auth(reporter_token))
    assert resp.status_code == 403


def test_reporter_cannot_patch_incident(client, reporter_token):
    incident_id = create_incident(client, reporter_token).json()["id"]
    resp = client.patch(
        f"/api/v1/incidents/{incident_id}", json={"status": "INVESTIGATING"}, headers=auth(reporter_token)
    )
    assert resp.status_code == 403


def test_analyst_can_patch_status_and_severity(client, reporter_token, analyst_token):
    incident_id = create_incident(client, reporter_token).json()["id"]
    resp = client.patch(
        f"/api/v1/incidents/{incident_id}",
        json={"status": "INVESTIGATING", "severity": "CRITICAL"},
        headers=auth(analyst_token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "INVESTIGATING"
    assert body["severity"] == "CRITICAL"


def test_reporter_cannot_delete_incident(client, reporter_token):
    incident_id = create_incident(client, reporter_token).json()["id"]
    resp = client.delete(f"/api/v1/incidents/{incident_id}", headers=auth(reporter_token))
    assert resp.status_code == 403


def test_analyst_cannot_delete_incident(client, reporter_token, analyst_token):
    incident_id = create_incident(client, reporter_token).json()["id"]
    resp = client.delete(f"/api/v1/incidents/{incident_id}", headers=auth(analyst_token))
    assert resp.status_code == 403


def test_admin_can_delete_incident(client, reporter_token, admin_token):
    incident_id = create_incident(client, reporter_token).json()["id"]
    resp = client.delete(f"/api/v1/incidents/{incident_id}", headers=auth(admin_token))
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/incidents/{incident_id}", headers=auth(admin_token))
    assert resp.status_code == 404


def test_get_nonexistent_incident_returns_404(client, admin_token):
    resp = client.get("/api/v1/incidents/does-not-exist", headers=auth(admin_token))
    assert resp.status_code == 404
