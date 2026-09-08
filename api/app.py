import os

import sqlalchemy
from fastapi import FastAPI

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