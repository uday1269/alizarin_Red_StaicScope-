import React from 'react';
import { Monitor, Tablet, Smartphone, Layers } from 'lucide-react';

export default function ScreenSwitcher({ activeScreen, onSelectScreen, deviceView, onSelectDevice }) {
  const screens = [
    { id: 'splash', label: '1. Splash' },
    { id: 'login', label: '2. Login' },
    { id: 'signup', label: '3. Sign Up' },
    { id: 'forgot-password', label: '4. Forgot Pass' },
    { id: 'otp', label: '5. OTP' },
    { id: 'reset-password', label: '6. Reset Pass' },
    { id: 'account-created', label: '7. Created' },
    { id: 'dashboard', label: '8. Home' },
    { id: 'upload', label: '9. Upload' },
    { id: 'processing', label: '10. Processing' },
    { id: 'results', label: '11. Results' },
    { id: 'compare', label: '12. Compare' },
    { id: 'reports', label: '13. Reports' },
    { id: 'profile', label: '14. Profile' },
  ];

  return (
    <div className="screen-switcher-bar">
      <div className="screen-switcher-title">
        <Layers size={16} />
        <span>StainScope Screens:</span>
      </div>

      <div className="screen-switcher-pills">
        {screens.map((scr) => (
          <button
            key={scr.id}
            className={`screen-pill-btn ${activeScreen === scr.id ? 'active' : ''}`}
            onClick={() => onSelectScreen(scr.id)}
          >
            {scr.label}
          </button>
        ))}
      </div>

      <div className="device-view-switcher">
        <button
          className={`device-btn ${deviceView === 'desktop' ? 'active' : ''}`}
          onClick={() => onSelectDevice('desktop')}
          title="Desktop view"
        >
          <Monitor size={14} /> Desktop
        </button>
        <button
          className={`device-btn ${deviceView === 'tablet' ? 'active' : ''}`}
          onClick={() => onSelectDevice('tablet')}
          title="Tablet view"
        >
          <Tablet size={14} /> Tablet
        </button>
        <button
          className={`device-btn ${deviceView === 'mobile' ? 'active' : ''}`}
          onClick={() => onSelectDevice('mobile')}
          title="Mobile view"
        >
          <Smartphone size={14} /> Mobile
        </button>
      </div>
    </div>
  );
}
