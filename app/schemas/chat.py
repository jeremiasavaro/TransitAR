from datetime import datetime

from config.settings import settings
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatCreate(BaseModel):
    # Input schema for the public endpoint.
    # Pydantic uses this class to validate the JSON body before the service runs.
    message: str = Field(
        min_length=settings.message_min_length,
        max_length=settings.message_max_length,
    )

    @field_validator("message")
    @classmethod
    def strip_message(cls, value: str) -> str:
        # field_validator runs automatically after Pydantic reads the raw input value.
        normalized = value.strip()
        if not normalized:
            raise ValueError("message cannot be empty")
        return normalized


class ChatRead(BaseModel):
    # Response schema returned after persistence.
    # from_attributes=True lets Pydantic read fields from a SQLAlchemy model object.
    model_config = ConfigDict(from_attributes=True)

    id: int
    message: str
    created_at: datetime
