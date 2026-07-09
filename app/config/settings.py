from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Centralize values that may change during development.
    # Pydantic reads app/.env and environment variables, so this stays minimal.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    message_min_length: int = 1
    message_max_length: int = 280
    password_min_length: int = 6
    password_max_length: int = 72
    password_hash_iterations: int = 100_000
    password_salt_bytes: int = 16
    database_url: str
    password_hash_algorithm: str
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int = 30


settings = Settings()
