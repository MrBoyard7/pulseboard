"""Project model: the central entity tracked from kickoff to close-out."""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import ProjectStage


class Project(Base):
    """A tracked initiative with budget, timeline, and ownership."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    stage: Mapped[ProjectStage] = mapped_column(
        Enum(ProjectStage, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        default=ProjectStage.KICKOFF,
        nullable=False,
        index=True,
    )

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    budget_total: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped["User"] = relationship(back_populates="owned_projects", foreign_keys=[owner_id])
    team: Mapped["Team"] = relationship(back_populates="projects")
    tasks: Mapped[list["Task"]] = relationship(  # noqa: F821
        back_populates="project", cascade="all, delete-orphan"
    )
    blockers: Mapped[list["Blocker"]] = relationship(  # noqa: F821
        back_populates="project", cascade="all, delete-orphan"
    )
    budget_entries: Mapped[list["BudgetEntry"]] = relationship(  # noqa: F821
        back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Project id={self.id} name={self.name!r} stage={self.stage.value}>"