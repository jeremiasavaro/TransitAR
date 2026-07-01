from models.chat_history import ChatHistory
from schemas.chat import ChatRead
from sqlalchemy.orm import Session
from utils.text import normalize_message


def create_chat_message(db: Session, message: str) -> ChatRead:
    # Build the SQLAlchemy model instance in memory first.
    # At this point nothing is in the database yet.
    chat_history = ChatHistory(message=normalize_message(message))
    # marks the object to be inserted on the next commit.
    db.add(chat_history)
    # sends the INSERT to the database.
    db.commit()
    # reloads generated values like id and created_at from the DB.
    db.refresh(chat_history)
    # Convert the ORM object into the public response schema.
    return ChatRead.model_validate(chat_history)

def list_chat_messages(db: Session) -> list[ChatHistory]:
    return db.query(ChatHistory).order_by(ChatHistory.created_at).all()