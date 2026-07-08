"""Task CRUD endpoints.

Members may only create tasks assigned to themselves and may only edit
tasks already assigned to them; admins have unrestricted access.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.core.permissions import PermissionError, can_create_task, can_write_task, require
from app.database import get_db
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.realtime import manager

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead])
def list_tasks(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    project_id: int | None = None,
    assignee_id: int | None = None,
) -> list[Task]:
    """List tasks, optionally filtered by project or assignee."""
    query = db.query(Task)
    if project_id is not None:
        query = query.filter(Task.project_id == project_id)
    if assignee_id is not None:
        query = query.filter(Task.assignee_id == assignee_id)
    return query.order_by(Task.due_date.asc().nulls_last()).all()


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate, current_user: CurrentUser, db: Session = Depends(get_db)) -> Task:
    """Create a task. Members may only self-assign."""
    try:
        require(can_create_task(current_user, payload.assignee_id))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    await manager.broadcast("task.created", {"task_id": task.id, "project_id": task.project_id})
    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int, payload: TaskUpdate, current_user: CurrentUser, db: Session = Depends(get_db)
) -> Task:
    """Update a task. Members may only update tasks assigned to them."""
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    try:
        require(can_write_task(current_user, task))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    for field_name, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field_name, value)

    db.commit()
    db.refresh(task)
    await manager.broadcast("task.updated", {"task_id": task.id, "project_id": task.project_id})
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, current_user: CurrentUser, db: Session = Depends(get_db)) -> None:
    """Delete a task. Members may only delete tasks assigned to them."""
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    try:
        require(can_write_task(current_user, task))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    project_id = task.project_id
    db.delete(task)
    db.commit()
    await manager.broadcast("task.deleted", {"task_id": task_id, "project_id": project_id})
