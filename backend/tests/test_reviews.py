"""
Tests for the Reviews and Stats API endpoints.

Covers:
  - POST /api/books/{id}/reviews — creating reviews
  - GET /api/books/{id}/reviews — listing reviews
  - DELETE /api/reviews/{id} — deleting reviews
  - GET /api/stats — dashboard statistics
  - Edge cases: invalid rating, nonexistent book
"""


class TestCreateReview:
    """Tests for POST /api/books/{id}/reviews."""

    def test_create_review_success(self, client, sample_book):
        """Creating a review with valid data returns 201."""
        response = client.post(
            f"/api/books/{sample_book['id']}/reviews",
            json={
                "reviewer_name": "Bob",
                "rating": 4,
                "comment": "Very informative!",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["reviewer_name"] == "Bob"
        assert data["rating"] == 4
        assert data["book_id"] == sample_book["id"]

    def test_create_review_invalid_rating(self, client, sample_book):
        """Creating a review with rating > 5 returns 422."""
        response = client.post(
            f"/api/books/{sample_book['id']}/reviews",
            json={
                "reviewer_name": "Eve",
                "rating": 6,
            },
        )
        assert response.status_code == 422

    def test_create_review_rating_zero(self, client, sample_book):
        """Creating a review with rating 0 returns 422."""
        response = client.post(
            f"/api/books/{sample_book['id']}/reviews",
            json={
                "reviewer_name": "Eve",
                "rating": 0,
            },
        )
        assert response.status_code == 422

    def test_create_review_nonexistent_book(self, client):
        """Creating a review for a nonexistent book returns 404."""
        response = client.post(
            "/api/books/99999/reviews",
            json={
                "reviewer_name": "Ghost",
                "rating": 3,
            },
        )
        assert response.status_code == 404


class TestListReviews:
    """Tests for GET /api/books/{id}/reviews."""

    def test_list_reviews_success(self, client, sample_book_with_review):
        """Listing reviews for a book with reviews returns them."""
        book_id = sample_book_with_review["id"]
        response = client.get(f"/api/books/{book_id}/reviews")
        assert response.status_code == 200
        reviews = response.json()
        assert len(reviews) >= 1
        assert reviews[0]["reviewer_name"] == "Alice"


class TestDeleteReview:
    """Tests for DELETE /api/reviews/{id}."""

    def test_delete_review_success(self, client, sample_book_with_review):
        """Deleting a review returns 204."""
        review_id = sample_book_with_review["reviews"][0]["id"]
        response = client.delete(f"/api/reviews/{review_id}")
        assert response.status_code == 204

    def test_delete_review_not_found(self, client):
        """Deleting a nonexistent review returns 404."""
        response = client.delete("/api/reviews/99999")
        assert response.status_code == 404


class TestStats:
    """Tests for GET /api/stats."""

    def test_stats_empty_database(self, client):
        """Stats with no books returns all zeros."""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_books"] == 0
        assert data["want_to_read"] == 0
        assert data["reading"] == 0
        assert data["finished"] == 0
        assert data["total_reviews"] == 0
        assert data["average_rating"] is None

    def test_stats_with_data(self, client, sample_book_with_review):
        """Stats reflect actual book and review data."""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_books"] == 1
        assert data["reading"] == 1  # sample_book has status='reading'
        assert data["total_reviews"] == 1
        assert data["average_rating"] == 5.0
