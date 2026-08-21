import React from 'react';
import { Microscope, LayoutDashboard, UploadCloud, GitCompare, History, FileText, User, LogOut } from 'lucide-react';

export default function TopNav({ activeScreen, onNavigate, onLogout, userProfile }) {
  const navItems = [
    { id: 'dashboard', label: 'Home', icon: LayoutDashboard },
    { id: 'upload', label: 'Upload & Analyze', icon: UploadCloud },
    { id: 'compare', label: 'Compare', icon: GitCompare },
    { id: 'reports', label: 'Reports', icon: FileText },
    { id: 'profile', label: 'Profile', icon: User },
  ];

  const displayName = userProfile?.full_name || 'Researcher';
  const initials = displayName.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() || 'RS';

  return (
    <header className="app-navbar">
      <div className="navbar-brand" onClick={() => onNavigate('dashboard')}>
        <div className="navbar-brand-icon">
          <Microscope size={20} />
        </div>
        <span>Stain<span style={{ color: '#801D1E' }}>Scope</span></span>
      </div>

      <nav className="navbar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeScreen === item.id || 
            (item.id === 'upload' && (activeScreen === 'processing' || activeScreen === 'results'));
          return (
            <button
              key={item.id}
              className={`nav-link-btn ${isActive ? 'active' : ''}`}
              onClick={() => onNavigate(item.id)}
            >
              <Icon size={16} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="navbar-user-profile">
        <div className="user-avatar-circle" title={displayName} onClick={() => onNavigate('profile')} style={{ cursor: 'pointer' }}>
          {initials}
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', fontSize: '13px' }}>
          <span style={{ fontWeight: '700', color: 'var(--text-dark)', lineHeight: '1.2' }}>{displayName}</span>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{userProfile?.lab_name || 'Regenerative Medicine Lab'}</span>
        </div>
        <button 
          onClick={onLogout || (() => onNavigate('login'))}
          style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '6px', marginLeft: '6px' }}
          title="Log out of workstation"
        >
          <LogOut size={16} />
        </button>
      </div>
    </header>
  );
}
