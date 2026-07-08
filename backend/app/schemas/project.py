"""Pydantic schemas for project creation, updates, and API responses."""
from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ProjectStage, TimelineHealth


class ProjectBase(BaseModel):
    name: str
    description: str | None = None
    stage: ProjectStage = ProjectStage.KICKOFF
    start_date: date
    target_end_date: date
    budget_total: float = Field(ge=0)
    owner_id: int
    team_id: int | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    stage: ProjectStage | None = None
    target_end_date: date | None = None
    actual_end_date: date | None = None
    budget_total: float | None = Field(default=None, ge=0)
    owner_id: int | None = None
    team_id: int | None = None


class ProjectRead(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actual_end_date: date | None = None


class ProjectSummary(BaseModel):
    """Aggregated, dashboard-friendly view of a single project."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    stage: ProjectStage
    owner_name: str
    budget_total: float
    budget_spent: float
    budget_burn_pct: float
    open_blockers: int
    critical_blockers: int
    timeline_health: TimelineHealth
    target_end_date: date
