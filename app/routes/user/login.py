from datetime import datetime, timezone

from dependencies.auth import get_current_access_payload, get_current_user
from fastapi import APIRouter, Depends
from infrastructure.database.session import get_db
from models.user import User
from schemas.user import (
    LogoutRead,
    PasswordResetConfirm,
    PasswordResetConfirmRead,
    PasswordResetRequest,
    PasswordResetRequestRead,
    TokenRead,
    UserLogin,
)
from services.user_service import (
    authenticate_user_and_create_token,
    confirm_password_reset,
    request_password_reset,
    revoke_token,
)

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/login", response_model=TokenRead)
def login(payload: UserLogin, db=Depends(get_db)) -> TokenRead:
    # Login is only credential verification in this minimal version.
    return authenticate_user_and_create_token(db, payload.email, payload.password)


@router.post("/logout", response_model=LogoutRead)
def logout(
    payload: dict = Depends(get_current_access_payload),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
) -> LogoutRead:
    jti = payload.get("jti")
    exp_timestamp = payload.get("exp")
    # If the token has an expiration timestamp, convert it to a datetime object.
    if isinstance(exp_timestamp, int):
        expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    else:
        expires_at = datetime.now(timezone.utc)

    # Revoke the token by storing its JTI in the database. Future requests with this token will be rejected.
    revoke_token(db, jti=jti, token_type="access", expires_at=expires_at)
    return LogoutRead(message="logged out")


@router.post("/reset-password/request", response_model=PasswordResetRequestRead)
def reset_password_request(
    payload: PasswordResetRequest, db=Depends(get_db)
) -> PasswordResetRequestRead:
    return request_password_reset(db, payload.email)


@router.post("/reset-password/confirm", response_model=PasswordResetConfirmRead)
def reset_password_confirm(
    payload: PasswordResetConfirm, db=Depends(get_db)
) -> PasswordResetConfirmRead:
    return confirm_password_reset(db, payload.reset_token, payload.new_password)
