from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_hex

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
