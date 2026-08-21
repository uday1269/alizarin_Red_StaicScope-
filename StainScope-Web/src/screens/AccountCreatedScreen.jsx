import React from 'react';
import { CheckCircle2, ShieldCheck, ArrowRight, Sparkles, Microscope } from 'lucide-react';

export default function AccountCreatedScreen({ onNavigate }) {
  return (
    <div className="account-created-page-wrapper animate-fade-in">
      {/* Subtle scientific background reticles for visual depth */}
      <div className="account-created-bg-reticle" style={{ top: '40px', left: '40px' }}>
        <Microscope size={32} />
      </div>
      <div className="account-created-bg-reticle" style={{ bottom: '40px', right: '40px' }}>
        <Microscope size={32} />
      </div>

      <div className="account-created-card">
        {/* Supporting badge */}
        <div className="account-created-pill">
          <Sparkles size={14} />
          <span>Your workspace is ready</span>
        </div>

        {/* Animated Check Circle Icon */}
        <div className="account-created-icon-badge">
          <CheckCircle2 size={48} strokeWidth={2.5} />
        </div>

        {/* Main Header */}
        <div className="auth-header" style={{ marginBottom: '24px', textAlign: 'center' }}>
          <h1 className="auth-title" style={{ fontSize: '28px', marginBottom: '8px' }}>
            Account Created!
          </h1>
          <p className="auth-subtitle" style={{ maxWidth: '420px', margin: '0 auto', lineHeight: '1.55' }}>
            Your scientific workstation account has been configured for automated Alizarin Red S stain quantification.
          </p>
        </div>

        {/* Verified Researcher Info Box */}
        <div className="account-created-info-box">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '700', color: 'var(--primary-burgundy)', marginBottom: '10px', fontSize: '14px' }}>
            <ShieldCheck size={18} /> Verified Researcher Account
          </div>
          <div style={{ color: 'var(--text-muted)', lineHeight: '1.6', fontSize: '13.5px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px', marginBottom: '6px' }}>
              <span>Authentication Status:</span>
              <strong style={{ color: '#059669' }}>Supabase Auth Verified</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
              <span>Default Stain Matrix:</span>
              <strong style={{ color: 'var(--text-dark)' }}>Alizarin Red S (2% Solution)</strong>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <button 
          className="btn-primary-burgundy"
          style={{ width: '100%', height: '48px', fontSize: '15px', justifyContent: 'center', gap: '8px' }}
          onClick={() => onNavigate('login')}
        >
          Continue to Sign In <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );
}
