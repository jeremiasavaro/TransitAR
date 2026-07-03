from fastapi import APIRouter, Depends
from infrastructure.database.session import get_db
from schemas.chat import ChatCreate, ChatRead
from services.chat_service import create_chat_message, list_chat_messages
from sqlalchemy.orm import Session

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatRead, status_code=201)
def chat(payload: ChatCreate, db: Session = Depends(get_db)) -> ChatRead:
    # The route stays thin: validation happens in the schema and persistence in the service.
    # Since the Payload is a ChatCreate, FastAPI builds a 'ChatCreate' instance from the JSON body
    # and validates it before this function is called.
    return create_chat_message(db, payload.message)

@router.get("/", response_model=list[ChatRead])
def list_chats(db: Session = Depends(get_db)) -> list[ChatRead]:
    chats = list_chat_messages(db)
    return [ChatRead.model_validate(chat) for chat in chats]