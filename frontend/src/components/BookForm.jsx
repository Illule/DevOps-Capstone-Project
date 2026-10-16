/**
 * BookForm — Modal form for creating and editing books.
 *
 * Handles both "Add Book" (no initial data) and "Edit Book"
 * (pre-filled fields) modes based on the `book` prop.
 */

import { useState, useEffect } from 'react';

export default function BookForm({ book, onSubmit, onClose }) {
  const isEditing = Boolean(book);

  const [formData, setFormData] = useState({
    title: '',
    author: '',
    isbn: '',
    status: 'want_to_read',
    page_count: '',
    description: '',
  });

  const [submitting, setSubmitting] = useState(false);

  // Pre-fill form when editing
  useEffect(() => {
    if (book) {
      setFormData({
        title: book.title || '',
        author: book.author || '',
        isbn: book.isbn || '',
        status: book.status || 'want_to_read',
        page_count: book.page_count || '',
        description: book.description || '',
      });
    }
  }, [book]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      // Build the payload — omit empty optional fields
      const payload = {
        title: formData.title.trim(),
        author: formData.author.trim(),
        status: formData.status,
      };

      if (formData.isbn.trim()) payload.isbn = formData.isbn.trim();
      if (formData.page_count) payload.page_count = parseInt(formData.page_count, 10);
      if (formData.description.trim()) payload.description = formData.description.trim();

      await onSubmit(payload);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2 className="modal__title">
          {isEditing ? '✏️ Edit Book' : '📚 Add New Book'}
        </h2>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="title">Title *</label>
            <input
              id="title"
              name="title"
              type="text"
              value={formData.title}
              onChange={handleChange}
              placeholder="e.g. The Pragmatic Programmer"
              required
              maxLength={255}
            />
          </div>

          <div className="form-group">
            <label htmlFor="author">Author *</label>
            <input
              id="author"
              name="author"
              type="text"
              value={formData.author}
              onChange={handleChange}
              placeholder="e.g. David Thomas"
              required
              maxLength={255}
            />
          </div>

          <div className="form-group">
            <label htmlFor="isbn">ISBN</label>
            <input
              id="isbn"
              name="isbn"
              type="text"
              value={formData.isbn}
              onChange={handleChange}
              placeholder="e.g. 9780135957059"
              maxLength={13}
            />
          </div>

          <div className="form-group">
            <label htmlFor="status">Reading Status</label>
            <select
              id="status"
              name="status"
              value={formData.status}
              onChange={handleChange}
            >
              <option value="want_to_read">Want to Read</option>
              <option value="reading">Reading</option>
              <option value="finished">Finished</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="page_count">Page Count</label>
            <input
              id="page_count"
              name="page_count"
              type="number"
              value={formData.page_count}
              onChange={handleChange}
              placeholder="e.g. 352"
              min={1}
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Brief description of the book..."
              maxLength={5000}
              rows={3}
            />
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={submitting}
            >
              {submitting
                ? 'Saving...'
                : isEditing
                  ? 'Save Changes'
                  : 'Add Book'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
