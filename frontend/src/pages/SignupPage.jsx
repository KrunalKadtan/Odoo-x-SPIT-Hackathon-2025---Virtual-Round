import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Label } from '../components/ui/Label';
import { authAPI, tokenManager } from '../services/api';
import './LoginPage.css';

export function SignupPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    loginId: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Login ID validation
    if (formData.loginId.length < 6 || formData.loginId.length > 12) {
      newErrors.loginId = 'Login ID must be 6-12 characters';
    } else if (!/^[a-zA-Z0-9]+$/.test(formData.loginId)) {
      newErrors.loginId = 'Login ID must be alphanumeric only';
    }

    // Email validation
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email';
    }

    // Password validation
    if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    } else if (!/[A-Z]/.test(formData.password)) {
      newErrors.password = 'Password must contain at least 1 uppercase letter';
    } else if (!/[!@#$%^&*(),.?":{}|<>]/.test(formData.password)) {
      newErrors.password = 'Password must contain at least 1 special character';
    }

    // Confirm password validation
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const response = await authAPI.signup(
        formData.loginId,
        formData.email,
        formData.password
      );
      
      // Store tokens and user data
      tokenManager.setTokens(response.access_token, response.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      
      // Navigate to dashboard
      navigate('/dashboard');
    } catch (err) {
      const errorData = err.response?.data;
      if (errorData?.details) {
        // Handle field-specific errors from backend
        const backendErrors = {};
        Object.keys(errorData.details).forEach(key => {
          backendErrors[key] = Array.isArray(errorData.details[key]) 
            ? errorData.details[key][0] 
            : errorData.details[key];
        });
        setErrors(backendErrors);
      } else {
        setErrors({ general: errorData?.error || 'Registration failed. Please try again.' });
      }
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

      {/* Right side - Signup Form */}
      <div className="login-form-container">
        <div className="login-form-wrapper">
          <div className="login-card">
            <h2 className="form-title">Create an account</h2>
            <p className="form-subtitle">Sign up to get started</p>

            {errors.general && (
              <div className="error-message">
                {errors.general}
              </div>
            )}

            <form onSubmit={handleSubmit} className="login-form">
              <div className="form-group">
                <Label htmlFor="loginId">Login ID</Label>
                <Input
                  id="loginId"
                  name="loginId"
                  type="text"
                  placeholder="6-12 alphanumeric characters"
                  value={formData.loginId}
                  onChange={handleChange}
                  required
                  disabled={loading}
                  aria-invalid={!!errors.loginId}
                />
                {errors.loginId && (
                  <span style={{ color: '#ef4444', fontSize: '0.875rem' }}>
                    {errors.loginId}
                  </span>
                )}
              </div>

              <div className="form-group">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  disabled={loading}
                  aria-invalid={!!errors.email}
                />
                {errors.email && (
                  <span style={{ color: '#ef4444', fontSize: '0.875rem' }}>
                    {errors.email}
                  </span>
                )}
              </div>

              <div className="form-group">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="Min 8 chars, 1 uppercase, 1 special"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  disabled={loading}
                  aria-invalid={!!errors.password}
                />
                {errors.password && (
                  <span style={{ color: '#ef4444', fontSize: '0.875rem' }}>
                    {errors.password}
                  </span>
                )}
              </div>

              <div className="form-group">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  placeholder="Re-enter your password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                  disabled={loading}
                  aria-invalid={!!errors.confirmPassword}
                />
                {errors.confirmPassword && (
                  <span style={{ color: '#ef4444', fontSize: '0.875rem' }}>
                    {errors.confirmPassword}
                  </span>
                )}
              </div>

              <Button type="submit" className="submit-button" disabled={loading}>
                {loading ? 'Creating account...' : 'Sign Up'}
              </Button>
            </form>

            <div className="signup-link">
              <span>Already have an account? </span>
              <Link to="/login">Sign in</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
