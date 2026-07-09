"""Pure functions that turn raw project records into dashboard metrics.

Isolating this math from the route handlers keeps it independently
testable and reusable (e.g. for a future scheduled report or CSV
export) without touching the HTTP layer.
"""

from datetime import date

from app.models.enums import BlockerSeverity, ProjectStage, TimelineHealth
from app.models.project import Project


def budget_spent(project: Project) -> float:
    """Sum every budget entry recorded against a project."""
    return float(sum(entry.amount for entry in project.budget_entries))


def budget_burn_pct(project: Project) -> float:
    """Percentage of total budget consumed so far, capped for display safety."""
    if project.budget_total <= 0:
        return 0.0
    pct = (budget_spent(project) / float(project.budget_total)) * 100
    return round(min(pct, 999.0), 1)


def open_blocker_counts(project: Project) -> tuple[int, int]:
    """Return (open_blockers, critical_open_blockers) for a project."""
    open_blockers = [b for b in project.blockers if not b.resolved]
    critical = [b for b in open_blockers if b.severity == BlockerSeverity.CRITICAL]
    return len(open_blockers), len(critical)


def timeline_health(project: Project, today: date | None = None) -> TimelineHealth:
    """Derive a traffic-light timeline indicator for a project.

    Rules, evaluated in order:
    1. Past the target end date and not closed -> DELAYED.
    2. Any unresolved critical blocker -> AT_RISK.
    3. Budget burn above 90% while work remains -> AT_RISK.
    4. More time elapsed than the plan allotted (schedule slippage
       without yet crossing the deadline) -> AT_RISK.
    5. Otherwise -> ON_TRACK.
    """
    today = today or date.today()

    if project.stage != ProjectStage.CLOSED and today > project.target_end_date:
        return TimelineHealth.DELAYED

    _, critical_open = open_blocker_counts(project)
    if critical_open > 0:
        return TimelineHealth.AT_RISK

    if project.stage not in (ProjectStage.REVIEW, ProjectStage.CLOSED) and budget_burn_pct(project) >= 90:
        return TimelineHealth.AT_RISK

    total_duration = (project.target_end_date - project.start_date).days or 1
    elapsed = (today - project.start_date).days
    if project.stage not in (ProjectStage.REVIEW, ProjectStage.CLOSED) and elapsed / total_duration >= 0.9:
        return TimelineHealth.AT_RISK

    return TimelineHealth.ON_TRACK
