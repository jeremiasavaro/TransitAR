from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from infrastructure.database.session import get_db
from jwt import PyJWTError
from models.user import User
from services.user_service import get_user_by_id, is_token_revoked
from sqlalchemy.orm import Session
from utils.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_access_payload(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict:
    """
    Retrieve and validate the payload from the current access token.
    This function checks for the presence of a Bearer token in the request,
    decodes it, and verifies that it hasn't been revoked. If the token is valid,
    it returns the payload as a dictionary. If not, raise a 401.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing token",
        )

    try:
        payload = decode_access_token(credentials.credentials)
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        )

    jti = payload.get("jti")
    if not jti or is_token_revoked(db, jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        )

    return payload


def get_current_user(
    payload: dict = Depends(get_current_access_payload),
    db: Session = Depends(get_db),
) -> User:
    """
    Retrieve the current user based on the payload from the access token.
    This function extracts the user ID from the token payload, fetches the corresponding
    user from the database, and returns the User object. If the user does not exist,
    it raises a 401 Code.
    """
    raw_user_id = payload.get("sub")
    try:
        user_id = int(raw_user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        )

    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        )

    return user
