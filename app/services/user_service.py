from fastapi import HTTPException, status
from models.user import User
from schemas.user import UserRead
from sqlalchemy import select
from sqlalchemy.orm import Session
from utils.security import hash_password, verify_password


def register_user(db: Session, email: str, password: str) -> UserRead:
    # Keep the service tiny: check duplicates, create the row, and return public data.
    existing_user = db.scalar(select(User).where(User.email == email))
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="email already registered"
        )

    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


def authenticate_user(db: Session, email: str, password: str) -> UserRead:
    # Login only checks the credentials and returns the public user record.
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials"
        )

    return UserRead.model_validate(user)
