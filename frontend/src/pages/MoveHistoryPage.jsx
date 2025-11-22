import { useState, useEffect } from 'react';
import { inventoryAPI } from '../services/api';
import { Card } from '../components/ui/Card';
import './MoveHistoryPage.css';

export function MoveHistoryPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    action_type: '',
    date_from: '',
    date_to: '',
  });

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError(null);

      // Build query params
      const params = {};
      if (filters.action_type) params.action_type = filters.action_type;
      if (filters.date_from) params.date_from = filters.date_from;
      if (filters.date_to) params.date_to = filters.date_to;

      const data = await inventoryAPI.getMoveHistory(params);
      setHistory(data);
    } catch (err) {
      console.error('Error fetching move history:', err);
      setError('Failed to load move history. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleApplyFilters = () => {
    fetchHistory();
  };

  const handleClearFilters = () => {
    setFilters({
      action_type: '',
      date_from: '',
      date_to: '',
    });
    setTimeout(() => fetchHistory(), 0);
  };

  const getActionTypeBadge = (actionType) => {
    const badges = {
      stock_move: { label: 'Stock Move', className: 'badge-blue' },
      status_change: { label: 'Status Change', className: 'badge-purple' },
      adjustment: { label: 'Adjustment', className: 'badge-amber' },
    };
    return badges[actionType] || { label: actionType, className: 'badge-gray' };
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="history-page">
        <div className="history-header">
          <h1 className="history-title">Move History</h1>
          <p className="history-subtitle">Audit log of all inventory movements and changes</p>
        </div>
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="history-page">
      <div className="history-header">
        <h1 className="history-title">Move History</h1>
        <p className="history-subtitle">Audit log of all inventory movements and changes</p>
      </div>

      {error && (
        <div className="alert alert-error">
          <svg className="alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{error}</span>
        </div>
      )}

      {/* Filters */}
      <Card className="filters-card">
        <div className="filters-header">
          <h2 className="filters-title">Filters</h2>
        </div>
        <div className="filters-grid">
          <div className="filter-group">
            <label htmlFor="action_type" className="filter-label">Action Type</label>
            <select
              id="action_type"
              name="action_type"
              value={filters.action_type}
              onChange={handleFilterChange}
              className="filter-select"
            >
              <option value="">All Types</option>
              <option value="stock_move">Stock Move</option>
              <option value="status_change">Status Change</option>
              <option value="adjustment">Adjustment</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="date_from" className="filter-label">From Date</label>
            <input
              type="datetime-local"
              id="date_from"
              name="date_from"
              value={filters.date_from}
              onChange={handleFilterChange}
              className="filter-input"
            />
          </div>

          <div className="filter-group">
            <label htmlFor="date_to" className="filter-label">To Date</label>
            <input
              type="datetime-local"
              id="date_to"
              name="date_to"
              value={filters.date_to}
              onChange={handleFilterChange}
              className="filter-input"
            />
          </div>
        </div>

        <div className="filters-actions">
          <button onClick={handleApplyFilters} className="btn btn-primary">
            Apply Filters
          </button>
          <button onClick={handleClearFilters} className="btn btn-outline">
            Clear
          </button>
        </div>
      </Card>

      {/* History List */}
      <Card className="history-card">
        <div className="history-stats">
          <span className="stats-text">
            Showing <strong>{history.length}</strong> {history.length === 1 ? 'entry' : 'entries'}
          </span>
        </div>

        {history.length === 0 ? (
          <div className="empty-state">
            <svg className="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="empty-text">No history entries found</p>
            <p className="empty-subtext">Try adjusting your filters or check back later</p>
          </div>
        ) : (
          <div className="history-list">
            {history.map((entry) => {
              const badge = getActionTypeBadge(entry.action_type);
              return (
                <div key={entry.id} className="history-entry">
                  <div className="entry-header">
                    <div className="entry-meta">
                      <span className={`badge ${badge.className}`}>
                        {badge.label}
                      </span>
                      <span className="entry-time">{formatDateTime(entry.timestamp)}</span>
                    </div>
                    {entry.user && (
                      <span className="entry-user">
                        <svg className="user-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        {entry.user.username}
                      </span>
                    )}
                  </div>

                  <div className="entry-content">
                    <p className="entry-description">{entry.action_display}</p>

                    <div className="entry-details">
                      {entry.picking && (
                        <div className="detail-item">
                          <span className="detail-label">Picking:</span>
                          <span className="detail-value">{entry.picking.reference}</span>
                        </div>
                      )}

                      {entry.product && (
                        <div className="detail-item">
                          <span className="detail-label">Product:</span>
                          <span className="detail-value">{entry.product.sku} - {entry.product.name}</span>
                        </div>
                      )}

                      {entry.quantity && (
                        <div className="detail-item">
                          <span className="detail-label">Quantity:</span>
                          <span className="detail-value">{entry.quantity}</span>
                        </div>
                      )}

                      {entry.source_location && (
                        <div className="detail-item">
                          <span className="detail-label">From:</span>
                          <span className="detail-value">{entry.source_location.name}</span>
                        </div>
                      )}

                      {entry.destination_location && (
                        <div className="detail-item">
                          <span className="detail-label">To:</span>
                          <span className="detail-value">{entry.destination_location.name}</span>
                        </div>
                      )}

                      {entry.old_status && entry.new_status && (
                        <div className="detail-item">
                          <span className="detail-label">Status:</span>
                          <span className="detail-value">
                            {entry.old_status} → {entry.new_status}
                          </span>
                        </div>
                      )}
                    </div>

                    {entry.notes && (
                      <div className="entry-notes">
                        <span className="notes-label">Notes:</span>
                        <span className="notes-text">{entry.notes}</span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>
    </div>
  );
}
