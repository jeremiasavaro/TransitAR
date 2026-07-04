from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    # Every SQLAlchemy model in the app inherits from this class.
    # That is how SQLAlchemy collects the table definitions into metadata.
    pass
