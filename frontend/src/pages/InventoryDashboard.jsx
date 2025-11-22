import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { inventoryAPI } from '../services/api';
import './InventoryDashboard.css';

export function InventoryDashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    receipts: { total: 0, late: 0, waiting: 0 },
    deliveries: { total: 0, late: 0, waiting: 0, operations: 0 }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      // Fetch pickings data
      const pickings = await inventoryAPI.getPickings();
      
      // Calculate stats
      const receipts = pickings.filter(p => p.operation_type_name?.includes('Receipt'));
      const deliveries = pickings.filter(p => p.operation_type_name?.includes('Delivery'));
      
      const receiptsToProcess = receipts.filter(p => ['draft', 'confirmed', 'waiting'].includes(p.status));
      const receiptsLate = receipts.filter(p => {
        const scheduled = new Date(p.scheduled_date);
        return scheduled < new Date() && p.status !== 'done';
      });
      const receiptsWaiting = receipts.filter(p => p.status === 'waiting');
      
      const deliveriesToDeliver = deliveries.filter(p => ['draft', 'confirmed', 'waiting'].includes(p.status));
      const deliveriesLate = deliveries.filter(p => {
        const scheduled = new Date(p.scheduled_date);
        return scheduled < new Date() && p.status !== 'done';
      });
      const deliveriesWaiting = deliveries.filter(p => p.status === 'waiting');
      const deliveriesOperations = deliveries.length;

      setStats({
        receipts: {
          total: receiptsToProcess.length,
          late: receiptsLate.length,
          waiting: receiptsWaiting.length
        },
        deliveries: {
          total: deliveriesToDeliver.length,
          late: deliveriesLate.length,
          waiting: deliveriesWaiting.length,
          operations: deliveriesOperations
        }
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="inventory-dashboard">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Dashboard</h1>
        <p className="dashboard-subtitle">Overview of your warehouse operations</p>
      </div>

      <div className="dashboard-grid">
        {/* Receipts Card */}
        <Card 
          className="dashboard-card receipts-card"
          onClick={() => navigate('/inventory/receipts')}
        >
          <div className="card-icon-header">
            <div className="icon-wrapper green">
              <svg className="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
            <span className="card-label">Receipts</span>
          </div>

          <div className="card-stats">
            <div className="stat-number">{loading ? '...' : stats.receipts.total}</div>
            <div className="stat-label">To Process</div>
          </div>

          <div className="card-indicators">
            <div className="indicator">
              <div className="indicator-dot red"></div>
              <span className="indicator-text">
                <span className="indicator-value">{stats.receipts.late}</span> Late
              </span>
            </div>
            <div className="indicator">
              <div className="indicator-dot amber"></div>
              <span className="indicator-text">
                <span className="indicator-value">{stats.receipts.waiting}</span> Waiting
              </span>
            </div>
          </div>
        </Card>

        {/* Delivery Orders Card */}
        <Card 
          className="dashboard-card deliveries-card"
          onClick={() => navigate('/inventory/deliveries')}
        >
          <div className="card-icon-header">
            <div className="icon-wrapper blue">
              <svg className="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span className="card-label">Delivery Orders</span>
          </div>

          <div className="card-stats">
            <div className="stat-number">{loading ? '...' : stats.deliveries.total}</div>
            <div className="stat-label">To Deliver</div>
          </div>

          <div className="card-indicators">
            <div className="indicator">
              <div className="indicator-dot red"></div>
              <span className="indicator-text">
                <span className="indicator-value">{stats.deliveries.late}</span> Late
              </span>
            </div>
            <div className="indicator">
              <div className="indicator-dot amber"></div>
              <span className="indicator-text">
                <span className="indicator-value">{stats.deliveries.waiting}</span> Waiting
              </span>
            </div>
            <div className="indicator">
              <div className="indicator-dot gray"></div>
              <span className="indicator-text">
                <span className="indicator-value">{stats.deliveries.operations}</span> Operations
              </span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
