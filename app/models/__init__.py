from models import chat_history, revoked_token, user

# Keep model modules imported so SQLAlchemy registers all tables in Base.metadata.
__all__ = ["chat_history", "revoked_token", "user"]
