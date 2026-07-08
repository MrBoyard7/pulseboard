"""Blocker model: an obstacle reported against a project."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import BlockerSeverity


class Blocker(Base):
    """A reported obstacle that threatens a project's timeline or budget."""

    __tablename__ = "blockers"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    reported_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    severity: Mapped[BlockerSeverity] = mapped_column(
        Enum(BlockerSeverity, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        default=BlockerSeverity.MEDIUM,
        nullable=False,
    )
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="blockers")
    reported_by: Mapped["User"] = relationship()

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Blocker id={self.id} severity={self.severity.value} resolved={self.resolved}>"