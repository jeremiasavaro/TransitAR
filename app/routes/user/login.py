from fastapi import APIRouter, Depends
from infrastructure.database.session import get_db
from schemas.user import TokenRead, UserLogin
from services.user_service import authenticate_user_and_create_token

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/login", response_model=TokenRead)
def login(payload: UserLogin, db=Depends(get_db)) -> TokenRead:
    # Login is only credential verification in this minimal version.
    return authenticate_user_and_create_token(db, payload.email, payload.password)
