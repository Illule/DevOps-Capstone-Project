"""
Test fixtures and configuration.

Creates an isolated test database using SQLite in-memory so tests:
  - Never touch the production PostgreSQL database
  - Run fast (no network I/O)
  - Are fully isolated (fresh DB per test session)

The `client` fixture overrides FastAPI's `get_db` dependency to use
the test database session instead of the production one.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# In-memory SQLite database for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Yield a test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the dependency globally for all tests
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """
    Create all tables before each test and drop them after.

    This ensures complete isolation between tests — no leftover data
    from previous tests can cause false passes or false failures.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Provide a FastAPI TestClient for making HTTP requests."""
    return TestClient(app)


@pytest.fixture
def sample_book(client):
    """Create and return a sample book for tests that need existing data."""
    response = client.post(
        "/api/books",
        json={
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "isbn": "9780132350884",
            "status": "reading",
            "page_count": 464,
            "description": "A Handbook of Agile Software Craftsmanship",
        },
    )
    return response.json()


@pytest.fixture
def sample_book_with_review(client, sample_book):
    """Create a book with a review attached."""
    client.post(
        f"/api/books/{sample_book['id']}/reviews",
        json={
            "reviewer_name": "Alice",
            "rating": 5,
            "comment": "Excellent book on writing clean code!",
        },
    )
    # Refresh the book to include reviews
    response = client.get(f"/api/books/{sample_book['id']}")
    return response.json()
