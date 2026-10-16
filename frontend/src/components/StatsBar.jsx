/**
 * StatsBar — Dashboard statistics cards.
 *
 * Displays reading metrics: total books, counts by status,
 * total reviews, and average rating.
 */

export default function StatsBar({ stats }) {
  if (!stats) return null;

  const cards = [
    { value: stats.total_books, label: 'Total Books', icon: '📚' },
    { value: stats.want_to_read, label: 'Want to Read', icon: '📋' },
    { value: stats.reading, label: 'Reading', icon: '📖' },
    { value: stats.finished, label: 'Finished', icon: '✅' },
    { value: stats.total_reviews, label: 'Reviews', icon: '💬' },
    {
      value: stats.average_rating ? `${stats.average_rating} ★` : '—',
      label: 'Avg Rating',
      icon: '⭐',
    },
  ];

  return (
    <div className="stats-grid">
      {cards.map((card) => (
        <div key={card.label} className="stat-card">
          <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>{card.icon}</div>
          <div className="stat-card__value">{card.value}</div>
          <div className="stat-card__label">{card.label}</div>
        </div>
      ))}
    </div>
  );
}
