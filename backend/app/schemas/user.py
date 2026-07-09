"""Pydantic schemas for user creation, updates, and API responses."""

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import UserRole


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole = UserRole.MEMBER
    team_id: int | None = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: UserRole | None = None
    team_id: int | None = None
    is_active: bool | None = None
