from datetime import datetime, timedelta, timezone
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_hex
from typing import Any

import jwt
from config.settings import settings


def hash_password(password: str) -> str:
    # A tiny salted hash implementation so we do not store plain passwords.
    salt = token_hex(settings.password_salt_bytes)
    derived = pbkdf2_hmac(
        settings.password_hash_algorithm,
        password.encode("utf-8"),
        salt.encode("utf-8"),
        settings.password_hash_iterations,
    )
    return f"pbkdf2_{settings.password_hash_algorithm}${salt}${derived.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    algorithm, salt, expected_hash = stored_hash.split("$", 2)
    if algorithm != f"pbkdf2_{settings.password_hash_algorithm}":
        return False
    derived = pbkdf2_hmac(
        settings.password_hash_algorithm,
        password.encode("utf-8"),
        salt.encode("utf-8"),
        settings.password_hash_iterations,
    )
    return compare_digest(derived.hex(), expected_hash)


# The create_access_token function is used to generate a JWT access token for a user. It takes the user's email (subject) and optional extra claims as input. The function creates a payload containing the subject, issued-at time, and expiration time based on the configured access token expiration duration. It then encodes the payload into a JWT using the secret key and algorithm specified in the settings, returning the generated access token as a string.
def create_access_token(
    subject: str, extra_claims: dict[str, Any] | None = None
) -> str:
    now = datetime.now(timezone.utc)
    # The payload must include the subject (the user email) and the issued-at and expiration times.
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),  # issued at
        "exp": int(  # expiration time
            (now + timedelta(minutes=settings.access_token_expire_minutes)).timestamp()
        ),
    }
    if extra_claims:
        payload.update(extra_claims)

    # Encode the payload into a JWT using the secret key and algorithm from settings.
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


# The decode_access_token function is used to decode a JWT access token and verify its signature and claims. It uses the secret key and algorithm specified in the settings to perform the decoding. If the token is valid, it returns the decoded payload as a dictionary. If the token is invalid or expired, it raises an exception.
def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
    )
