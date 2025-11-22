import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import './OperationsPage.css';

export function OperationsPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('receipts');

  const tabs = [
    { id: 'receipts', label: 'Receipts', icon: '📦' },
    { id: 'deliveries', label: 'Deliveries', icon: '🚚' },
    { id: 'transfers', label: 'Internal Transfers', icon: '🔄' },
  ];

  return (
    <div className="operations-page">
      <div className="operations-header">
        <div>
          <h1 className="operations-title">Operations</h1>
          <p className="operations-subtitle">Manage receipts, deliveries, and transfers</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="operations-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="operations-content">
        {activeTab === 'receipts' && (
          <div className="tab-content">
            <div className="content-header">
              <h2 className="content-title">Receipts</h2>
              <Button onClick={() => navigate('/inventory/receipts')}>
                View All Receipts
              </Button>
            </div>
            <p className="content-description">
              Manage incoming stock from suppliers. Create receipt orders, validate deliveries, and update inventory levels.
            </p>
            <div className="quick-actions">
              <Button onClick={() => navigate('/inventory/receipts/new')}>
                <svg className="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                New Receipt
              </Button>
              <Button variant="outline" onClick={() => navigate('/inventory/receipts')}>
                Browse Receipts
              </Button>
            </div>
          </div>
        )}

        {activeTab === 'deliveries' && (
          <div className="tab-content">
            <div className="content-header">
              <h2 className="content-title">Deliveries</h2>
              <Button onClick={() => navigate('/inventory/deliveries')}>
                View All Deliveries
              </Button>
            </div>
            <p className="content-description">
              Manage outgoing stock to customers. Create delivery orders, process shipments, and track deliveries.
            </p>
            <div className="quick-actions">
              <Button onClick={() => navigate('/inventory/deliveries/new')}>
                <svg className="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                New Delivery
              </Button>
              <Button variant="outline" onClick={() => navigate('/inventory/deliveries')}>
                Browse Deliveries
              </Button>
            </div>
          </div>
        )}

        {activeTab === 'transfers' && (
          <div className="tab-content">
            <div className="content-header">
              <h2 className="content-title">Internal Transfers</h2>
              <Button disabled>
                Coming Soon
              </Button>
            </div>
            <p className="content-description">
              Move stock between warehouse locations. Create transfer orders and track internal movements.
            </p>
            <div className="placeholder-box">
              <svg className="placeholder-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
              <p className="placeholder-text">Internal transfers feature coming soon...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
