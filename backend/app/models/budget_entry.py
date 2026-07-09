"""BudgetEntry model: an individual spend recorded against a project."""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.project import Project


class BudgetEntry(Base):
    """A single expense line item that contributes to a project's budget burn."""

    __tablename__ = "budget_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)

    label: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    incurred_on: Mapped[date] = mapped_column(Date, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="budget_entries")

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<BudgetEntry id={self.id} label={self.label!r} amount={self.amount}>"
