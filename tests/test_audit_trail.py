from tests.test_incidents import SAMPLE_INCIDENT, auth, create_incident


def test_status_and_severity_change_writes_audit_log(client, reporter_token, analyst_token):
    incident_id = create_incident(client, reporter_token).json()["id"]

    client.patch(
        f"/api/v1/incidents/{incident_id}",
        json={"status": "INVESTIGATING", "severity": "CRITICAL"},
        headers=auth(analyst_token),
    )

    resp = client.get(f"/api/v1/incidents/{incident_id}/logs", headers=auth(analyst_token))
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) == 2

    by_field = {log["field_name"]: log for log in logs}
    assert by_field["status"]["old_value"] == "OPEN"
    assert by_field["status"]["new_value"] == "INVESTIGATING"
    assert by_field["severity"]["old_value"] == SAMPLE_INCIDENT["severity"]
    assert by_field["severity"]["new_value"] == "CRITICAL"
    for log in logs:
        assert log["incident_id"] == incident_id


def test_no_op_update_does_not_write_audit_log(client, reporter_token, analyst_token):
    incident_id = create_incident(client, reporter_token).json()["id"]

    client.patch(
        f"/api/v1/incidents/{incident_id}",
        json={"severity": SAMPLE_INCIDENT["severity"]},
        headers=auth(analyst_token),
    )

    resp = client.get(f"/api/v1/incidents/{incident_id}/logs", headers=auth(analyst_token))
    assert resp.json() == []


def test_reporter_cannot_read_audit_trail(client, reporter_token):
    incident_id = create_incident(client, reporter_token).json()["id"]
    resp = client.get(f"/api/v1/incidents/{incident_id}/logs", headers=auth(reporter_token))
    assert resp.status_code == 403
