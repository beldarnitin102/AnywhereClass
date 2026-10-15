
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.repositories import user_repository
from app.schemas.auth import RegisterRequest

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import create_access_token, verify_password
from app.schemas.auth import LoginRequest


def register_user(db: Session, request: RegisterRequest):
    email = str(request.email).strip().lower()

    existing_user = user_repository.get_by_email(db, email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    hashed_password = hash_password(request.password)

    try:
        return user_repository.create_user(
            db=db,
            email=email,
            password_hash=hashed_password,
        )
    except IntegrityError:
        # Handles a possible concurrent duplicate registration.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )



def login_user(db: Session, request: LoginRequest) -> dict:
    email = str(request.email).strip().lower()
    user = user_repository.get_by_email(db, email)

    if (
        user is None
        or not user.is_active
        or not verify_password(request.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
