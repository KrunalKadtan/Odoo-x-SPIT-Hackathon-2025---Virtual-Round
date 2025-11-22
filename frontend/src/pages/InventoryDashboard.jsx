import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { inventoryAPI } from '../services/api';
import './InventoryDashboard.css';

export function InventoryDashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalProducts: 0,
    lowStockItems: 0,
    pendingReceipts: 0,
    pendingDeliveries: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      // Use the new dashboard stats endpoint
      const data = await inventoryAPI.getDashboardStats();
      
      setStats({
        totalProducts: data.total_products || 0,
        lowStockItems: data.low_stock_items || 0,
        pendingReceipts: data.pending_receipts || 0,
        pendingDeliveries: data.pending_deliveries || 0
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
        {/* Total Products Card */}
        <Card 
          className="dashboard-card products-card"
          onClick={() => navigate('/inventory/stocks')}
        >
          <div className="card-icon-header">
            <div className="icon-wrapper blue">
              <svg className="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
            <span className="card-label">Products</span>
          </div>

          <div className="card-stats">
            <div className="stat-number">{loading ? '...' : stats.totalProducts}</div>
            <div className="stat-label">Total Active</div>
          </div>

          <div className="card-indicators">
            <div className="indicator">
              <div className="indicator-dot blue"></div>
              <span className="indicator-text">
                <span className="indicator-value">{stats.totalProducts}</span> In Catalog
              </span>
            </div>
          </div>
        </Card>

        {/* Low Stock Items Card */}
        <Card 
          className="dashboard-card low-stock-card"
          onClick={() => navigate('/inventory/stocks')}
        >
          <div className="card-icon-header">
            <div className="icon-wrapper amber">
              <svg className="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <span className="card-label">Low Stock</span>
          </div>

          <div className="card-stats">
            <div className="stat-number">{loading ? '...' : stats.lowStockItems}</div>
            <div className="stat-label">Items Below 10</div>
          </div>

          <div className="card-indicators">
            <div className="indicator">
              <div className="indicator-dot amber"></div>
              <span className="indicator-text">
                <span className="indicator-value">{stats.lowStockItems}</span> Need Restock
              </span>
            </div>
          </div>
        </Card>

        {/* Pending Receipts Card */}
        <Card 
          className="dashboard-card receipts-card"
          onClick={() => navigate('/inventory/receipts')}
        >
          <div className="card-icon-header">
            <div className="icon-wrapper green">
              <svg className="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
              </svg>
            </div>
            <span className="card-label">Receipts</span>
          </div>

          <div className="card-stats">
            <div className="stat-number">{loading ? '...' : stats.pendingReceipts}</div>
            <div className="stat-label">To Process</div>
          </div>

          <div className="card-indicators">
            <div className="indicator">
              <div className="indicator-dot green"></div>
              <span className="indicator-text">
                <span className="indicator-value">{stats.pendingReceipts}</span> Pending
              </span>
            </div>
          </div>
        </Card>

        {/* Pending Deliveries Card */}
        <Card 
          className="dashboard-card deliveries-card"
          onClick={() => navigate('/inventory/deliveries')}
        >
          <div className="card-icon-header">
            <div className="icon-wrapper purple">
              <svg className="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
              </svg>
            </div>
            <span className="card-label">Deliveries</span>
          </div>

          <div className="card-stats">
            <div className="stat-number">{loading ? '...' : stats.pendingDeliveries}</div>
            <div className="stat-label">To Deliver</div>
          </div>

          <div className="card-indicators">
            <div className="indicator">
              <div className="indicator-dot purple"></div>
              <span className="indicator-text">
                <span className="indicator-value">{stats.pendingDeliveries}</span> Pending
              </span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
