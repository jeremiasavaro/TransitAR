from datetime import datetime

from config.settings import settings
from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserRegister(BaseModel):
    # Input schema for register.
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(
        min_length=settings.password_min_length,
        max_length=settings.password_max_length,
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        # Keep the example simple: trim spaces and force lowercase.
        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("invalid email")
        return normalized


class UserLogin(BaseModel):
    # Input schema for login.
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(
        min_length=settings.password_min_length,
        max_length=settings.password_max_length,
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserRead(BaseModel):
    # Public response schema. Notice that the password hash is not exposed.
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    created_at: datetime


class TokenRead(BaseModel):
    # Response schema returned by login.
    access_token: str
    token_type: str = "bearer"


class LogoutRead(BaseModel):
    message: str


class PasswordResetRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class PasswordResetRequestRead(BaseModel):
    # In a real app this token should be sent by email.
    reset_token: str | None = None
    message: str


class PasswordResetConfirm(BaseModel):
    reset_token: str
    new_password: str = Field(
        min_length=settings.password_min_length,
        max_length=settings.password_max_length,
    )


class PasswordResetConfirmRead(BaseModel):
    message: str
