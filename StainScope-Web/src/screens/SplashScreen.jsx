import React from 'react';
import { Microscope } from 'lucide-react';

export default function SplashScreen({ onNavigate }) {
  return (
    <div className="splash-container animate-fade-in">
      <div className="splash-microscope-graphic">
        {/* SVG representation of microscope optics & red stained cell matrix */}
        <svg width="280" height="280" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="0.5" style={{ opacity: 0.35, color: '#EF4444' }}>
          <circle cx="12" cy="12" r="10" strokeDasharray="2,2" />
          <circle cx="12" cy="12" r="6" stroke="#DC2626" strokeWidth="1" />
          <path d="M12 2v4M12 18v4M2 12h4M18 12h4" stroke="#F87171" strokeWidth="1" />
          <polygon points="12,7 15,12 12,17 9,12" fill="rgba(220,38,38,0.2)" stroke="#EF4444" />
        </svg>
      </div>

      <div className="splash-content">
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 14px',
          borderRadius: '20px',
          background: 'rgba(128, 29, 30, 0.4)',
          border: '1px solid rgba(239, 68, 68, 0.4)',
          color: '#FECACA',
          fontSize: '12px',
          fontWeight: '600',
          marginBottom: '20px',
          backdropFilter: 'blur(4px)'
        }}>
          <Microscope size={14} color="#EF4444" /> AI-Powered Stain Quantification
        </div>

        <h1 className="splash-title">
          Welcome to <span className="splash-title-highlight">StainScope</span>
        </h1>

        <p className="splash-subtitle">
          Join over 10,000 researchers worldwide and accelerate your osteogenesis & calcium matrix analysis!
        </p>

        <button 
          className="splash-btn-white"
          onClick={() => onNavigate('signup')}
        >
          Create an account
        </button>

        <div className="splash-footer-link">
          Already have an account? 
          <span onClick={() => onNavigate('login')}>Log in</span>
        </div>
      </div>
    </div>
  );
}
