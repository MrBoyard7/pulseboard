"""Pydantic schemas for budget entry creation and API responses."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class BudgetEntryBase(BaseModel):
    label: str
    amount: float = Field(ge=0)
    incurred_on: date


class BudgetEntryCreate(BudgetEntryBase):
    project_id: int


class BudgetEntryRead(BudgetEntryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
