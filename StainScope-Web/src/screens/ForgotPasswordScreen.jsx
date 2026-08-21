import React, { useState } from 'react';
import { ArrowLeft } from 'lucide-react';

export default function ForgotPasswordScreen({ onNavigate }) {
  const [email, setEmail] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onNavigate('otp');
  };

  return (
    <div className="auth-page-container animate-fade-in">
      <div className="auth-header">
        <h1 className="auth-title">
          Reset Your<br />Password
        </h1>
        <p className="auth-subtitle">Get your account back</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group" style={{ marginBottom: '24px' }}>
          <label className="form-label">Enter Your Email</label>
          <div className="input-wrapper">
            <input
              type="email"
              className={`form-input ${email ? 'has-active-value' : ''}`}
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
        </div>

        <button type="submit" className="btn-primary-burgundy">
          Send OTP
        </button>
      </form>

      <div style={{ marginTop: '20px', textAlign: 'center' }}>
        <button
          type="button"
          onClick={() => onNavigate('login')}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-muted)',
            fontSize: '13px',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          <ArrowLeft size={16} /> Back to Sign In
        </button>
      </div>
    </div>
  );
}
