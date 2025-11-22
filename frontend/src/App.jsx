import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './pages/LoginPage';
import { SignupPage } from './pages/SignupPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { ResetPasswordPage } from './pages/ResetPasswordPage';
import { Dashboard } from './pages/Dashboard';
import { InventoryDashboard } from './pages/InventoryDashboard';
import { InventoryListView } from './pages/InventoryListView';
import { InventoryFormView } from './pages/InventoryFormView';
import { OperationsPage } from './pages/OperationsPage';
import { StocksPage } from './pages/StocksPage';
import { ProtectedRoute } from './components/ProtectedRoute';
import { InventoryLayout } from './components/InventoryLayout';
import { tokenManager } from './services/api';

function App() {
  const isAuthenticated = tokenManager.isAuthenticated();

  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route 
          path="/login" 
          element={isAuthenticated ? <Navigate to="/inventory/dashboard" replace /> : <LoginPage />} 
        />
        <Route 
          path="/signup" 
          element={isAuthenticated ? <Navigate to="/inventory/dashboard" replace /> : <SignupPage />} 
        />
        <Route 
          path="/forgot-password" 
          element={isAuthenticated ? <Navigate to="/inventory/dashboard" replace /> : <ForgotPasswordPage />} 
        />
        <Route 
          path="/reset-password" 
          element={isAuthenticated ? <Navigate to="/inventory/dashboard" replace /> : <ResetPasswordPage />} 
        />

        {/* Protected routes - Old dashboard (kept for reference) */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Protected routes - Inventory Management */}
        <Route
          path="/inventory/dashboard"
          element={
            <ProtectedRoute>
              <InventoryLayout>
                <InventoryDashboard />
              </InventoryLayout>
            </ProtectedRoute>
          }
        />
        
        {/* Operations Page */}
        <Route
          path="/inventory/operations"
          element={
            <ProtectedRoute>
              <InventoryLayout>
                <OperationsPage />
              </InventoryLayout>
            </ProtectedRoute>
          }
        />
        
        {/* Stocks Page */}
        <Route
          path="/inventory/stocks"
          element={
            <ProtectedRoute>
              <InventoryLayout>
                <StocksPage />
              </InventoryLayout>
            </ProtectedRoute>
          }
        />
        
        {/* Receipts Routes */}
        <Route
          path="/inventory/receipts"
          element={
            <ProtectedRoute>
              <InventoryLayout>
                <InventoryListView type="receipts" />
              </InventoryLayout>
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/inventory/receipts/:id"
          element={
            <ProtectedRoute>
              <InventoryLayout>
                <InventoryFormView type="receipts" />
              </InventoryLayout>
            </ProtectedRoute>
          }
        />
        
        {/* Deliveries Routes */}
        <Route
          path="/inventory/deliveries"
          element={
            <ProtectedRoute>
              <InventoryLayout>
                <InventoryListView type="deliveries" />
              </InventoryLayout>
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/inventory/deliveries/:id"
          element={
            <ProtectedRoute>
              <InventoryLayout>
                <InventoryFormView type="deliveries" />
              </InventoryLayout>
            </ProtectedRoute>
          }
        />

        {/* Placeholder routes */}
        <Route
          path="/inventory/history"
          element={
            <ProtectedRoute>
              <InventoryLayout>
                <div style={{ padding: '2rem' }}>
                  <h1 style={{ fontSize: '1.875rem', marginBottom: '0.5rem' }}>Move History</h1>
                  <p style={{ color: '#64748b' }}>Audit log of all inventory movements</p>
                  <div style={{ marginTop: '1.5rem', backgroundColor: 'white', borderRadius: '0.5rem', border: '1px solid #e2e8f0', padding: '2rem', textAlign: 'center' }}>
                    <p style={{ color: '#475569' }}>Move history feature coming soon...</p>
                  </div>
                </div>
              </InventoryLayout>
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/inventory/settings"
          element={
            <ProtectedRoute>
              <InventoryLayout>
                <div style={{ padding: '2rem' }}>
                  <h1 style={{ fontSize: '1.875rem', marginBottom: '0.5rem' }}>Settings</h1>
                  <p style={{ color: '#64748b' }}>Manage your warehouse settings and locations</p>
                  <div style={{ marginTop: '1.5rem', backgroundColor: 'white', borderRadius: '0.5rem', border: '1px solid #e2e8f0', padding: '2rem', textAlign: 'center' }}>
                    <p style={{ color: '#475569' }}>Settings feature coming soon...</p>
                  </div>
                </div>
              </InventoryLayout>
            </ProtectedRoute>
          }
        />

        {/* Default redirect */}
        <Route 
          path="/" 
          element={<Navigate to={isAuthenticated ? "/inventory/dashboard" : "/login"} replace />} 
        />

        {/* 404 - Redirect to login or dashboard */}
        <Route 
          path="*" 
          element={<Navigate to={isAuthenticated ? "/inventory/dashboard" : "/login"} replace />} 
        />
      </Routes>
    </Router>
  );
}

export default App;
