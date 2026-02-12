"""
Tests for FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from database import init_db, engine, Base
from sqlalchemy.orm import Session


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    Base.metadata.create_all(bind=engine)
    yield Session(bind=engine)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_generate_article_endpoint(client):
    """Test article generation endpoint."""
    response = client.post("/generate", json={
        "topic": "test topic",
        "target_word_count": 1500,
        "language": "en"
    })
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert "status" in data
    assert data["status"] == "pending"


def test_generate_article_validation(client):
    """Test article generation validation."""
    # Empty topic
    response = client.post("/generate", json={
        "topic": "",
        "target_word_count": 1500
    })
    assert response.status_code == 422
    
    # Invalid word count
    response = client.post("/generate", json={
        "topic": "test",
        "target_word_count": 100
    })
    assert response.status_code == 422


def test_get_job_status_not_found(client):
    """Test getting status of non-existent job."""
    response = client.get("/jobs/non-existent-id")
    assert response.status_code == 404


def test_get_job_result_not_found(client):
    """Test getting result of non-existent job."""
    response = client.get("/jobs/non-existent-id/result")
    assert response.status_code == 404

