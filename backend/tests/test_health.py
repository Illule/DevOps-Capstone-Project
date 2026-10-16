"""
Tests for the health check endpoint.

Verifies:
  - The /api/health endpoint returns 200
  - The response body contains status and database fields
"""


def test_health_check_returns_200(client):
    """Health endpoint returns 200 when the database is reachable."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "healthy"
    assert data["service"] == "bookshelf-api"

    # Also verify direct /health endpoint
    direct_response = client.get("/health")
    assert direct_response.status_code == 200
    assert direct_response.json()["status"] == "healthy"


def test_root_endpoint(client):
    """Root endpoint returns service information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "BookShelf"
    assert "docs" in data
