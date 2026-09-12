import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DB_URL")

if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Get a database session.
    This function is a dependency that can be used in FastAPI routes to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()