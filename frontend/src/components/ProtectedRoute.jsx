import { Navigate } from 'react-router-dom';
import { tokenManager } from '../services/api';

export function ProtectedRoute({ children }) {
  const isAuthenticated = tokenManager.isAuthenticated();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
