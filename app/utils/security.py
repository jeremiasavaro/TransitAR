from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_hex


def hash_password(password: str) -> str:
    # A tiny salted hash implementation so we do not store plain passwords.
    salt = token_hex(16)
    derived = pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    )
    return f"pbkdf2_sha256${salt}${derived.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    algorithm, salt, expected_hash = stored_hash.split("$", 2)
    if algorithm != "pbkdf2_sha256":
        return False
    derived = pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    )
    return compare_digest(derived.hex(), expected_hash)
