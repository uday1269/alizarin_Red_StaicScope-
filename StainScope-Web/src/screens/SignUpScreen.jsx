import React, { useState } from 'react';
import { Eye, EyeOff, CheckCircle2, Info, ShieldCheck, AlertCircle, Loader2 } from 'lucide-react';
import { signUpUser } from '../api';

export default function SignUpScreen({ onNavigate, onLoginSuccess }) {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [signUpError, setSignUpError] = useState('');

  // Password validation rules & natural language missing requirements generator
  const getPasswordValidation = (pass) => {
    if (!pass) {
      return {
        isValid: false,
        message: 'Enter a password to continue.',
        color: '#E2E8F0',
        label: 'None',
        score: 0
      };
    }

    const missing = [];
    if (!/[A-Z]/.test(pass)) missing.push('an uppercase letter');
    if (!/[a-z]/.test(pass)) missing.push('a lowercase letter');
    if (!/[0-9]/.test(pass)) missing.push('a number');
    if (!/[^A-Za-z0-9]/.test(pass)) missing.push('a special character');

    if (pass.length < 6 && missing.length === 0) {
      missing.push('at least 6 characters');
    }

    const isValid = pass.length >= 6 && missing.length === 0;

    // Strength score & styling
    let label = 'Weak';
    let color = '#EF4444';
    let score = 1;

    if (isValid) {
      label = 'Strong';
      color = '#10B981';
      score = 3;
    } else if (missing.length <= 2 && pass.length >= 4) {
      label = 'Medium';
      color = '#F59E0B';
      score = 2;
    } else {
      label = 'Weak';
      color = '#EF4444';
      score = 1;
    }

    let message = '';
    if (isValid) {
      message = 'valid password ✓';
    } else if (missing.length === 1) {
      message = `Add ${missing[0]}.`;
    } else if (missing.length === 2) {
      message = `Add ${missing[0]} and ${missing[1]}.`;
    } else {
      const last = missing[missing.length - 1];
      const initial = missing.slice(0, -1).join(', ');
      message = `Add ${initial}, and ${last}.`;
    }

    return {
      isValid,
      message,
      label,
      color,
      score
    };
  };

  const validation = getPasswordValidation(password);
  const passwordsMatch = password && confirmPassword && password === confirmPassword;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validation.isValid) {
      setSignUpError(validation.message);
      return;
    }
    if (password !== confirmPassword) {
      setSignUpError('Passwords do not match. Please verify your entries.');
      return;
    }

    setSignUpError('');
    setIsSubmitting(true);

    try {
      const data = await signUpUser(email, password, fullName);
      setIsSubmitting(false);
      if (data?.session) {
        if (onLoginSuccess) {
          onLoginSuccess(data.session);
        } else {
          onNavigate('dashboard');
        }
      } else {
        onNavigate('account-created');
      }
    } catch (err) {
      setIsSubmitting(false);
      console.error('Sign up error:', err);
      const rawMsg = err.message || '';
      setSignUpError(rawMsg || 'Failed to create account. Please try again.');
    }
  };

  return (
    <div className="auth-page-container animate-fade-in">
      <div className="auth-header">
        <h1 className="auth-title">
          Join us<br />Now!!
        </h1>
        <p className="auth-subtitle">Let's Create your account.</p>
      </div>

      {signUpError && (
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
          <span>{signUpError}</span>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Full Name</label>
          <div className="input-wrapper">
            <input
              type="text"
              className="form-input"
              placeholder="enter your name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Email</label>
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

        <div className="form-group" style={{ marginBottom: '16px' }}>
          <label className="form-label">Password</label>
          <div className="input-wrapper">
            <input
              type={showPassword ? 'text' : 'password'}
              className="form-input"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              style={{ paddingRight: '42px' }}
            />
            <button
              type="button"
              className="input-icon-right"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          {password && (
            <div style={{ marginTop: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', fontWeight: '700', marginBottom: '4px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Strength:</span>
                <span style={{ color: validation.color }}>{validation.label}</span>
              </div>
              <div style={{ width: '100%', height: '4px', background: '#E2E8F0', borderRadius: '2px', overflow: 'hidden', marginBottom: '8px' }}>
                <div style={{
                  width: `${(validation.score / 3) * 100}%`,
                  height: '100%',
                  background: validation.color,
                  transition: 'all 0.3s ease'
                }} />
              </div>

              <div style={{
                fontSize: '12px',
                fontWeight: '600',
                color: validation.isValid ? '#059669' : '#D97706',
                background: validation.isValid ? '#ECFDF5' : '#FFFBEB',
                border: `1px solid ${validation.isValid ? '#A7F3D0' : '#FDE68A'}`,
                borderRadius: 'var(--radius-md)',
                padding: '8px 12px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                transition: 'all 0.2s ease'
              }}>
                {validation.isValid ? (
                  <CheckCircle2 size={15} style={{ color: '#059669', flexShrink: 0 }} />
                ) : (
                  <Info size={15} style={{ color: '#D97706', flexShrink: 0 }} />
                )}
                <span>{validation.message}</span>
              </div>
            </div>
          )}
        </div>

        <div className="form-group" style={{ marginBottom: '20px' }}>
          <label className="form-label">Confirm Password</label>
          <div className="input-wrapper">
            <input
              type={showConfirmPassword ? 'text' : 'password'}
              className="form-input"
              placeholder="enter your password again"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={6}
              style={{ paddingRight: '42px' }}
            />
            <button
              type="button"
              className="input-icon-right"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            >
              {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          {confirmPassword && (
            <div style={{ marginTop: '6px', fontSize: '11.5px', fontWeight: '700', color: passwordsMatch ? '#059669' : '#DC2626', display: 'flex', alignItems: 'center', gap: '4px' }}>
              {passwordsMatch ? (
                <>
                  <ShieldCheck size={14} /> Passwords match successfully
                </>
              ) : (
                'Passwords do not match yet'
              )}
            </div>
          )}
        </div>

        <button
          type="submit"
          className="btn-primary-burgundy"
          disabled={isSubmitting || (password ? (!validation.isValid || !passwordsMatch) : false)}
          style={{ opacity: isSubmitting || (password && (!validation.isValid || !passwordsMatch)) ? 0.65 : 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
        >
          {isSubmitting ? <><Loader2 className="animate-spin" size={18} /> Creating Account...</> : 'Sign up'}
        </button>
      </form>

      <div className="auth-footer-text">
        Already have An Account?{' '}
        <a
          href="#login"
          className="auth-footer-link"
          onClick={(e) => {
            e.preventDefault();
            onNavigate('login');
          }}
        >
          Sign-in
        </a>
      </div>
    </div>
  );
}
