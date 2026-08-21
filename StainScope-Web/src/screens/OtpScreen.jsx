import React, { useState, useRef } from 'react';
import { ArrowLeft, KeyRound } from 'lucide-react';

export default function OtpScreen({ onNavigate }) {
  const [otp, setOtp] = useState(['4', '8', '2', '9']);
  const [resendAlert, setResendAlert] = useState('');
  const inputRefs = [useRef(), useRef(), useRef(), useRef()];

  const handleChange = (index, value) => {
    if (value.length > 1) value = value.slice(-1);
    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    if (value && index < 3) {
      inputRefs[index + 1].current.focus();
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs[index - 1].current.focus();
    }
  };

  const handleResendOtp = () => {
    // TODO: Backend integration - POST /api/v1/auth/resend-otp
    setResendAlert('A new 4-digit OTP code has been dispatched to your email');
    setTimeout(() => setResendAlert(''), 4000);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Backend integration - POST /api/v1/auth/verify-otp
    onNavigate('reset-password');
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
          <KeyRound size={24} />
        </div>
        <h1 className="auth-title">
          OTP Verification
        </h1>
        <p className="auth-subtitle">
          Enter the 4-digit code sent to <strong style={{ color: 'var(--text-dark)' }}>your registered email</strong>
        </p>
      </div>

      {resendAlert && (
        <div style={{
          background: 'var(--primary-burgundy-light)',
          border: '1px solid var(--primary-burgundy-border)',
          color: 'var(--primary-burgundy)',
          padding: '10px 14px',
          borderRadius: 'var(--radius-md)',
          fontSize: '12.5px',
          fontWeight: '700',
          marginBottom: '16px',
          textAlign: 'center'
        }}>
          {resendAlert}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginBottom: '24px' }}>
          {otp.map((digit, idx) => (
            <input
              key={idx}
              ref={inputRefs[idx]}
              type="text"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onChange={(e) => handleChange(idx, e.target.value)}
              onKeyDown={(e) => handleKeyDown(idx, e)}
              style={{
                width: '56px',
                height: '60px',
                borderRadius: '14px',
                border: '1.5px solid ' + (digit ? 'var(--primary-burgundy)' : 'var(--border-light)'),
                fontSize: '22px',
                fontWeight: '700',
                textAlign: 'center',
                color: 'var(--text-dark)',
                outline: 'none',
                background: digit ? 'var(--primary-burgundy-light)' : '#FFFFFF',
                boxShadow: digit ? '0 0 0 3px rgba(128, 29, 30, 0.1)' : 'none',
                transition: 'all 0.2s ease'
              }}
              required
            />
          ))}
        </div>

        <div style={{ textAlign: 'center', fontSize: '13px', color: 'var(--text-muted)', marginBottom: '24px' }}>
          Didn't receive the code?{' '}
          <button
            type="button"
            onClick={handleResendOtp}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--primary-burgundy)',
              fontWeight: '700',
              cursor: 'pointer'
            }}
          >
            Resend OTP
          </button>
        </div>

        <button type="submit" className="btn-primary-burgundy">
          Verify &amp; Proceed
        </button>
      </form>

      <div style={{ marginTop: '16px', textAlign: 'center' }}>
        <button
          type="button"
          onClick={() => onNavigate('forgot-password')}
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
          <ArrowLeft size={16} /> Back
        </button>
      </div>
    </div>
  );
}
