from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_check():
    """
    Test the health check endpoint.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    
def test_health_check_db():
    """
    Test the health check database endpoint.
    """
    response = client.get("/health/db")
    assert response.status_code == 200
    json_response = response.json()
    assert "db" in json_response
    assert json_response["db"] == "connected" or json_response["db"] == "disconnected"