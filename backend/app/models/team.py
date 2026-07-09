"""Team model: a group of users collaborating on one or more projects."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class Team(Base):
    """A functional or cross-functional team within the organization."""

    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    members: Mapped[list["User"]] = relationship(back_populates="team")  # noqa: F821
    projects: Mapped[list["Project"]] = relationship(back_populates="team")  # noqa: F821

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Team id={self.id} name={self.name!r}>"
