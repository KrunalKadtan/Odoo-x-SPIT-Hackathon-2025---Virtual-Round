import { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { OTPInput } from 'input-otp';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Label } from '../components/ui/Label';
import { authAPI, tokenManager } from '../services/api';
import './LoginPage.css';
import './ResetPasswordPage.css';

export function ResetPasswordPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const emailFromState = location.state?.email || '';

  const [formData, setFormData] = useState({
    email: emailFromState,
    otpCode: '',
    newPassword: '',
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
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleOTPChange = (value) => {
    setFormData(prev => ({
      ...prev,
      otpCode: value
    }));
    if (errors.otpCode) {
      setErrors(prev => ({ ...prev, otpCode: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    }

    if (formData.otpCode.length !== 6) {
      newErrors.otpCode = 'OTP must be 6 digits';
    }

    if (formData.newPassword.length < 8) {
      newErrors.newPassword = 'Password must be at least 8 characters';
    } else if (!/[A-Z]/.test(formData.newPassword)) {
      newErrors.newPassword = 'Password must contain at least 1 uppercase letter';
    } else if (!/[!@#$%^&*(),.?":{}|<>]/.test(formData.newPassword)) {
      newErrors.newPassword = 'Password must contain at least 1 special character';
    }

    if (formData.newPassword !== formData.confirmPassword) {
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
      const response = await authAPI.confirmPasswordReset(
        formData.email,
        formData.otpCode,
        formData.newPassword
      );
      
      // Store tokens and navigate to inventory dashboard
      tokenManager.setTokens(response.access_token, response.refresh_token);
      
      // Show success message and redirect
      alert('Password reset successful! Redirecting to dashboard...');
      navigate('/inventory/dashboard');
    } catch (err) {
      const errorData = err.response?.data;
      if (errorData?.details) {
        const backendErrors = {};
        Object.keys(errorData.details).forEach(key => {
          backendErrors[key] = Array.isArray(errorData.details[key]) 
            ? errorData.details[key][0] 
            : errorData.details[key];
        });
        setErrors(backendErrors);
      } else {
        setErrors({ general: errorData?.error || 'Password reset failed. Please try again.' });
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

      {/* Right side - Reset Password Form */}
      <div className="login-form-container">
        <div className="login-form-wrapper">
          <div className="login-card">
            <h2 className="form-title">Reset Password</h2>
            <p className="form-subtitle">
              Enter the OTP sent to your email and create a new password
            </p>

            {errors.general && (
              <div className="error-message">
                {errors.general}
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
                <Label htmlFor="otpCode">OTP Code</Label>
                <div className="otp-container">
                  <OTPInput
                    maxLength={6}
                    value={formData.otpCode}
                    onChange={handleOTPChange}
                    render={({ slots }) => (
                      <div className="otp-input-group">
                        {slots.map((slot, idx) => (
                          <div key={idx} className="otp-slot">
                            {slot.char !== null && <div>{slot.char}</div>}
                            {slot.hasFakeCaret && <div className="otp-caret" />}
                          </div>
                        ))}
                      </div>
                    )}
                  />
                </div>
                {errors.otpCode && (
                  <span style={{ color: '#ef4444', fontSize: '0.875rem' }}>
                    {errors.otpCode}
                  </span>
                )}
              </div>

              <div className="form-group">
                <Label htmlFor="newPassword">New Password</Label>
                <Input
                  id="newPassword"
                  name="newPassword"
                  type="password"
                  placeholder="Min 8 chars, 1 uppercase, 1 special"
                  value={formData.newPassword}
                  onChange={handleChange}
                  required
                  disabled={loading}
                  aria-invalid={!!errors.newPassword}
                />
                {errors.newPassword && (
                  <span style={{ color: '#ef4444', fontSize: '0.875rem' }}>
                    {errors.newPassword}
                  </span>
                )}
              </div>

              <div className="form-group">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  placeholder="Re-enter your new password"
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
                {loading ? 'Resetting password...' : 'Reset Password'}
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
