"""Project CRUD endpoints, including filtering used by the dashboard."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.core.permissions import PermissionError, can_write_project, require
from app.database import get_db
from app.models.enums import ProjectStage
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.realtime import manager

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead])
def list_projects(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    stage: ProjectStage | None = None,
    owner_id: int | None = None,
    team_id: int | None = None,
    search: str | None = Query(default=None, description="Case-insensitive name search"),
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[Project]:
    """List projects, optionally filtered by stage, owner, team, or name."""
    query = db.query(Project)
    if stage is not None:
        query = query.filter(Project.stage == stage)
    if owner_id is not None:
        query = query.filter(Project.owner_id == owner_id)
    if team_id is not None:
        query = query.filter(Project.team_id == team_id)
    if search:
        query = query.filter(Project.name.ilike(f"%{search}%"))
    return query.order_by(Project.updated_at.desc()).offset(offset).limit(limit).all()


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, current_user: CurrentUser, db: Session = Depends(get_db)) -> Project:
    """Retrieve a single project by id for drill-down views."""
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return project


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate, current_user: CurrentUser, db: Session = Depends(get_db)
) -> Project:
    """Create a new project. Restricted to project managers (admins)."""
    try:
        require(can_write_project(current_user))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    await manager.broadcast("project.created", {"project_id": project.id})
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int, payload: ProjectUpdate, current_user: CurrentUser, db: Session = Depends(get_db)
) -> Project:
    """Update a project. Restricted to project managers (admins)."""
    try:
        require(can_write_project(current_user))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    for field_name, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field_name, value)

    db.commit()
    db.refresh(project)
    await manager.broadcast("project.updated", {"project_id": project.id})
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, current_user: CurrentUser, db: Session = Depends(get_db)) -> None:
    """Delete a project and its dependent records. Restricted to admins."""
    try:
        require(can_write_project(current_user))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    db.delete(project)
    db.commit()
    await manager.broadcast("project.deleted", {"project_id": project_id})
