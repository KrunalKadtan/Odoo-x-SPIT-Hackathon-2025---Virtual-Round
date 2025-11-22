import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { tokenManager } from '../services/api';
import './Dashboard.css';

export function Dashboard() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const handleLogout = () => {
    tokenManager.clearTokens();
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <nav className="dashboard-nav">
        <div className="nav-content">
          <div className="nav-brand">
            <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
            <span className="nav-title">StockMaster</span>
          </div>
          <Button variant="outline" onClick={handleLogout}>
            Logout
          </Button>
        </div>
      </nav>

      <main className="dashboard-main">
        <div className="dashboard-content">
          <div className="welcome-card">
            <h1 className="welcome-title">Welcome to StockMaster!</h1>
            <p className="welcome-subtitle">
              You have successfully logged in to the Inventory Management System
            </p>
            
            <div className="user-info">
              <div className="info-item">
                <span className="info-label">Login ID:</span>
                <span className="info-value">{user.login_id || 'N/A'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Email:</span>
                <span className="info-value">{user.email || 'N/A'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Member Since:</span>
                <span className="info-value">
                  {user.date_joined ? new Date(user.date_joined).toLocaleDateString() : 'N/A'}
                </span>
              </div>
            </div>

            <div className="dashboard-placeholder">
              <svg className="placeholder-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="placeholder-text">
                Go to Inventory Management
              </p>
              <p className="placeholder-subtext">
                Access the full inventory management system
              </p>
              <Button 
                style={{ marginTop: '1.5rem' }}
                onClick={() => navigate('/inventory/dashboard')}
              >
                Open Inventory Dashboard
              </Button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
