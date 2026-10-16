/**
 * App — Root application component.
 *
 * Manages the application state and renders either the book list
 * (with stats, search, filtering) or the book detail view.
 *
 * State architecture:
 *   - `view`: controls which page is shown ('list' or 'detail')
 *   - `books`: the fetched book list
 *   - `stats`: dashboard statistics
 *   - `selectedBookId`: which book to show in detail view
 *   - `editingBook`: which book to pre-fill in the form modal
 *   - `showForm`: whether the add/edit modal is open
 *   - `toast`: notification message and type
 */

import { useState, useEffect, useCallback } from 'react';
import {
  fetchBooks,
  fetchStats,
  createBook,
  updateBook,
  deleteBook,
} from './services/api';

import StatsBar from './components/StatsBar';
import BookCard from './components/BookCard';
import BookForm from './components/BookForm';
import BookDetail from './components/BookDetail';

export default function App() {
  // --- State ---
  const [view, setView] = useState('list');
  const [selectedBookId, setSelectedBookId] = useState(null);

  const [books, setBooks] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const [showForm, setShowForm] = useState(false);
  const [editingBook, setEditingBook] = useState(null);

  const [toast, setToast] = useState(null);

  // --- Toast helper ---
  const showToast = useCallback((message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  }, []);

  // --- Data fetching ---
  const loadBooks = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchBooks(
        statusFilter || null,
        searchQuery || null,
      );
      setBooks(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, searchQuery]);

  const loadStats = useCallback(async () => {
    try {
      const data = await fetchStats();
      setStats(data);
    } catch (_err) {
      // Stats are non-critical — silently ignore
    }
  }, []);

  useEffect(() => {
    loadBooks();
    loadStats();
  }, [loadBooks, loadStats]);

  // --- Handlers ---
  const handleAddBook = () => {
    setEditingBook(null);
    setShowForm(true);
  };

  const handleEditBook = (book) => {
    setEditingBook(book);
    setShowForm(true);
  };

  const handleFormSubmit = async (payload) => {
    try {
      if (editingBook) {
        await updateBook(editingBook.id, payload);
        showToast('Book updated successfully!');
      } else {
        await createBook(payload);
        showToast('Book added to your shelf!');
      }
      setShowForm(false);
      setEditingBook(null);
      loadBooks();
      loadStats();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  const handleDeleteBook = async (id) => {
    if (!window.confirm('Are you sure you want to delete this book?')) return;
    try {
      await deleteBook(id);
      showToast('Book removed from your shelf');
      loadBooks();
      loadStats();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  const handleViewDetail = (id) => {
    setSelectedBookId(id);
    setView('detail');
  };

  const handleBackToList = () => {
    setView('list');
    setSelectedBookId(null);
    loadBooks();
    loadStats();
  };

  // --- Render ---
  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header__brand">
          <span className="header__logo">📚</span>
          <div>
            <h1 className="header__title">BookShelf</h1>
            <p className="header__subtitle">Your personal reading tracker</p>
          </div>
        </div>
        {view === 'list' && (
          <button className="btn btn-primary" onClick={handleAddBook}>
            ＋ Add Book
          </button>
        )}
      </header>

      {/* Detail View */}
      {view === 'detail' && selectedBookId && (
        <BookDetail
          bookId={selectedBookId}
          onBack={handleBackToList}
          onShowToast={showToast}
        />
      )}

      {/* List View */}
      {view === 'list' && (
        <>
          {/* Stats Dashboard */}
          <StatsBar stats={stats} />

          {/* Toolbar */}
          <div className="toolbar">
            <input
              className="search-input"
              type="text"
              placeholder="🔍 Search by title or author..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <select
              className="filter-select"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">All Status</option>
              <option value="want_to_read">Want to Read</option>
              <option value="reading">Reading</option>
              <option value="finished">Finished</option>
            </select>
          </div>

          {/* Error State */}
          {error && (
            <div className="error-banner">
              ⚠️ {error}
              <button
                className="btn btn-secondary btn-sm"
                onClick={loadBooks}
                style={{ marginLeft: 'auto' }}
              >
                Retry
              </button>
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="loading">
              <div className="loading-spinner" />
              <span>Loading your bookshelf...</span>
            </div>
          )}

          {/* Empty State */}
          {!loading && !error && books.length === 0 && (
            <div className="empty-state">
              <div className="empty-state__icon">📖</div>
              <h3 className="empty-state__title">Your shelf is empty</h3>
              <p className="empty-state__text">
                Start building your reading collection by adding your first book.
              </p>
              <button className="btn btn-primary" onClick={handleAddBook}>
                ＋ Add Your First Book
              </button>
            </div>
          )}

          {/* Book Grid */}
          {!loading && books.length > 0 && (
            <div className="book-grid">
              {books.map((book) => (
                <BookCard
                  key={book.id}
                  book={book}
                  onEdit={handleEditBook}
                  onDelete={handleDeleteBook}
                  onViewDetail={handleViewDetail}
                />
              ))}
            </div>
          )}
        </>
      )}

      {/* Add/Edit Modal */}
      {showForm && (
        <BookForm
          book={editingBook}
          onSubmit={handleFormSubmit}
          onClose={() => {
            setShowForm(false);
            setEditingBook(null);
          }}
        />
      )}

      {/* Toast Notification */}
      {toast && (
        <div className={`toast toast--${toast.type}`}>
          {toast.type === 'success' ? '✅' : '❌'} {toast.message}
        </div>
      )}
    </div>
  );
}
