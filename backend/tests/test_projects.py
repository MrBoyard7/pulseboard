"""Tests for project creation, listing, filtering, and updates."""
from datetime import date, timedelta

from tests.conftest import auth_headers


def test_admin_can_create_project(client, admin_user):
    headers = auth_headers(client, admin_user.email)
    payload = {
        "name": "New Platform Migration",
        "description": "Move core services to the new platform.",
        "stage": "planning",
        "start_date": str(date.today()),
        "target_end_date": str(date.today() + timedelta(days=90)),
        "budget_total": 50000,
        "owner_id": admin_user.id,
    }
    response = client.post("/api/projects", json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["name"] == "New Platform Migration"


def test_member_cannot_create_project(client, member_user):
    headers = auth_headers(client, member_user.email)
    payload = {
        "name": "Unauthorized Project",
        "start_date": str(date.today()),
        "target_end_date": str(date.today() + timedelta(days=30)),
        "budget_total": 10000,
        "owner_id": member_user.id,
    }
    response = client.post("/api/projects", json=payload, headers=headers)
    assert response.status_code == 403


def test_list_projects_filters_by_stage(client, admin_user, sample_project):
    headers = auth_headers(client, admin_user.email)
    response = client.get("/api/projects", params={"stage": "kickoff"}, headers=headers)
    assert response.status_code == 200
    assert any(p["id"] == sample_project.id for p in response.json())

    response = client.get("/api/projects", params={"stage": "closed"}, headers=headers)
    assert all(p["id"] != sample_project.id for p in response.json())


def test_get_project_not_found_returns_404(client, admin_user):
    headers = auth_headers(client, admin_user.email)
    response = client.get("/api/projects/999999", headers=headers)
    assert response.status_code == 404


def test_admin_can_update_project_stage(client, admin_user, sample_project):
    headers = auth_headers(client, admin_user.email)
    response = client.patch(
        f"/api/projects/{sample_project.id}", json={"stage": "in_progress"}, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["stage"] == "in_progress"
