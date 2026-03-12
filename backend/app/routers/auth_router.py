from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.db import get_session
from backend.app.core.security import ApiError, create_access_token, hash_password, require_authenticated_user, verify_password
from backend.app.models.user import User
from backend.app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest, session: Session = Depends(get_session)) -> AuthResponse:
    existing_user = session.scalar(select(User).where(User.email == payload.email))
    if existing_user is not None:
        raise ApiError(
            status_code=409,
            code="auth_registration_conflict",
            message="An account with that email already exists.",
        )

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return AuthResponse(
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at,
        ),
        access_token=create_access_token(user.id),
    )


@router.post("/login", response_model=AuthResponse)
def login_user(payload: LoginRequest, session: Session = Depends(get_session)) -> AuthResponse:
    user = session.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise ApiError(
            status_code=401,
            code="auth_invalid_credentials",
            message="Invalid email or password.",
        )

    return AuthResponse(
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at,
        ),
        access_token=create_access_token(user.id),
    )


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(require_authenticated_user)) -> UserResponse:
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
    )
