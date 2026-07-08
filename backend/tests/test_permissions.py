"""Tests enforcing the role-based access control policy end to end."""
from tests.conftest import auth_headers


def test_member_can_self_assign_task(client, member_user, sample_project):
    headers = auth_headers(client, member_user.email)
    payload = {"title": "Write test plan", "project_id": sample_project.id, "assignee_id": member_user.id}
    response = client.post("/api/tasks", json=payload, headers=headers)
    assert response.status_code == 201


def test_member_cannot_assign_task_to_someone_else(client, member_user, admin_user, sample_project):
    headers = auth_headers(client, member_user.email)
    payload = {"title": "Sneaky assignment", "project_id": sample_project.id, "assignee_id": admin_user.id}
    response = client.post("/api/tasks", json=payload, headers=headers)
    assert response.status_code == 403


def test_member_cannot_edit_others_task(client, member_user, admin_user, sample_project):
    admin_headers = auth_headers(client, admin_user.email)
    create_response = client.post(
        "/api/tasks",
        json={"title": "Admin's task", "project_id": sample_project.id, "assignee_id": admin_user.id},
        headers=admin_headers,
    )
    task_id = create_response.json()["id"]

    member_headers = auth_headers(client, member_user.email)
    response = client.patch(f"/api/tasks/{task_id}", json={"status": "done"}, headers=member_headers)
    assert response.status_code == 403


def test_executive_cannot_report_blocker(client, executive_user, sample_project):
    headers = auth_headers(client, executive_user.email)
    payload = {"description": "Should not be allowed", "project_id": sample_project.id}
    response = client.post("/api/blockers", json=payload, headers=headers)
    assert response.status_code == 403


def test_member_can_report_blocker_but_not_resolve_it(client, member_user, sample_project):
    headers = auth_headers(client, member_user.email)
    create_response = client.post(
        "/api/blockers",
        json={"description": "Waiting on vendor", "project_id": sample_project.id},
        headers=headers,
    )
    assert create_response.status_code == 201
    blocker_id = create_response.json()["id"]

    resolve_response = client.patch(
        f"/api/blockers/{blocker_id}", json={"resolved": True}, headers=headers
    )
    assert resolve_response.status_code == 403


def test_executive_can_read_dashboard_summary(client, executive_user, sample_project):
    headers = auth_headers(client, executive_user.email)
    response = client.get("/api/dashboard/summary", headers=headers)
    assert response.status_code == 200
