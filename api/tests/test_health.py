"""Tests for the health-check endpoints in ``app.py``."""

import pytest


def test_health_check_returns_healthy(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_health_check_db_reports_connected(client):
    """With a reachable database (the test SQLite file) the endpoint reports it."""
    response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {"db": "connected"}
