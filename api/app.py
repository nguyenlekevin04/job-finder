import os

import sqlalchemy
from fastapi import FastAPI, Depends
from security import hash_password
from database import get_db, Base, engine
from models import User

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

@app.post("/register")
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
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email}

Base.metadata.create_all(bind=engine)