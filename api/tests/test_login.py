"""Tests for the ``POST /login`` endpoint in ``app.py``."""

from jose import jwt
from security import ALGORITHM, JWT_REFRESH_SECRET_KEY, JWT_SECRET_KEY

VALID = {"username": "loginuser", "email": "loginuser@example.com", "password": "hunter2"}


def _register(client, user=VALID):
    response = client.post("/register", params=user)
    assert response.status_code == 200
    return response.json()


def test_login_returns_tokens_for_correct_credentials(client):
    _register(client)

    response = client.post(
        "/login", params={"email": VALID["email"], "password": VALID["password"]}
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_login_access_token_encodes_the_user_id(client):
    user = _register(client)

    response = client.post(
        "/login", params={"email": VALID["email"], "password": VALID["password"]}
    )

    decoded = jwt.decode(response.json()["access_token"], JWT_SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == str(user["id"])


def test_login_refresh_token_is_signed_with_the_refresh_secret(client):
    _register(client)

    response = client.post(
        "/login", params={"email": VALID["email"], "password": VALID["password"]}
    )

    # Must decode with the refresh secret, proving access and refresh tokens
    # are not interchangeable.
    decoded = jwt.decode(
        response.json()["refresh_token"], JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM]
    )
    assert decoded["sub"] is not None


def test_login_returns_401_for_wrong_password(client):
    _register(client)

    response = client.post("/login", params={"email": VALID["email"], "password": "wrong-pw"})

    assert response.status_code == 401


def test_login_returns_401_for_unknown_email(client):
    response = client.post(
        "/login", params={"email": "nobody@example.com", "password": "hunter2"}
    )

    assert response.status_code == 401


def test_login_error_message_does_not_reveal_whether_email_exists(client):
    """A wrong password and an unknown email must return the same error
    detail, otherwise the endpoint leaks which emails are registered."""
    _register(client)

    wrong_password = client.post(
        "/login", params={"email": VALID["email"], "password": "wrong-pw"}
    )
    unknown_email = client.post(
        "/login", params={"email": "nobody@example.com", "password": "hunter2"}
    )

    assert wrong_password.json()["detail"] == unknown_email.json()["detail"]


def test_login_response_never_contains_the_password_hash(client):
    _register(client)

    response = client.post(
        "/login", params={"email": VALID["email"], "password": VALID["password"]}
    )

    assert "hashed_password" not in response.text
    assert VALID["password"] not in response.text
