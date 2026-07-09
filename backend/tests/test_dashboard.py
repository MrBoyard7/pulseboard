"""Tests for the analytics helpers and dashboard aggregation endpoints."""

from datetime import date, timedelta

from app.models.blocker import Blocker
from app.models.budget_entry import BudgetEntry
from app.models.enums import BlockerSeverity, TimelineHealth
from app.services.analytics import budget_burn_pct, timeline_health
from tests.conftest import auth_headers


def test_timeline_health_delayed_when_past_target_date(db_session, sample_project):
    sample_project.target_end_date = date.today() - timedelta(days=1)
    db_session.commit()
    assert timeline_health(sample_project) == TimelineHealth.DELAYED


def test_timeline_health_at_risk_with_critical_blocker(db_session, sample_project, admin_user):
    db_session.add(
        Blocker(
            project_id=sample_project.id,
            reported_by_id=admin_user.id,
            description="Critical vendor outage",
            severity=BlockerSeverity.CRITICAL,
            resolved=False,
        )
    )
    db_session.commit()
    db_session.refresh(sample_project)
    assert timeline_health(sample_project) == TimelineHealth.AT_RISK


def test_timeline_health_on_track_by_default(sample_project):
    assert timeline_health(sample_project) == TimelineHealth.ON_TRACK


def test_budget_burn_pct_computation(db_session, sample_project):
    db_session.add(
        BudgetEntry(project_id=sample_project.id, label="Invoice", amount=25_000, incurred_on=date.today())
    )
    db_session.commit()
    db_session.refresh(sample_project)
    # sample_project.budget_total == 100_000
    assert budget_burn_pct(sample_project) == 25.0


def test_dashboard_summary_endpoint_returns_expected_shape(client, admin_user, sample_project):
    headers = auth_headers(client, admin_user.email)
    response = client.get("/api/dashboard/summary", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    row = body[0]
    for field in (
        "id",
        "name",
        "stage",
        "owner_name",
        "budget_total",
        "budget_spent",
        "budget_burn_pct",
        "open_blockers",
        "critical_blockers",
        "timeline_health",
    ):
        assert field in row


def test_dashboard_kpis_endpoint(client, admin_user, sample_project):
    headers = auth_headers(client, admin_user.email)
    response = client.get("/api/dashboard/kpis", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total_projects"] == 1
