"""Budget entry endpoints used to track spend against each project."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.core.permissions import PermissionError, can_write_budget_entry, require
from app.database import get_db
from app.models.budget_entry import BudgetEntry
from app.schemas.budget_entry import BudgetEntryCreate, BudgetEntryRead
from app.services.realtime import manager

router = APIRouter(prefix="/api/budget-entries", tags=["budget"])


@router.get("", response_model=list[BudgetEntryRead])
def list_budget_entries(
    current_user: CurrentUser, db: Session = Depends(get_db), project_id: int | None = None
) -> list[BudgetEntry]:
    """List budget entries, optionally filtered by project."""
    query = db.query(BudgetEntry)
    if project_id is not None:
        query = query.filter(BudgetEntry.project_id == project_id)
    return query.order_by(BudgetEntry.incurred_on.desc()).all()


@router.post("", response_model=BudgetEntryRead, status_code=status.HTTP_201_CREATED)
async def create_budget_entry(
    payload: BudgetEntryCreate, current_user: CurrentUser, db: Session = Depends(get_db)
) -> BudgetEntry:
    """Record a new spend line item. Restricted to project managers (admins)."""
    try:
        require(can_write_budget_entry(current_user))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    entry = BudgetEntry(**payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    await manager.broadcast("budget.created", {"project_id": entry.project_id})
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget_entry(
    entry_id: int, current_user: CurrentUser, db: Session = Depends(get_db)
) -> None:
    """Delete a spend line item. Restricted to project managers (admins)."""
    try:
        require(can_write_budget_entry(current_user))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    entry = db.get(BudgetEntry, entry_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget entry not found.")

    project_id = entry.project_id
    db.delete(entry)
    db.commit()
    await manager.broadcast("budget.deleted", {"project_id": project_id})
