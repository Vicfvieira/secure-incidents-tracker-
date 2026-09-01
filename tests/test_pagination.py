from tests.test_incidents import SAMPLE_INCIDENT, auth, create_incident


def _create_many(client, token, count, **overrides):
    for i in range(count):
        payload = {**SAMPLE_INCIDENT, "title": f"Incident {i}", **overrides}
        create_incident(client, token, payload)


def test_default_pagination_values(client, reporter_token):
    _create_many(client, reporter_token, 3)

    resp = client.get("/api/v1/incidents", headers=auth(reporter_token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["page"] == 1
    assert body["limit"] == 20
    assert body["total"] == 3
    assert body["total_pages"] == 1
    assert len(body["items"]) == 3


def test_pagination_splits_results_across_pages(client, reporter_token):
    _create_many(client, reporter_token, 5)

    resp = client.get("/api/v1/incidents?page=1&limit=2", headers=auth(reporter_token))
    body = resp.json()
    assert body["total"] == 5
    assert body["total_pages"] == 3
    assert len(body["items"]) == 2

    resp = client.get("/api/v1/incidents?page=3&limit=2", headers=auth(reporter_token))
    body = resp.json()
    assert len(body["items"]) == 1
    assert body["page"] == 3


def test_page_beyond_last_page_returns_empty_items(client, reporter_token):
    _create_many(client, reporter_token, 2)

    resp = client.get("/api/v1/incidents?page=99&limit=10", headers=auth(reporter_token))
    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 2


def test_limit_is_capped_at_maximum(client, reporter_token):
    resp = client.get("/api/v1/incidents?limit=1000", headers=auth(reporter_token))
    assert resp.status_code == 422


def test_page_below_one_is_rejected(client, reporter_token):
    resp = client.get("/api/v1/incidents?page=0", headers=auth(reporter_token))
    assert resp.status_code == 422


def test_filter_by_severity(client, reporter_token):
    create_incident(client, reporter_token, {**SAMPLE_INCIDENT, "title": "High one", "severity": "HIGH"})
    create_incident(client, reporter_token, {**SAMPLE_INCIDENT, "title": "Low one", "severity": "LOW"})

    resp = client.get("/api/v1/incidents?severity=LOW", headers=auth(reporter_token))
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Low one"


def test_filter_by_status(client, reporter_token, analyst_token):
    incident_id = create_incident(client, reporter_token).json()["id"]
    create_incident(client, reporter_token, {**SAMPLE_INCIDENT, "title": "Second incident"})

    client.patch(
        f"/api/v1/incidents/{incident_id}",
        json={"status": "INVESTIGATING"},
        headers=auth(analyst_token),
    )

    resp = client.get("/api/v1/incidents?status=INVESTIGATING", headers=auth(reporter_token))
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == incident_id

    resp = client.get("/api/v1/incidents?status=OPEN", headers=auth(reporter_token))
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Second incident"


def test_combined_severity_and_status_filters(client, reporter_token, analyst_token):
    matching_id = create_incident(
        client, reporter_token, {**SAMPLE_INCIDENT, "title": "Match", "severity": "CRITICAL"}
    ).json()["id"]
    create_incident(client, reporter_token, {**SAMPLE_INCIDENT, "title": "Wrong severity", "severity": "LOW"})

    client.patch(
        f"/api/v1/incidents/{matching_id}",
        json={"status": "MITIGATED"},
        headers=auth(analyst_token),
    )

    resp = client.get(
        "/api/v1/incidents?severity=CRITICAL&status=MITIGATED", headers=auth(reporter_token)
    )
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == matching_id


def test_reporter_pagination_is_still_scoped_to_own_incidents(client, reporter_token, analyst_token):
    create_incident(client, reporter_token)
    create_incident(client, analyst_token, {**SAMPLE_INCIDENT, "title": "Not mine"})

    resp = client.get("/api/v1/incidents?limit=50", headers=auth(reporter_token))
    body = resp.json()
    assert body["total"] == 1
