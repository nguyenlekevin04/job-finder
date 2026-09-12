"""Tests for password hashing and JWT token creation in ``security.py``."""

import calendar
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from jose import jwt
from jose.exceptions import JWTError
from security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    JWT_REFRESH_SECRET_KEY,
    JWT_SECRET_KEY,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_refresh_token,
    hash_password,
    pwd_context,
    verify_password,
)


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


def test_verify_password_accepts_correct_password():
    hashed = hash_password("correct-horse-battery-staple")

    assert verify_password("correct-horse-battery-staple", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("correct-horse-battery-staple")

    assert verify_password("wrong-password", hashed) is False


def test_create_access_token_returns_jwt_with_correct_subject():
    token = create_access_token(subject=42)

    decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "42"


def test_create_access_token_sets_expiry_30_minutes_out():
    # Mocked datetime.now so the expiry check isn't time-dependent or flaky.
    fixed_now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with patch("security.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_now
        token = create_access_token(subject=1)

    # verify_exp disabled: fixed_now is a fixed point in the past relative to
    # the real clock, so the claim would otherwise fail expiry validation
    # before we get to check its value.
    decoded = jwt.decode(
        token, JWT_SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False}
    )
    expected_exp = calendar.timegm(
        (fixed_now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).utctimetuple()
    )
    assert decoded["exp"] == expected_exp


def test_create_refresh_token_returns_jwt_with_correct_subject():
    token = create_refresh_token(subject=42)

    decoded = jwt.decode(token, JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "42"


def test_create_refresh_token_sets_expiry_7_days_out():
    fixed_now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with patch("security.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_now
        token = create_refresh_token(subject=1)

    decoded = jwt.decode(
        token, JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False}
    )
    expected_exp = calendar.timegm(
        (fixed_now + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)).utctimetuple()
    )
    assert decoded["exp"] == expected_exp


def test_access_token_cannot_be_decoded_with_refresh_secret():
    """Access and refresh tokens must be signed with distinct secrets so a
    leaked refresh token can't be replayed as an access token or vice versa."""
    access_token = create_access_token(subject=1)

    with pytest.raises(JWTError):
        jwt.decode(access_token, JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM])


def test_expired_access_token_is_rejected_on_decode():
    with patch("security.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2020, 1, 1, tzinfo=timezone.utc)
        expired_token = create_access_token(subject=1)

    with pytest.raises(JWTError):
        jwt.decode(expired_token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
