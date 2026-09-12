"""Tests for the session helper and import-time guard in ``database.py``."""

import inspect
import os
import subprocess
import sys

import database
import pytest
import sqlalchemy
from sqlalchemy.orm import Session


def test_get_db_is_a_generator_function():
    assert inspect.isgeneratorfunction(database.get_db)


def test_get_db_yields_a_session_and_closes_it():
    gen = database.get_db()
    session = next(gen)

    assert isinstance(session, Session)

    # Exhausting the generator runs the ``finally`` block that closes the session.
    with pytest.raises(StopIteration):
        next(gen)


def test_get_db_yields_a_usable_session():
    gen = database.get_db()
    session = next(gen)
    try:
        result = session.execute(sqlalchemy.text("SELECT 1")).scalar()
        assert result == 1
    finally:
        gen.close()


def test_import_without_database_url_raises_runtime_error():
    """Importing the module with no ``DB_URL`` must fail loudly."""
    env = {k: v for k, v in os.environ.items() if k != "DB_URL"}
    env["PYTHONPATH"] = os.path.dirname(os.path.abspath(database.__file__))

    proc = subprocess.run(
        [sys.executable, "-c", "import database"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert proc.returncode != 0
    assert "DATABASE_URL is not set" in proc.stderr
