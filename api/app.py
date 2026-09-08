import os

from fastapi import FastAPI
import uvicorn
import sqlalchemy
import os

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/health/db")
async def health_check_db():
    try:
        engine = sqlalchemy.create_engine(os.getenv("DB_URL"))
        connection = engine.connect()
        sqlalchemy.text("SELECT 1").execute(connection)
        connection.close()
        return {"db": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "db": "disconnected", "error": str(e)}