"""Dashboard endpoints: the aggregated views the frontend renders."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.api.deps import CurrentUser
from app.database import get_db
from app.models.enums import ProjectStage, TimelineHealth
from app.models.project import Project
from app.schemas.project import ProjectSummary
from app.services.analytics import budget_burn_pct, budget_spent, open_blocker_counts, timeline_health

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=list[ProjectSummary])
def portfolio_summary(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    stage: ProjectStage | None = None,
    owner_id: int | None = None,
    health: TimelineHealth | None = None,
) -> list[ProjectSummary]:
    """Return one summary row per project for the portfolio-level view.

    All three roles (admin, member, executive) may call this endpoint;
    it never exposes edit affordances, only read-only aggregates, so it
    is safe for executives per the role policy.
    """
    query = db.query(Project).options(
        joinedload(Project.owner), joinedload(Project.blockers), joinedload(Project.budget_entries)
    )
    if stage is not None:
        query = query.filter(Project.stage == stage)
    if owner_id is not None:
        query = query.filter(Project.owner_id == owner_id)

    summaries: list[ProjectSummary] = []
    for project in query.all():
        computed_health = timeline_health(project)
        if health is not None and computed_health != health:
            continue

        open_blockers, critical_blockers = open_blocker_counts(project)
        summaries.append(
            ProjectSummary(
                id=project.id,
                name=project.name,
                stage=project.stage,
                owner_name=project.owner.full_name,
                budget_total=float(project.budget_total),
                budget_spent=budget_spent(project),
                budget_burn_pct=budget_burn_pct(project),
                open_blockers=open_blockers,
                critical_blockers=critical_blockers,
                timeline_health=computed_health,
                target_end_date=project.target_end_date,
            )
        )
    return summaries


@router.get("/kpis")
def portfolio_kpis(current_user: CurrentUser, db: Session = Depends(get_db)) -> dict:
    """Return headline portfolio KPIs shown at the top of the dashboard."""
    projects = db.query(Project).options(
        joinedload(Project.blockers), joinedload(Project.budget_entries)
    ).all()

    active = [p for p in projects if p.stage not in (ProjectStage.CLOSED,)]
    delayed = [p for p in projects if timeline_health(p) == TimelineHealth.DELAYED]
    at_risk = [p for p in projects if timeline_health(p) == TimelineHealth.AT_RISK]
    total_budget = sum(float(p.budget_total) for p in projects)
    total_spent = sum(budget_spent(p) for p in projects)

    return {
        "total_projects": len(projects),
        "active_projects": len(active),
        "delayed_projects": len(delayed),
        "at_risk_projects": len(at_risk),
        "total_budget": total_budget,
        "total_spent": total_spent,
        "overall_burn_pct": round((total_spent / total_budget * 100), 1) if total_budget else 0.0,
    }
