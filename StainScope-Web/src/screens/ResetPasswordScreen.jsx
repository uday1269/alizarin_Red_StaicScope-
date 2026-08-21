import React, { useState } from 'react';
import { Lock, Eye, EyeOff, CheckCircle2, ShieldCheck, ArrowLeft, Info } from 'lucide-react';

export default function ResetPasswordScreen({ onNavigate }) {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showNewPass, setShowNewPass] = useState(false);
  const [showConfirmPass, setShowConfirmPass] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

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

  const validation = getPasswordValidation(newPassword);
  const passwordsMatch = newPassword && confirmPassword && newPassword === confirmPassword;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!newPassword || !confirmPassword) return;

    if (!validation.isValid) {
      alert(validation.message);
      return;
    }

    if (newPassword !== confirmPassword) {
      alert('Passwords do not match. Please verify your entries.');
      return;
    }

    setIsSubmitting(true);
    setSuccessMessage('Password reset successful! Returning to Sign In...');

    setTimeout(() => {
      onNavigate('login');
    }, 1200);
  };

  return (
    <div className="auth-page-container animate-fade-in">
      <div className="auth-header">
        <div style={{
          width: '48px',
          height: '48px',
          borderRadius: '14px',
          background: 'var(--primary-burgundy-light)',
          color: 'var(--primary-burgundy)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '16px'
        }}>
          <Lock size={24} />
        </div>
        <h1 className="auth-title">
          Reset Password
        </h1>
        <p className="auth-subtitle">
          Create a new secure password for <strong style={{ color: 'var(--text-dark)' }}>your account</strong>
        </p>
      </div>

      {successMessage && (
        <div style={{
          background: '#ECFDF5',
          border: '1px solid #A7F3D0',
          color: '#047857',
          padding: '12px 16px',
          borderRadius: 'var(--radius-md)',
          marginBottom: '20px',
          fontSize: '13px',
          fontWeight: '700',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <CheckCircle2 size={16} /> {successMessage}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* New Password Field */}
        <div className="form-group" style={{ marginBottom: '16px' }}>
          <label className="form-label">New Password</label>
          <div style={{ position: 'relative' }}>
            <input
              type={showNewPass ? 'text' : 'password'}
              className="form-input"
              placeholder="Enter new password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              minLength={6}
              style={{ paddingRight: '42px' }}
            />
            <button
              type="button"
              onClick={() => setShowNewPass(!showNewPass)}
              style={{
                position: 'absolute',
                right: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                padding: '4px'
              }}
            >
              {showNewPass ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          {/* Password Strength Bar & Compact Dynamic Validation Feedback */}
          {newPassword && (
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

              {/* Dynamic Missing Requirement Badge */}
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

        {/* Confirm Password Field */}
        <div className="form-group" style={{ marginBottom: '24px' }}>
          <label className="form-label">Confirm New Password</label>
          <div style={{ position: 'relative' }}>
            <input
              type={showConfirmPass ? 'text' : 'password'}
              className="form-input"
              placeholder="Re-enter new password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={6}
              style={{ paddingRight: '42px' }}
            />
            <button
              type="button"
              onClick={() => setShowConfirmPass(!showConfirmPass)}
              style={{
                position: 'absolute',
                right: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                padding: '4px'
              }}
            >
              {showConfirmPass ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          {/* Match validation status indicator */}
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

        {/* Submit Button */}
        <button
          type="submit"
          className="btn-primary-burgundy"
          disabled={isSubmitting || (newPassword ? (!validation.isValid || !passwordsMatch) : false)}
          style={{ opacity: isSubmitting || (newPassword && (!validation.isValid || !passwordsMatch)) ? 0.65 : 1 }}
        >
          {isSubmitting ? 'Updating Password & Logging in...' : 'Reset Password & Sign In'}
        </button>
      </form>

      <div style={{ marginTop: '20px', textAlign: 'center' }}>
        <button
          type="button"
          onClick={() => onNavigate('otp')}
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
          <ArrowLeft size={16} /> Back to OTP Verification
        </button>
      </div>
    </div>
  );
}
