"""Task model: a unit of work owned by a single assignee within a project."""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import TaskStatus

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class Task(Base):
    """A discrete, assignable piece of work belonging to a project."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        default=TaskStatus.TODO,
        nullable=False,
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped["Project"] = relationship(back_populates="tasks")
    assignee: Mapped["User"] = relationship(back_populates="assigned_tasks")

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Task id={self.id} title={self.title!r} status={self.status.value}>"
