from collections.abc import Generator

from config.settings import settings
from infrastructure.database.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# create_engine() builds the low-level connection factory.
# The same engine is reused by every request in this backend process.
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

# sessionmaker() builds new Session objects from the shared engine.
# We use one Session per request so each endpoint work is isolated.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    # FastAPI depends on this generator to open a session, hand it to the route,
    # and guarantee the close() happens after the request finishes.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # create_all() reads all registered models from Base.metadata
    # and creates the missing tables in the database.
    Base.metadata.create_all(bind=engine)
