"""Tests for the ``User`` ORM model in ``models.py``."""

import pytest
from sqlalchemy.exc import IntegrityError

from models import User


def test_user_table_shape():
    assert User.__tablename__ == "users"
    columns = {c.name for c in User.__table__.columns}
    assert columns == {"id", "username", "email", "hashed_password"}


def test_user_can_be_persisted_and_read_back(db_session):
    user = User(username="alice", email="alice@example.com", hashed_password="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None

    fetched = db_session.query(User).filter_by(username="alice").one()
    assert fetched.email == "alice@example.com"
    assert fetched.hashed_password == "x"


def test_username_is_unique(db_session):
    db_session.add(User(username="bob", email="bob1@example.com", hashed_password="x"))
    db_session.commit()

    db_session.add(User(username="bob", email="bob2@example.com", hashed_password="x"))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_email_is_unique(db_session):
    db_session.add(User(username="carol", email="dup@example.com", hashed_password="x"))
    db_session.commit()

    db_session.add(User(username="carol2", email="dup@example.com", hashed_password="x"))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
