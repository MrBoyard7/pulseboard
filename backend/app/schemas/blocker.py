"""Pydantic schemas for blocker creation, updates, and API responses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import BlockerSeverity


class BlockerBase(BaseModel):
    description: str
    severity: BlockerSeverity = BlockerSeverity.MEDIUM


class BlockerCreate(BlockerBase):
    project_id: int


class BlockerUpdate(BaseModel):
    description: str | None = None
    severity: BlockerSeverity | None = None
    resolved: bool | None = None


class BlockerRead(BlockerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    reported_by_id: int
    resolved: bool
    created_at: datetime
    resolved_at: datetime | None = None
