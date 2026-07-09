from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from infrastructure.database.session import get_db
from jwt import PyJWTError
from models.user import User
from services.user_service import get_user_by_email
from sqlalchemy.orm import Session
from utils.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


# This dependency is used to get the current authenticated user from the request.
# It checks for a valid Bearer token in the Authorization header, decodes it,
# and retrieves the corresponding user from the database.
# If any step fails (missing token, invalid token, or user not found), it raises an HTTP 401 Unauthorized error.
def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    # This dependency is the gatekeeper for protected endpoints.
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

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        )

    user = get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        )

    return user
