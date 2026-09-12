"""Tests for the ``POST /register`` endpoint in ``app.py``."""

import pytest
from models import User
from sqlalchemy.exc import IntegrityError

VALID = {"username": "newuser", "email": "newuser@example.com", "password": "hunter2"}


def test_register_returns_public_user_fields(client):
    response = client.post("/register", params=VALID)

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "newuser"
    assert body["email"] == "newuser@example.com"
    assert isinstance(body["id"], int)
    # The password (hashed or not) must never be echoed back.
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_persists_a_hashed_password(client, db_session):
    client.post("/register", params=VALID)

    user = db_session.query(User).filter_by(username="newuser").one()
    assert user.hashed_password != VALID["password"]
    assert user.hashed_password.startswith(("$2a$", "$2b$", "$2y$"))


def test_register_requires_all_query_params(client):
    response = client.post("/register", params={"username": "x"})

    assert response.status_code == 422


def test_register_rejects_duplicate_username(client):
    assert client.post("/register", params=VALID).status_code == 200

    duplicate = {**VALID, "email": "other@example.com"}
    # NOTE: the endpoint does not yet handle this; the unique constraint surfaces
    # as an unhandled IntegrityError. Ideally this should become a 409 response.
    with pytest.raises(IntegrityError):
        client.post("/register", params=duplicate)
