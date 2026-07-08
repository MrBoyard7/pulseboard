"""Blocker endpoints: reporting and resolving project obstacles."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.core.permissions import PermissionError, can_resolve_blocker, can_write_blocker, require
from app.database import get_db
from app.models.blocker import Blocker
from app.schemas.blocker import BlockerCreate, BlockerRead, BlockerUpdate
from app.services.realtime import manager

router = APIRouter(prefix="/api/blockers", tags=["blockers"])


@router.get("", response_model=list[BlockerRead])
def list_blockers(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    project_id: int | None = None,
    resolved: bool | None = None,
) -> list[Blocker]:
    """List blockers, optionally filtered by project or resolution state."""
    query = db.query(Blocker)
    if project_id is not None:
        query = query.filter(Blocker.project_id == project_id)
    if resolved is not None:
        query = query.filter(Blocker.resolved == resolved)
    return query.order_by(Blocker.created_at.desc()).all()


@router.post("", response_model=BlockerRead, status_code=status.HTTP_201_CREATED)
async def create_blocker(
    payload: BlockerCreate, current_user: CurrentUser, db: Session = Depends(get_db)
) -> Blocker:
    """Report a new blocker. Admins and members may report; executives may not."""
    try:
        require(can_write_blocker(current_user))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    blocker = Blocker(**payload.model_dump(), reported_by_id=current_user.id)
    db.add(blocker)
    db.commit()
    db.refresh(blocker)
    await manager.broadcast("blocker.created", {"blocker_id": blocker.id, "project_id": blocker.project_id})
    return blocker


@router.patch("/{blocker_id}", response_model=BlockerRead)
async def update_blocker(
    blocker_id: int, payload: BlockerUpdate, current_user: CurrentUser, db: Session = Depends(get_db)
) -> Blocker:
    """Update a blocker. Only admins may mark a blocker as resolved."""
    blocker = db.get(Blocker, blocker_id)
    if blocker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blocker not found.")

    data = payload.model_dump(exclude_unset=True)
    if "resolved" in data:
        try:
            require(can_resolve_blocker(current_user))
        except PermissionError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
        if data["resolved"]:
            blocker.resolved_at = datetime.now(timezone.utc)

    for field_name, value in data.items():
        setattr(blocker, field_name, value)

    db.commit()
    db.refresh(blocker)
    await manager.broadcast("blocker.updated", {"blocker_id": blocker.id, "project_id": blocker.project_id})
    return blocker
