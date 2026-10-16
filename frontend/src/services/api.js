/**
 * API Service Layer
 *
 * Centralizes all backend API calls. In development, Vite proxies
 * /api to the FastAPI backend. In production (Docker/K8s), Nginx
 * or Ingress handles the routing.
 */

const API_BASE = '/api';

/**
 * Generic fetch wrapper with error handling.
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;

  const config = {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  };

  const response = await fetch(url, config);

  // Handle 204 No Content (delete responses)
  if (response.status === 204) {
    return null;
  }

  // Parse JSON response, handling non-JSON error bodies gracefully
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error(`Request failed with status ${response.status}`);
  }

  // Throw on error responses
  if (!response.ok) {
    const message = data.detail || `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return data;
}

// ---------------------------------------------------------------------------
// Books API
// ---------------------------------------------------------------------------

export async function fetchBooks(status = null, search = null) {
  const params = new URLSearchParams();
  if (status) params.set('status', status);
  if (search) params.set('search', search);
  const query = params.toString();
  return request(`/books${query ? `?${query}` : ''}`);
}

export async function fetchBook(id) {
  return request(`/books/${id}`);
}

export async function createBook(bookData) {
  return request('/books', {
    method: 'POST',
    body: JSON.stringify(bookData),
  });
}

export async function updateBook(id, bookData) {
  return request(`/books/${id}`, {
    method: 'PUT',
    body: JSON.stringify(bookData),
  });
}

export async function deleteBook(id) {
  return request(`/books/${id}`, {
    method: 'DELETE',
  });
}

// ---------------------------------------------------------------------------
// Reviews API
// ---------------------------------------------------------------------------

export async function fetchReviews(bookId) {
  return request(`/books/${bookId}/reviews`);
}

export async function createReview(bookId, reviewData) {
  return request(`/books/${bookId}/reviews`, {
    method: 'POST',
    body: JSON.stringify(reviewData),
  });
}

export async function deleteReview(reviewId) {
  return request(`/reviews/${reviewId}`, {
    method: 'DELETE',
  });
}

// ---------------------------------------------------------------------------
// Stats API
// ---------------------------------------------------------------------------

export async function fetchStats() {
  return request('/stats');
}

// ---------------------------------------------------------------------------
// Health API
// ---------------------------------------------------------------------------

export async function fetchHealth() {
  return request('/health');
}
