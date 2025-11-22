import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Label } from '../components/ui/Label';
import { authAPI } from '../services/api';
import './LoginPage.css';

export function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);

    try {
      const response = await authAPI.requestPasswordReset(email);
      setMessage(response.message);
      
      // Navigate to reset password page after 2 seconds
      setTimeout(() => {
        navigate('/reset-password', { state: { email } });
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to send OTP. Please try again.');
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

      {/* Right side - Forgot Password Form */}
      <div className="login-form-container">
        <div className="login-form-wrapper">
          <div className="login-card">
            <h2 className="form-title">Forgot Password</h2>
            <p className="form-subtitle">
              Enter your email address and we'll send you an OTP to reset your password
            </p>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            {message && (
              <div style={{
                backgroundColor: '#d1fae5',
                border: '1px solid #a7f3d0',
                color: '#065f46',
                padding: '0.75rem',
                borderRadius: '0.375rem',
                marginBottom: '1.5rem',
                fontSize: '0.875rem'
              }}>
                {message}
              </div>
            )}

            <form onSubmit={handleSubmit} className="login-form">
              <div className="form-group">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={loading}
                />
              </div>

              <Button type="submit" className="submit-button" disabled={loading}>
                {loading ? 'Sending OTP...' : 'Send OTP'}
              </Button>
            </form>

            <div className="signup-link">
              <span>Remember your password? </span>
              <Link to="/login">Sign in</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
