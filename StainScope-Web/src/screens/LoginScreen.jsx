import React, { useState } from 'react';
import { Eye, EyeOff, AlertCircle, Loader2 } from 'lucide-react';
import { signInUser } from '../api';

export default function LoginScreen({ onNavigate, onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [authError, setAuthError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setAuthError('Please enter both email and password.');
      return;
    }

    setAuthError('');
    setIsSubmitting(true);

    try {
      const data = await signInUser(email, password);
      setIsSubmitting(false);

      if (data?.session) {
        if (onLoginSuccess) {
          onLoginSuccess(data.session);
        } else {
          onNavigate('dashboard');
        }
      } else {
        setAuthError('Login succeeded but session could not be established.');
      }
    } catch (err) {
      setIsSubmitting(false);
      console.error('Login authentication error:', err);
      setAuthError(err.message || 'Invalid email or password. Please check your credentials.');
    }
  };

  return (
    <div className="auth-page-container animate-fade-in">
      <div className="auth-header">
        <h1 className="auth-title">
          Hey,<br />Welcome Back
        </h1>
        <p className="auth-subtitle">Please login to your scientific account.</p>
      </div>

      {authError && (
        <div style={{
          background: '#FEF2F2',
          border: '1px solid #FCA5A5',
          color: '#DC2626',
          padding: '12px 14px',
          borderRadius: 'var(--radius-md)',
          fontSize: '13px',
          fontWeight: '600',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <AlertCircle size={18} style={{ flexShrink: 0 }} />
          <span>{authError}</span>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Email</label>
          <div className="input-wrapper">
            <input
              type="email"
              className={`form-input ${email ? 'has-active-value' : ''}`}
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
        </div>

        <div className="form-group" style={{ marginBottom: '4px' }}>
          <label className="form-label">Password</label>
          <div className="input-wrapper">
            <input
              type={showPassword ? 'text' : 'password'}
              className="form-input"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button
              type="button"
              className="input-icon-right"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
        </div>

        <a
          href="#forgot"
          className="forgot-password-link"
          onClick={(e) => {
            e.preventDefault();
            onNavigate('forgot-password');
          }}
        >
          Forgot Password
        </a>

        <button type="submit" className="btn-primary-burgundy" disabled={isSubmitting} style={{ opacity: isSubmitting ? 0.7 : 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
          {isSubmitting ? <><Loader2 className="animate-spin" size={18} /> Signing in...</> : 'Sign in'}
        </button>
      </form>

      <div className="auth-footer-text">
        Didn't have an Account?
        <a
          href="#signup"
          className="auth-footer-link"
          onClick={(e) => {
            e.preventDefault();
            onNavigate('signup');
          }}
        >
          Sign-up
        </a>
      </div>
    </div>
  );
}
