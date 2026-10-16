"""
Tests for the Books API endpoints.

Covers:
  - POST /api/books — creation with validation
  - GET /api/books — listing and filtering
  - GET /api/books/{id} — detail retrieval
  - PUT /api/books/{id} — updates
  - DELETE /api/books/{id} — deletion with cascade
  - Edge cases: 404, duplicate ISBN, invalid data
"""


class TestCreateBook:
    """Tests for POST /api/books."""

    def test_create_book_success(self, client):
        """Creating a book with valid data returns 201."""
        response = client.post(
            "/api/books",
            json={
                "title": "The Pragmatic Programmer",
                "author": "David Thomas",
                "isbn": "9780135957059",
                "status": "want_to_read",
                "page_count": 352,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "The Pragmatic Programmer"
        assert data["author"] == "David Thomas"
        assert data["isbn"] == "9780135957059"
        assert data["status"] == "want_to_read"
        assert data["id"] is not None

    def test_create_book_missing_title(self, client):
        """Creating a book without a title returns 422 (validation error)."""
        response = client.post(
            "/api/books",
            json={"author": "Someone"},
        )
        assert response.status_code == 422

    def test_create_book_duplicate_isbn(self, client, sample_book):
        """Creating a book with a duplicate ISBN returns 409."""
        response = client.post(
            "/api/books",
            json={
                "title": "Another Book",
                "author": "Another Author",
                "isbn": sample_book["isbn"],  # same ISBN
            },
        )
        assert response.status_code == 409

    def test_create_book_defaults_to_want_to_read(self, client):
        """Books default to 'want_to_read' status when not specified."""
        response = client.post(
            "/api/books",
            json={"title": "New Book", "author": "Author"},
        )
        assert response.status_code == 201
        assert response.json()["status"] == "want_to_read"


class TestListBooks:
    """Tests for GET /api/books."""

    def test_list_books_empty(self, client):
        """Listing books with no data returns an empty list."""
        response = client.get("/api/books")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_books_with_data(self, client, sample_book):
        """Listing books returns existing books."""
        response = client.get("/api/books")
        assert response.status_code == 200
        books = response.json()
        assert len(books) == 1
        assert books[0]["title"] == sample_book["title"]

    def test_filter_books_by_status(self, client, sample_book):
        """Filtering by status returns only matching books."""
        # sample_book has status="reading"
        response = client.get("/api/books?status=reading")
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = client.get("/api/books?status=finished")
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_search_books_by_title(self, client, sample_book):
        """Searching by title substring finds matching books."""
        response = client.get("/api/books?search=Clean")
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = client.get("/api/books?search=Nonexistent")
        assert response.status_code == 200
        assert len(response.json()) == 0


class TestGetBook:
    """Tests for GET /api/books/{id}."""

    def test_get_book_success(self, client, sample_book):
        """Getting a book by ID returns 200 with details and reviews."""
        response = client.get(f"/api/books/{sample_book['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_book["title"]
        assert "reviews" in data

    def test_get_book_not_found(self, client):
        """Getting a nonexistent book returns 404."""
        response = client.get("/api/books/99999")
        assert response.status_code == 404


class TestUpdateBook:
    """Tests for PUT /api/books/{id}."""

    def test_update_book_success(self, client, sample_book):
        """Updating a book's status returns 200."""
        response = client.put(
            f"/api/books/{sample_book['id']}",
            json={"status": "finished"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "finished"

    def test_update_book_not_found(self, client):
        """Updating a nonexistent book returns 404."""
        response = client.put(
            "/api/books/99999",
            json={"title": "Updated"},
        )
        assert response.status_code == 404


class TestDeleteBook:
    """Tests for DELETE /api/books/{id}."""

    def test_delete_book_success(self, client, sample_book):
        """Deleting a book returns 204 and removes it from the database."""
        response = client.delete(f"/api/books/{sample_book['id']}")
        assert response.status_code == 204

        # Verify deletion
        response = client.get(f"/api/books/{sample_book['id']}")
        assert response.status_code == 404

    def test_delete_book_not_found(self, client):
        """Deleting a nonexistent book returns 404."""
        response = client.delete("/api/books/99999")
        assert response.status_code == 404
