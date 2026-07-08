"""Enumerations shared by ORM models and Pydantic schemas."""
import enum


class UserRole(str, enum.Enum):
    """Access levels enforced throughout the API.

    - ADMIN: project managers and system administrators. Full read/write
      access to every project, task, budget entry, and user record.
    - MEMBER: individual contributors. Can update only the tasks and
      status updates assigned to them.
    - EXECUTIVE: read-only access to portfolio-level summaries. Cannot
      view or edit raw records unless explicitly drilling into a project
      they have been granted visibility on.
    """

    ADMIN = "admin"
    MEMBER = "member"
    EXECUTIVE = "executive"


class ProjectStage(str, enum.Enum):
    """Lifecycle stage of a project, from kickoff to close-out."""

    KICKOFF = "kickoff"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    REVIEW = "review"
    CLOSED = "closed"


class TaskStatus(str, enum.Enum):
    """Status of an individual task within a project."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"


class BlockerSeverity(str, enum.Enum):
    """Severity classification for a reported blocker."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TimelineHealth(str, enum.Enum):
    """Derived timeline health indicator used by dashboard widgets."""

    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    DELAYED = "delayed"
