import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Label } from '../components/ui/Label';
import { authAPI, tokenManager } from '../services/api';
import './LoginPage.css';

export function LoginPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    loginId: '',
    password: '',
    rememberMe: false,
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authAPI.login(formData.loginId, formData.password);
      
      // Store tokens and user data
      tokenManager.setTokens(response.access_token, response.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      
      // Navigate to inventory dashboard
      navigate('/inventory/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Invalid credentials. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      {/* Left side - Brand/Image */}
      <div className="login-brand">
        <div className="brand-content">
          <div className="brand-icon">
            <svg className="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
          <h1 className="brand-title">Inventory Management System</h1>
          <p className="brand-description">
            Streamline your warehouse operations with powerful inventory tracking and management tools.
          </p>
        </div>
      </div>

      {/* Right side - Login Form */}
      <div className="login-form-container">
        <div className="login-form-wrapper">
          <div className="login-card">
            <h2 className="form-title">Welcome back</h2>
            <p className="form-subtitle">Sign in to your account to continue</p>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="login-form">
              <div className="form-group">
                <Label htmlFor="loginId">Login ID</Label>
                <Input
                  id="loginId"
                  name="loginId"
                  type="text"
                  placeholder="Enter your login ID"
                  value={formData.loginId}
                  onChange={handleChange}
                  required
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  disabled={loading}
                />
              </div>

              <div className="form-options">
                <label className="remember-me">
                  <input
                    type="checkbox"
                    name="rememberMe"
                    checked={formData.rememberMe}
                    onChange={handleChange}
                    disabled={loading}
                  />
                  <span>Remember me</span>
                </label>
                <Link to="/forgot-password" className="forgot-link">
                  Forgot password?
                </Link>
              </div>

              <Button type="submit" className="submit-button" disabled={loading}>
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>

            <div className="signup-link">
              <span>Don't have an account? </span>
              <Link to="/signup">Sign up</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
