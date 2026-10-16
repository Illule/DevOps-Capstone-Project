/**
 * BookCard — Displays a single book as a card in the grid.
 *
 * Shows title, author, status badge, description preview,
 * and action buttons for edit, view reviews, and delete.
 */

const STATUS_LABELS = {
  want_to_read: 'Want to Read',
  reading: 'Reading',
  finished: 'Finished',
};

export default function BookCard({ book, onEdit, onDelete, onViewDetail }) {
  return (
    <div className="book-card">
      <div className="book-card__color-bar" />
      <div className="book-card__content">
        <div className="book-card__header">
          <h3 className="book-card__title">{book.title}</h3>
          <span className={`status-badge status-badge--${book.status}`}>
            {STATUS_LABELS[book.status] || book.status}
          </span>
        </div>

        <p className="book-card__author">by {book.author}</p>

        {book.description && (
          <p className="book-card__description">{book.description}</p>
        )}

        <div className="book-card__meta">
          {book.isbn && (
            <span className="book-card__isbn">ISBN: {book.isbn}</span>
          )}
          {book.page_count && (
            <span className="book-card__pages">{book.page_count} pages</span>
          )}
        </div>

        <div className="book-card__actions">
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => onViewDetail(book.id)}
          >
            📖 Details
          </button>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => onEdit(book)}
          >
            ✏️ Edit
          </button>
          <button
            className="btn btn-danger btn-sm"
            onClick={() => onDelete(book.id)}
          >
            🗑️ Delete
          </button>
        </div>
      </div>
    </div>
  );
}
