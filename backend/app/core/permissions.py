"""Centralized authorization rules.

Keeping every permission check in one module makes the access-control
policy auditable at a glance and prevents subtly inconsistent checks
from being duplicated across route handlers.

Policy summary
--------------
- ADMIN: unrestricted read/write access to all projects, tasks,
  blockers, and budget entries.
- MEMBER: read access to any project they belong to; write access only
  to tasks assigned to them and blockers they report.
- EXECUTIVE: read-only access to portfolio summaries and drill-down
  records. Never permitted to create, update, or delete anything.
"""
from app.models.enums import UserRole
from app.models.task import Task
from app.models.user import User


class PermissionError(Exception):
    """Raised when a user attempts an action they are not authorized for."""


def can_view_dashboard(user: User) -> bool:
    """All authenticated roles may view dashboard summaries."""
    return True


def can_write_project(user: User) -> bool:
    """Only admins (project managers) may create or edit projects."""
    return user.role == UserRole.ADMIN


def can_write_budget_entry(user: User) -> bool:
    """Only admins may record budget entries against a project."""
    return user.role == UserRole.ADMIN


def can_write_blocker(user: User) -> bool:
    """Admins and members may report blockers; executives may not."""
    return user.role in (UserRole.ADMIN, UserRole.MEMBER)


def can_resolve_blocker(user: User) -> bool:
    """Only admins may mark a blocker as resolved."""
    return user.role == UserRole.ADMIN


def can_write_task(user: User, task: Task | None = None) -> bool:
    """Admins may edit any task; members may only edit their own."""
    if user.role == UserRole.ADMIN:
        return True
    if user.role == UserRole.MEMBER and task is not None:
        return task.assignee_id == user.id
    return False


def can_create_task(user: User, assignee_id: int | None) -> bool:
    """Admins may assign tasks to anyone; members may only self-assign."""
    if user.role == UserRole.ADMIN:
        return True
    if user.role == UserRole.MEMBER:
        return assignee_id == user.id
    return False


def require(condition: bool, message: str = "You are not authorized to perform this action.") -> None:
    """Raise PermissionError if the given condition is False."""
    if not condition:
        raise PermissionError(message)
