from fastapi import APIRouter, Depends

from infrastructure.database.session import get_db
from schemas.user import UserLogin, UserRead
from services.user_service import authenticate_user

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/login", response_model=UserRead)
def login(payload: UserLogin, db = Depends(get_db)) -> UserRead:
	# Login is only credential verification in this minimal version.
	return authenticate_user(db, payload.email, payload.password)
