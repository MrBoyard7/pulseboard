"""ORM model registry.

Importing every model here ensures SQLAlchemy's mapper configuration
sees all classes and can resolve string-based relationship references
(e.g. `Mapped["Project"]`) regardless of import order elsewhere in the
application.
"""
from app.models.blocker import Blocker
from app.models.budget_entry import BudgetEntry
from app.models.project import Project
from app.models.task import Task
from app.models.team import Team
from app.models.user import User

__all__ = ["Blocker", "BudgetEntry", "Project", "Task", "Team", "User"]
