from pydantic import BaseModel


class Settings(BaseModel):
    # Centralize values that may change during development.
    database_url: str = "sqlite:///./transitar.db"
    message_min_length: int = 1
    message_max_length: int = 280


settings = Settings()
