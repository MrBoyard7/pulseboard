"""Authentication endpoints: login and identity check."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.core.security import create_access_token, verify_password
from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserRead

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """Exchange an email/password pair for a JWT access token."""
    user = db.query(User).filter(User.email == credentials.email).first()
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled.")

    token = create_access_token(subject=str(user.id), role=user.role.value)
    return Token(access_token=token)


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: CurrentUser) -> User:
    """Return the profile of the currently authenticated user."""
    return current_user
