"""Tests for password hashing in ``security.py``."""

from security import hash_password, pwd_context


def test_hash_is_not_plaintext():
    hashed = hash_password("s3cret-pw")

    assert hashed != "s3cret-pw"
    assert isinstance(hashed, str)


def test_hash_uses_bcrypt():
    hashed = hash_password("s3cret-pw")

    assert hashed.startswith(("$2a$", "$2b$", "$2y$"))
    assert pwd_context.identify(hashed) == "bcrypt"


def test_hash_is_verifiable():
    hashed = hash_password("correct horse battery staple")

    assert pwd_context.verify("correct horse battery staple", hashed) is True
    assert pwd_context.verify("wrong password", hashed) is False


def test_hash_is_salted():
    """Hashing the same password twice yields different digests."""
    assert hash_password("same-input") != hash_password("same-input")
