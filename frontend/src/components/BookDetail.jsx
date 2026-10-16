/**
 * BookDetail — Expanded view of a single book with reviews.
 *
 * Shows all book metadata, the full list of reviews, and a form
 * to submit a new review. Supports deleting individual reviews.
 */

import { useState, useEffect, useCallback } from 'react';
import { fetchBook, createReview, deleteReview } from '../services/api';

const STATUS_LABELS = {
  want_to_read: 'Want to Read',
  reading: 'Reading',
  finished: 'Finished',
};

function StarRating({ rating, onRate, interactive = false }) {
  return (
    <div className="stars">
      {[1, 2, 3, 4, 5].map((n) => (
        <span
          key={n}
          className={`star ${n <= rating ? 'star--filled' : 'star--empty'}`}
          onClick={interactive ? () => onRate(n) : undefined}
          style={interactive ? { cursor: 'pointer' } : {}}
        >
          ★
        </span>
      ))}
    </div>
  );
}

export default function BookDetail({ bookId, onBack, onShowToast }) {
  const [book, setBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Review form state
  const [reviewerName, setReviewerName] = useState('');
  const [reviewRating, setReviewRating] = useState(0);
  const [reviewComment, setReviewComment] = useState('');
  const [submittingReview, setSubmittingReview] = useState(false);

  const loadBook = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchBook(bookId);
      setBook(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [bookId]);

  useEffect(() => {
    loadBook();
  }, [loadBook]);

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    if (reviewRating === 0) {
      onShowToast('Please select a star rating', 'error');
      return;
    }

    setSubmittingReview(true);
    try {
      await createReview(bookId, {
        reviewer_name: reviewerName.trim(),
        rating: reviewRating,
        comment: reviewComment.trim() || null,
      });
      onShowToast('Review added successfully!', 'success');
      setReviewerName('');
      setReviewRating(0);
      setReviewComment('');
      loadBook(); // Refresh to show the new review
    } catch (err) {
      onShowToast(err.message, 'error');
    } finally {
      setSubmittingReview(false);
    }
  };

  const handleDeleteReview = async (reviewId) => {
    if (!window.confirm('Delete this review?')) return;
    try {
      await deleteReview(reviewId);
      onShowToast('Review deleted', 'success');
      loadBook();
    } catch (err) {
      onShowToast(err.message, 'error');
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner" />
        <span>Loading book details...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <div className="error-banner">⚠️ {error}</div>
        <button className="btn btn-secondary" onClick={onBack}>
          ← Back to Library
        </button>
      </div>
    );
  }

  if (!book) return null;

  return (
    <div>
      <div className="book-detail">
        <div className="book-detail__back">
          <button className="btn btn-secondary btn-sm" onClick={onBack}>
            ← Back to Library
          </button>
        </div>

        <h1 className="book-detail__title">{book.title}</h1>
        <p className="book-detail__author">by {book.author}</p>

        <div className="book-detail__info">
          <span className={`status-badge status-badge--${book.status}`}>
            {STATUS_LABELS[book.status]}
          </span>
          {book.isbn && (
            <span className="book-card__isbn">ISBN: {book.isbn}</span>
          )}
          {book.page_count && (
            <span className="book-card__pages">{book.page_count} pages</span>
          )}
        </div>

        {book.description && (
          <p className="book-detail__description">{book.description}</p>
        )}
      </div>

      {/* Reviews Section */}
      <div className="book-detail" style={{ marginTop: '20px' }}>
        <h2 style={{ marginBottom: '20px', fontSize: '1.2rem', fontWeight: 700 }}>
          💬 Reviews ({book.reviews?.length || 0})
        </h2>

        {/* Review List */}
        {book.reviews && book.reviews.length > 0 ? (
          <div className="reviews-section">
            {book.reviews.map((review) => (
              <div key={review.id} className="review-item">
                <div className="review-item__header">
                  <div>
                    <span className="review-item__author">
                      {review.reviewer_name}
                    </span>
                    <div style={{ marginTop: '4px' }}>
                      <StarRating rating={review.rating} />
                    </div>
                  </div>
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDeleteReview(review.id)}
                  >
                    🗑️
                  </button>
                </div>
                {review.comment && (
                  <p className="review-item__comment">{review.comment}</p>
                )}
                <p className="review-item__date">
                  {new Date(review.created_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: 'var(--text-muted)', marginBottom: '20px' }}>
            No reviews yet. Be the first to review this book!
          </p>
        )}

        {/* Add Review Form */}
        <div style={{ marginTop: '24px', paddingTop: '24px', borderTop: '1px solid var(--border-subtle)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '16px' }}>
            ✍️ Write a Review
          </h3>
          <form onSubmit={handleSubmitReview}>
            <div className="form-group">
              <label htmlFor="reviewer_name">Your Name *</label>
              <input
                id="reviewer_name"
                type="text"
                value={reviewerName}
                onChange={(e) => setReviewerName(e.target.value)}
                placeholder="Your name"
                required
                maxLength={100}
              />
            </div>

            <div className="form-group">
              <label>Rating *</label>
              <StarRating
                rating={reviewRating}
                onRate={setReviewRating}
                interactive
              />
            </div>

            <div className="form-group">
              <label htmlFor="review_comment">Comment</label>
              <textarea
                id="review_comment"
                value={reviewComment}
                onChange={(e) => setReviewComment(e.target.value)}
                placeholder="Share your thoughts about this book..."
                maxLength={2000}
                rows={3}
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={submittingReview}
            >
              {submittingReview ? 'Submitting...' : 'Submit Review'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
