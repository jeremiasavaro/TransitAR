from fastapi import APIRouter, Depends

from infrastructure.database.session import get_db
from schemas.user import UserRead, UserRegister
from services.user_service import register_user

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(payload: UserRegister, db = Depends(get_db)) -> UserRead:
	# The route only connects the HTTP body to the service.
	return register_user(db, payload.email, payload.password)
