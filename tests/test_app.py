from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Basic assertions about structure
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_unregister_flow(client):
    activity = "Chess Club"
    email = "tester@example.com"

    # Ensure email is not present initially
    resp = client.get("/activities")
    assert resp.status_code == 200
    if email in resp.json().get(activity, {}).get("participants", []):
        # If test rerun left data behind, remove it first
        client.delete(f"/activities/{quote(activity, safe='')}/signup?email={quote(email, safe='')}" )

    # Sign up
    signup_resp = client.post(f"/activities/{quote(activity, safe='')}/signup?email={quote(email, safe='')}")
    assert signup_resp.status_code == 200
    assert "Signed up" in signup_resp.json().get("message", "")

    # Verify participant present
    resp2 = client.get("/activities")
    participants = resp2.json()[activity]["participants"]
    assert email in participants

    # Signing up again should fail with 400
    dup_resp = client.post(f"/activities/{quote(activity, safe='')}/signup?email={quote(email, safe='')}")
    assert dup_resp.status_code == 400

    # Unregister
    del_resp = client.delete(f"/activities/{quote(activity, safe='')}/signup?email={quote(email, safe='')}")
    assert del_resp.status_code == 200
    assert "Unregistered" in del_resp.json().get("message", "")

    # Verify removed
    resp3 = client.get("/activities")
    participants_after = resp3.json()[activity]["participants"]
    assert email not in participants_after
