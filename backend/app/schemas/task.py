"""Pydantic schemas for task creation, updates, and API responses."""

from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import TaskStatus


class TaskBase(BaseModel):
    title: str
    status: TaskStatus = TaskStatus.TODO
    due_date: date | None = None
    assignee_id: int | None = None


class TaskCreate(TaskBase):
    project_id: int


class TaskUpdate(BaseModel):
    title: str | None = None
    status: TaskStatus | None = None
    due_date: date | None = None
    assignee_id: int | None = None


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
