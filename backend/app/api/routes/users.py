"""User management endpoints. Creation and listing are admin-only."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, require_roles
from app.core.security import hash_password
from app.database import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserRead], dependencies=[Depends(require_roles(UserRole.ADMIN))])
def list_users(db: Session = Depends(get_db)) -> list[User]:
    """List every user account. Restricted to admins."""
    return db.query(User).order_by(User.full_name).all()


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    """Create a new user account. Restricted to admins."""
    if db.query(User).filter(User.email == payload.email).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        team_id=payload.team_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserRead)
def read_own_profile(current_user: CurrentUser) -> User:
    """Convenience alias for /api/auth/me, kept under /api/users for symmetry."""
    return current_user
