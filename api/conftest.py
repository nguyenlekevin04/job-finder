import os
import tempfile

# ``database.py`` reads ``DATABASE_URL`` at import time and raises if it is
# missing, and ``app.py`` reads ``DB_URL`` for its DB health check. Both have to
# be set before anything under test is imported, so it happens here at module
# top. A throwaway SQLite file keeps the suite isolated from any real database.
_DB_FD, _DB_PATH = tempfile.mkstemp(suffix=".sqlite3")
os.close(_DB_FD)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_DB_PATH}")
os.environ.setdefault("DB_URL", os.environ["DATABASE_URL"])

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import app  # noqa: E402
from database import Base, SessionLocal, engine  # noqa: E402
from models import User  # noqa: E402, F401  -- imported so the table is registered on Base.metadata


@pytest.fixture(scope="session", autouse=True)
def _schema():
    """Create the schema once for the whole run, drop it and delete the file after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    try:
        os.remove(_DB_PATH)
    except OSError:
        pass


@pytest.fixture(autouse=True)
def _clean_tables():
    """Every test starts against empty tables."""
    yield
    session = SessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
    finally:
        session.close()


@pytest.fixture
def db_session():
    """A plain SQLAlchemy session bound to the test database."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    """A FastAPI test client. Server-side exceptions are re-raised into the test."""
    with TestClient(app) as test_client:
        yield test_client
