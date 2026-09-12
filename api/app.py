import os

import sqlalchemy
from database import Base, engine, get_db
from fastapi import Depends, FastAPI, HTTPException
from models import User
from schemas import TokenResponse, UserResponse
from security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)

app = FastAPI()

@app.get("/health")
async def health_check():
    """
    Check the health of the application.
    Returns a JSON response indicating that the application is healthy.
    """
    return {"status": "healthy"}

@app.get("/health/db")
async def health_check_db():
    """
    Check the health of the database connection. 
    Returns a JSON response indicating whether the database is connected or disconnected. 
    If an error occurs during the connection attempt, it will return an error message along with the status.
    """
    try:
        engine = sqlalchemy.create_engine(os.getenv("DB_URL"))
        connection = engine.connect()
        connection.execute(sqlalchemy.text("SELECT 1"))
        connection.close()
        return {"db": "connected"}
    except AttributeError as e:
        return {"status": "unhealthy", "db": "disconnected", "error": str(e)}

@app.post("/register", response_model=UserResponse)
async def register_user(username: str, email: str, password: str, db=Depends(get_db)):
    """
    Register a new user.
    This endpoint is a placeholder for user registration functionality.
    """
    hashed_password = hash_password(password)
    new_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=TokenResponse)
async def login_user(email: str, password: str, db=Depends(get_db), response_model=TokenResponse):
    """
    Log in a user.
    This endpoint is a placeholder for user login functionality.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    return {"access_token": access_token, "refresh_token": refresh_token}

Base.metadata.create_all(bind=engine)