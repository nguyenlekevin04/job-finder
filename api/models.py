import sqlalchemy
from database import Base

class User(Base):
    """
    A user in the system.
    """
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    username = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)