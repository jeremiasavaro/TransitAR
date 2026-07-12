from datetime import datetime, timezone

from fastapi import HTTPException, status
from jwt import PyJWTError
from models.revoked_token import RevokedToken
from models.user import User
from schemas.user import (
    PasswordResetConfirmRead,
    PasswordResetRequestRead,
    TokenRead,
    UserRead,
)
from sqlalchemy import select
from sqlalchemy.orm import Session
from utils.security import (
    create_access_token,
    create_reset_token,
    decode_reset_token,
    hash_password,
    verify_password,
)


def register_user(db: Session, email: str, password: str) -> UserRead:
    # Keep the service tiny: check duplicates, create the row, and return public data.
    existing_user = db.scalar(select(User).where(User.email == email))
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="email already registered"
        )

    user = User(email=email, password_hash=hash_password(password))
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="email already registered"
        )
    return UserRead.model_validate(user)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.scalar(select(User).where(User.id == user_id))


def authenticate_user_and_create_token(
    db: Session, email: str, password: str
) -> TokenRead:
    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials"
        )

    token = create_access_token(
        subject=str(user.id), extra_claims={"email": user.email}
    )
    return TokenRead(access_token=token)


def is_token_revoked(db: Session, jti: str) -> bool:
    # Check if the token's JTI is in the revoked tokens table. If it is, the token is considered revoked.
    return db.scalar(select(RevokedToken).where(RevokedToken.jti == jti)) is not None


def revoke_token(db: Session, jti: str, token_type: str, expires_at: datetime) -> None:
    # If the token is already revoked, we don't need to add it again.
    if is_token_revoked(db, jti):
        return

    # Store the revoked token in the database. This will prevent future use of this token.
    revoked = RevokedToken(jti=jti, token_type=token_type, expires_at=expires_at)
    db.add(revoked)
    db.commit()


def request_password_reset(db: Session, email: str) -> PasswordResetRequestRead:
    user = get_user_by_email(db, email)
    if user is None:
        # Keep response generic to avoid leaking user existence.
        return PasswordResetRequestRead(
            message="If the account exists, a reset token was generated"
        )
    # Generate a reset token for the user. In a real application, this token would be sent via email.
    reset_token = create_reset_token(subject=str(user.id))
    return PasswordResetRequestRead(
        reset_token=reset_token,
        message="Use this reset token to confirm password reset",
    )


def confirm_password_reset(
    db: Session, reset_token: str, new_password: str
) -> PasswordResetConfirmRead:
    # Validate the reset token and ensure it hasn't been revoked.
    # If valid, update the user's password and revoke the token.
    try:
        payload = decode_reset_token(reset_token)
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid reset token"
        ) from None

    jti = payload.get("jti")
    if not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid reset token"
        )

    if is_token_revoked(db, jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="reset token already used"
        )

    raw_user_id = payload.get("sub")
    try:
        user_id = int(raw_user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid reset token"
        ) from None

    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid reset token"
        )

    user.password_hash = hash_password(new_password)
    db.add(user)

    exp_timestamp = payload.get("exp")
    if isinstance(exp_timestamp, int):
        expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    else:
        expires_at = datetime.now(timezone.utc)

    revoked = RevokedToken(jti=jti, token_type="reset_password", expires_at=expires_at)
    db.add(revoked)
    db.commit()

    return PasswordResetConfirmRead(message="password updated")
