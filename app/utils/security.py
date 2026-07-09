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


# Generic token creation function
def _create_token(
    subject: str,
    token_type: str,
    expires_minutes: int,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    jti = token_hex(16)  # Generate a unique identifier for the token (JTI)
    # Create the payload with standard claims and any extra claims provided
    payload: dict[str, Any] = {
        "sub": subject,
        "jti": jti,  # Unique identifier for the tokenS
        "iss": settings.jwt_issuer,  # Issuer claim
        "aud": settings.jwt_audience,  # Audience claim
        "typ": token_type,  # Token type claim
        "iat": int(now.timestamp()),  # Issued At
        "nbf": int(now.timestamp()),  # Not Before
        "exp": int(
            (now + timedelta(minutes=expires_minutes)).timestamp()
        ),  # Expiration
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


# Generic token decoding function
def _decode_token(token: str, expected_type: str) -> dict[str, Any]:
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        options={
            "require": ["sub", "jti", "iss", "aud", "typ", "iat", "nbf", "exp"],
        },
    )

    if payload.get("typ") != expected_type:
        raise jwt.InvalidTokenError("invalid token type")

    return payload


# Create token for user access
def create_access_token(
    subject: str, extra_claims: dict[str, Any] | None = None
) -> str:
    return _create_token(
        subject=subject,
        token_type="access",
        expires_minutes=settings.access_token_expire_minutes,
        extra_claims=extra_claims,
    )


# Create token for password reset
def create_reset_token(subject: str) -> str:
    return _create_token(
        subject=subject,
        token_type="reset_password",
        expires_minutes=settings.reset_token_expire_minutes,
    )


# Decode access token function
def decode_access_token(token: str) -> dict[str, Any]:
    return _decode_token(token, expected_type="access")


# Decode reset token function
def decode_reset_token(token: str) -> dict[str, Any]:
    return _decode_token(token, expected_type="reset_password")
