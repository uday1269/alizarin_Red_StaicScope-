import React, { useState, useEffect } from 'react';
import { 
  Star, 
  GitCompare, 
  Download, 
  Sun, 
  Moon, 
  HelpCircle, 
  Info, 
  BookOpen, 
  Plus, 
  Activity, 
  Edit3, 
  BookMarked,
  LogOut,
  X,
  Trash2,
  RotateCcw,
  Clock
} from 'lucide-react';
import { fetchProfile, updateProfile, createNote } from '../api';

export default function ProfileScreen({
  onNavigate,
  onLogout,
  analysesHistory,
  userProfile,
  savedNotes: propNotes,
  onSaveNote,
  onDeleteNote,
  savedComparisons: propComparisons,
  onDeleteComparison,
  recentlyDeleted: propRecentlyDeleted,
  onRestoreItem,
  theme: propTheme,
  onThemeChange
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [userName, setUserName] = useState(userProfile?.full_name || 'Researcher');
  const [userRole, setUserRole] = useState(userProfile?.role || 'Bone Tissue Researcher');
  const [userDept, setUserDept] = useState(userProfile?.lab_name || 'Regenerative Medicine & Tissue Engineering');
  const [userInst, setUserInst] = useState(userProfile?.institution || 'BioMed Research Institute');
  const userEmail = userProfile?.email || 'researcher@stainscope.org';

  useEffect(() => {
    if (userProfile) {
      if (userProfile.full_name) setUserName(userProfile.full_name);
      if (userProfile.role) setUserRole(userProfile.role);
      if (userProfile.institution) setUserInst(userProfile.institution);
      if (userProfile.lab_name) setUserDept(userProfile.lab_name);
    }
  }, [userProfile]);

  const handleToggleEdit = async () => {
    if (isEditing) {
      // Save updated profile to Supabase backend
      await updateProfile({
        full_name: userName,
        role: userRole,
        institution: userInst,
        lab_name: userDept
      });
    }
    setIsEditing(!isEditing);
  };

  // Theme selection ('light' | 'dark')
  const [localTheme, setLocalTheme] = useState('light');
  const activeTheme = propTheme || localTheme;

  const handleThemeSelect = (newTheme) => {
    setLocalTheme(newTheme);
    if (onThemeChange) {
      onThemeChange(newTheme);
    }
  };

  // Export Preferences
  const [exportFormat, setExportFormat] = useState('PDF (Vector + Charts)');
  const [incOriginal, setIncOriginal] = useState(true);
  const [incSegmentation, setIncSegmentation] = useState(true);
  const [incHeatmap, setIncHeatmap] = useState(true);
  const [incStats, setIncStats] = useState(true);

  // Notes state fallback
  const notes = propNotes || [];
  const [newNoteTitle, setNewNoteTitle] = useState('');
  const [newNoteContent, setNewNoteContent] = useState('');
  const [showNoteModal, setShowNoteModal] = useState(false);

  const handleAddNote = async (e) => {
    e.preventDefault();
    if (!newNoteTitle) return;
    const noteObj = {
      id: Date.now().toString(),
      title: newNoteTitle,
      date: new Date().toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }),
      content: newNoteContent
    };

    // Save note to Supabase backend
    const savedBackendNote = await createNote(newNoteTitle, newNoteContent);
    if (savedBackendNote && savedBackendNote.id) {
      noteObj.id = savedBackendNote.id;
    }

    if (onSaveNote) {
      onSaveNote(noteObj);
    }
    setNewNoteTitle('');
    setNewNoteContent('');
    setShowNoteModal(false);
  };

  // Comparisons fallback
  const comparisons = propComparisons || [
    {
      id: 'comp-1',
      title: 'Control vs Treatment (Day 14 vs Day 21)',
      subtitle: 'STAIN-8091 vs STAIN-8092 (+25.6% Delta)'
    },
    {
      id: 'comp-2',
      title: 'GelMA Hydrogel 3D vs Monolayer',
      subtitle: 'STAIN-8089 vs STAIN-8088 (+22.3% Delta)'
    }
  ];

  // Retention days calculation (28 days retention)
  const calculateDaysRemaining = (deletedTimeInput) => {
    const RETENTION_MS = 28 * 24 * 60 * 60 * 1000;
    const deletedTime = typeof deletedTimeInput === 'number' 
      ? deletedTimeInput 
      : (deletedTimeInput ? new Date(deletedTimeInput).getTime() : Date.now());
    const validTime = isNaN(deletedTime) ? Date.now() : deletedTime;
    const elapsedMs = Date.now() - validTime;
    const remainingMs = RETENTION_MS - elapsedMs;
    const days = Math.ceil(remainingMs / (1000 * 60 * 60 * 24));
    return Math.max(0, days);
  };

  const activeRecentlyDeleted = (propRecentlyDeleted || []).filter(
    (item) => calculateDaysRemaining(item.deletedTimestamp || item.deletedAt) > 0
  );

  return (
    <div className="animate-fade-in" style={{ padding: '24px 24px 48px', maxWidth: '1180px', margin: '0 auto' }}>
      
      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontSize: '26px', fontWeight: '800', color: 'var(--text-dark)' }}>
          Researcher Profile &amp; Workstation Settings
        </h1>
        <p style={{ fontSize: '14px', color: 'var(--text-muted)' }}>
          Manage your research profile, activity metrics, pinned samples, lab observations, and export preferences.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '28px' }}>
        
        {/* Left Column: Researcher Card & Activity Summary */}
        <div>
          {/* 👤 Researcher Profile Card */}
          <div style={{
            background: '#FFFFFF',
            borderRadius: 'var(--radius-xl)',
            border: '1px solid var(--border-light)',
            padding: '28px',
            boxShadow: 'var(--shadow-sm)',
            marginBottom: '28px',
            position: 'relative'
          }}>
            <button
              onClick={handleToggleEdit}
              style={{
                position: 'absolute',
                top: '20px',
                right: '20px',
                background: isEditing ? 'var(--primary-burgundy-light)' : 'var(--bg-light-app)',
                color: isEditing ? 'var(--primary-burgundy)' : 'var(--text-dark)',
                border: '1px solid var(--border-light)',
                padding: '6px 12px',
                borderRadius: 'var(--radius-md)',
                fontSize: '12px',
                fontWeight: '700',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <Edit3 size={14} /> {isEditing ? 'Done Editing' : 'Edit Profile'}
            </button>

            <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '20px' }}>
              <div style={{
                width: '76px',
                height: '76px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #801D1E 0%, #B91C1C 100%)',
                color: '#FFFFFF',
                fontSize: '26px',
                fontWeight: '800',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: '4px solid #FFFFFF',
                boxShadow: '0 8px 20px rgba(128, 29, 30, 0.3)'
              }}>
                {userName.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() || 'RS'}
              </div>

              <div>
                <h2 style={{ fontSize: '20px', fontWeight: '800', color: 'var(--text-dark)', marginBottom: '2px' }}>
                  {userName}
                </h2>
                <p style={{ fontSize: '13px', color: 'var(--primary-burgundy)', fontWeight: '700' }}>
                  {userRole}
                </p>
                <p style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>
                  {userEmail}
                </p>
              </div>
            </div>

            {isEditing ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', paddingTop: '10px', borderTop: '1px solid #F1F5F9' }}>
                <div className="form-group">
                  <label className="form-label">Full Name</label>
                  <input type="text" className="form-input" value={userName} onChange={(e) => setUserName(e.target.value)} />
                </div>
                <div className="form-group">
                  <label className="form-label">Role</label>
                  <select className="form-input" value={userRole} onChange={(e) => setUserRole(e.target.value)}>
                    <option>Senior Bone Tissue Engineer</option>
                    <option>Faculty Researcher</option>
                    <option>Postdoctoral Fellow</option>
                    <option>Graduate Student Researcher</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Department</label>
                  <input type="text" className="form-input" value={userDept} onChange={(e) => setUserDept(e.target.value)} />
                </div>
                <div className="form-group">
                  <label className="form-label">Institution</label>
                  <input type="text" className="form-input" value={userInst} onChange={(e) => setUserInst(e.target.value)} />
                </div>
              </div>
            ) : (
              <div style={{
                background: 'var(--bg-light-app)',
                borderRadius: 'var(--radius-lg)',
                padding: '14px 16px',
                fontSize: '13px',
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '10px'
              }}>
                <div>
                  <span style={{ color: 'var(--text-muted)', fontSize: '11px', display: 'block' }}>INSTITUTION</span>
                  <strong>{userInst}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)', fontSize: '11px', display: 'block' }}>DEPARTMENT</span>
                  <strong>{userDept}</strong>
                </div>
              </div>
            )}
          </div>

          {/* 📊 Activity Summary Section */}
          <div style={{
            background: '#FFFFFF',
            borderRadius: 'var(--radius-xl)',
            border: '1px solid var(--border-light)',
            padding: '24px',
            boxShadow: 'var(--shadow-sm)',
            marginBottom: '28px'
          }}>
            <h3 style={{ fontSize: '16px', fontWeight: '800', color: 'var(--text-dark)', marginBottom: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Activity size={18} color="var(--primary-burgundy)" /> Research Activity Summary
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
              <div style={{ background: '#F8FAFC', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-light)' }}>
                <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)' }}>TOTAL ANALYSES</span>
                <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--text-dark)', marginTop: '2px' }}>
                  {(analysesHistory || []).length}
                </div>
              </div>

              <div style={{ background: '#F8FAFC', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-light)' }}>
                <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)' }}>IMAGES PROCESSED</span>
                <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--primary-burgundy)', marginTop: '2px' }}>{(analysesHistory || []).length}</div>
              </div>

              <div style={{ background: '#F8FAFC', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-light)' }}>
                <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)' }}>REPORTS GENERATED</span>
                <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--text-dark)', marginTop: '2px' }}>
                  {(analysesHistory || []).length}
                </div>
              </div>

              <div style={{ background: '#F8FAFC', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-light)' }}>
                <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)' }}>SAVED COMPARISONS</span>
                <div style={{ fontSize: '24px', fontWeight: '800', color: '#059669', marginTop: '2px' }}>
                  {comparisons.length}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: 'var(--text-muted)', marginTop: '16px', paddingTop: '12px', borderTop: '1px solid #F1F5F9' }}>
              <span>Last Analysis: <strong>{(analysesHistory || [])[0]?.date || 'None'}</strong></span>
              <span>Backend Engine: <strong>Classical CV v1.0</strong></span>
            </div>
          </div>

          {/* ⭐ Favorite Samples Pinned */}
          <div style={{
            background: '#FFFFFF',
            borderRadius: 'var(--radius-xl)',
            border: '1px solid var(--border-light)',
            padding: '24px',
            boxShadow: 'var(--shadow-sm)',
            marginBottom: '28px'
          }}>
            <h3 style={{ fontSize: '16px', fontWeight: '800', color: 'var(--text-dark)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Star size={18} fill="#F59E0B" color="#F59E0B" /> Recent Analyzed Samples
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {(analysesHistory || []).slice(0, 2).map((sample) => (
                <div key={sample.id} style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '12px 14px',
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--bg-light-app)',
                  border: '1px solid var(--border-light)'
                }}>
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-dark)' }}>{sample.title.split('-')[0]}</div>
                    <div style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>ID: {sample.id} • Area: <strong style={{ color: 'var(--primary-burgundy)' }}>{sample.mineralizedArea}</strong></div>
                  </div>

                  <button
                    onClick={() => onNavigate('results', { analysis: sample })}
                    className="hover-lift"
                    style={{
                      background: 'var(--primary-burgundy-light)',
                      color: 'var(--primary-burgundy)',
                      border: 'none',
                      padding: '6px 12px',
                      borderRadius: 'var(--radius-md)',
                      fontSize: '12px',
                      fontWeight: '700',
                      cursor: 'pointer'
                    }}
                  >
                    Quick Open
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Saved Comparisons, Research Notes, Export Preferences & Help */}
        <div>
          {/* 🔬 Saved Comparisons */}
          <div style={{
            background: '#FFFFFF',
            borderRadius: 'var(--radius-xl)',
            border: '1px solid var(--border-light)',
            padding: '24px',
            boxShadow: 'var(--shadow-sm)',
            marginBottom: '28px'
          }}>
            <h3 style={{ fontSize: '16px', fontWeight: '800', color: 'var(--text-dark)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <GitCompare size={18} color="var(--primary-burgundy)" /> Saved Differential Comparisons
            </h3>

            {comparisons.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {comparisons.map((comp) => (
                  <div key={comp.id} style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 14px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--bg-light-app)',
                    border: '1px solid var(--border-light)'
                  }}>
                    <div>
                      <div style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-dark)' }}>{comp.title}</div>
                      <div style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>{comp.subtitle}</div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <button
                        onClick={() => onNavigate('compare')}
                        style={{ background: 'var(--primary-burgundy-light)', color: 'var(--primary-burgundy)', border: '1px solid var(--primary-burgundy-border)', padding: '6px 12px', borderRadius: '6px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}
                      >
                        Reopen
                      </button>
                      <button
                        onClick={() => onDeleteComparison && onDeleteComparison(comp.id)}
                        title="Move to Recently Deleted"
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: 'var(--text-muted)',
                          cursor: 'pointer',
                          padding: '4px',
                          borderRadius: '4px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}
                      >
                        <X size={15} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ fontSize: '12.5px', color: 'var(--text-muted)', textAlign: 'center', padding: '12px' }}>
                No saved comparisons.
              </div>
            )}
          </div>

          {/* 📝 Research Notes */}
          <div style={{
            background: '#FFFFFF',
            borderRadius: 'var(--radius-xl)',
            border: '1px solid var(--border-light)',
            padding: '24px',
            boxShadow: 'var(--shadow-sm)',
            marginBottom: '28px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: '800', color: 'var(--text-dark)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BookMarked size={18} color="var(--primary-burgundy)" /> Lab Research Notebook Notes
              </h3>
              <button
                onClick={() => setShowNoteModal(true)}
                style={{ background: 'var(--primary-burgundy-light)', color: 'var(--primary-burgundy)', border: 'none', padding: '4px 10px', borderRadius: '6px', fontSize: '12px', fontWeight: '700', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}
              >
                <Plus size={14} /> Add Note
              </button>
            </div>

            {notes.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {notes.map((note) => (
                  <div key={note.id} style={{
                    background: '#FEFCE8',
                    border: '1px solid #FEF08A',
                    borderRadius: 'var(--radius-md)',
                    padding: '14px',
                    position: 'relative'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '4px' }}>
                      <strong style={{ fontSize: '13.5px', color: '#854D0E', paddingRight: '20px' }}>{note.title}</strong>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '11px', color: '#A16207' }}>{note.date}</span>
                        <button
                          onClick={() => onDeleteNote && onDeleteNote(note.id)}
                          title="Move to Recently Deleted"
                          style={{
                            background: 'transparent',
                            border: 'none',
                            color: '#A16207',
                            cursor: 'pointer',
                            padding: '2px',
                            borderRadius: '4px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}
                        >
                          <X size={15} />
                        </button>
                      </div>
                    </div>
                    <p style={{ fontSize: '12.5px', color: '#713F12', lineHeight: '1.4' }}>{note.content}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ fontSize: '12.5px', color: 'var(--text-muted)', textAlign: 'center', padding: '12px' }}>
                No active research notes.
              </div>
            )}
          </div>

          {/* 📄 Export Preferences */}
          <div style={{
            background: '#FFFFFF',
            borderRadius: 'var(--radius-xl)',
            border: '1px solid var(--border-light)',
            padding: '24px',
            boxShadow: 'var(--shadow-sm)',
            marginBottom: '28px'
          }}>
            <h3 style={{ fontSize: '16px', fontWeight: '800', color: 'var(--text-dark)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Download size={18} color="var(--primary-burgundy)" /> Default Export Preferences
            </h3>

            <div className="form-group" style={{ marginBottom: '16px' }}>
              <label className="form-label">Preferred Report Export Format</label>
              <select className="form-input" value={exportFormat} onChange={(e) => setExportFormat(e.target.value)}>
                <option>PDF (Vector + Charts)</option>
                <option>CSV Raw Quantitative Data</option>
              </select>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '12.5px', color: 'var(--text-dark)' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                <input type="checkbox" checked={incOriginal} onChange={(e) => setIncOriginal(e.target.checked)} style={{ accentColor: 'var(--primary-burgundy)' }} /> Include Original Image
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                <input type="checkbox" checked={incSegmentation} onChange={(e) => setIncSegmentation(e.target.checked)} style={{ accentColor: 'var(--primary-burgundy)' }} /> Include AI Segmentation
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                <input type="checkbox" checked={incHeatmap} onChange={(e) => setIncHeatmap(e.target.checked)} style={{ accentColor: 'var(--primary-burgundy)' }} /> Include HSV Heatmap
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                <input type="checkbox" checked={incStats} onChange={(e) => setIncStats(e.target.checked)} style={{ accentColor: 'var(--primary-burgundy)' }} /> Include Statistics Table
              </label>
            </div>
          </div>

          {/* 🎨 Interface Theme Mode (Dedicated Card) */}
          <div style={{
            background: '#FFFFFF',
            borderRadius: 'var(--radius-xl)',
            border: '1px solid var(--border-light)',
            padding: '24px',
            boxShadow: 'var(--shadow-sm)',
            marginBottom: '28px'
          }}>
            <h3 style={{ fontSize: '16px', fontWeight: '800', color: 'var(--text-dark)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sun size={18} color="var(--primary-burgundy)" /> Interface Theme Mode
            </h3>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={() => handleThemeSelect('light')}
                style={{
                  flex: 1,
                  background: activeTheme === 'light' ? 'var(--primary-burgundy-light)' : 'var(--bg-card)',
                  color: activeTheme === 'light' ? 'var(--primary-burgundy)' : 'var(--text-dark)',
                  border: `1.5px solid ${activeTheme === 'light' ? 'var(--primary-burgundy)' : 'var(--border-light)'}`,
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '13px',
                  fontWeight: '700',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px'
                }}
              >
                <Sun size={16} /> Light Mode
              </button>

              <button
                onClick={() => handleThemeSelect('dark')}
                style={{
                  flex: 1,
                  background: activeTheme === 'dark' ? 'var(--primary-burgundy-light)' : 'var(--bg-card)',
                  color: activeTheme === 'dark' ? 'var(--primary-burgundy)' : 'var(--text-dark)',
                  border: `1.5px solid ${activeTheme === 'dark' ? 'var(--primary-burgundy)' : 'var(--border-light)'}`,
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '13px',
                  fontWeight: '700',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px'
                }}
              >
                <Moon size={16} /> Dark Mode
              </button>
            </div>
          </div>

          {/* ❓ Help & Support + ℹ️ Application Information */}
          <div style={{
            background: '#FFFFFF',
            borderRadius: 'var(--radius-xl)',
            border: '1px solid var(--border-light)',
            padding: '24px',
            boxShadow: 'var(--shadow-sm)'
          }}>
            <h3 style={{ fontSize: '16px', fontWeight: '800', color: 'var(--text-dark)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <HelpCircle size={18} color="var(--primary-burgundy)" /> Help, Support &amp; App Info
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '20px' }}>
              <a href="#guide" onClick={(e) => { e.preventDefault(); alert('StainScope User Guide: Alizarin Red S (2% pH 4.2) optical density calibration guide.'); }} style={{ textDecoration: 'none', background: '#F8FAFC', padding: '10px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-light)', fontSize: '12px', fontWeight: '700', color: 'var(--text-dark)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <BookOpen size={14} color="var(--primary-burgundy)" /> User Guide
              </a>

              <a href="#about-stain" onClick={(e) => { e.preventDefault(); alert('Alizarin Red S binds specifically to extracellular calcium cations forming red chelate complexes.'); }} style={{ textDecoration: 'none', background: '#F8FAFC', padding: '10px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-light)', fontSize: '12px', fontWeight: '700', color: 'var(--text-dark)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Info size={14} color="var(--primary-burgundy)" /> Alizarin Red S Info
              </a>
            </div>

            <button
              onClick={onLogout || (() => onNavigate('login'))}
              style={{
                width: '100%',
                background: '#FEF2F2',
                color: '#DC2626',
                border: '1px solid #FCA5A5',
                padding: '12px',
                borderRadius: 'var(--radius-md)',
                fontSize: '13px',
                fontWeight: '700',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                marginBottom: '20px'
              }}
            >
              <LogOut size={16} /> Sign Out of Workstation
            </button>

            <div style={{ fontSize: '12px', color: 'var(--text-muted)', paddingTop: '12px', borderTop: '1px solid #F1F5F9', display: 'flex', justifyContent: 'space-between' }}>
              <span>StainScope Version: <strong>v2.4.1 Production</strong></span>
              <span>Build: <strong>2026.08.07-STAIN</strong></span>
            </div>
          </div>
        </div>

      </div>

      {/* 🗑️ Recently Deleted Section (Recycle Bin System with 28-day retention) */}
      <div style={{
        background: '#FFFFFF',
        borderRadius: 'var(--radius-xl)',
        border: '1px solid var(--border-light)',
        padding: '24px',
        boxShadow: 'var(--shadow-sm)',
        marginTop: '28px'
      }}>
        <div style={{ marginBottom: '18px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '800', color: 'var(--text-dark)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Trash2 size={18} color="var(--primary-burgundy)" /> Recently Deleted (Recycle Bin)
          </h3>
          <p style={{ fontSize: '12.5px', color: 'var(--text-muted)', marginTop: '2px' }}>
            Items remain in Recently Deleted for 28 days before permanent automatic removal.
          </p>
        </div>

        {activeRecentlyDeleted.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '14px' }}>
            {activeRecentlyDeleted.map((item) => {
              const daysRemaining = calculateDaysRemaining(item.deletedTimestamp || item.deletedAt);
              const displayTitle = item.name || item.title || `Micrograph (${item.id.slice(0, 8)})`;
              const displayDate = item.deletedDate || item.deletedDateStr || item.date || 'Recent';
              const displayType = item.type || 'Result';
              return (
                <div
                  key={item.id}
                  style={{
                    background: '#F8FAFC',
                    border: '1px solid #E2E8F0',
                    borderRadius: 'var(--radius-lg)',
                    padding: '16px',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    gap: '12px'
                  }}
                >
                  <div>
                    <div style={{ fontSize: '13.5px', fontWeight: '700', color: 'var(--text-dark)', marginBottom: '4px' }}>
                      {displayTitle}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontSize: '11px',
                        fontWeight: '700',
                        background: (displayType === 'Analysis' || displayType === 'Result') ? 'rgba(128, 29, 30, 0.1)' : displayType === 'Note' ? 'rgba(245, 158, 11, 0.15)' : 'rgba(5, 150, 105, 0.1)',
                        color: (displayType === 'Analysis' || displayType === 'Result') ? 'var(--primary-burgundy)' : displayType === 'Note' ? '#D97706' : '#059669'
                      }}>
                        {displayType}
                      </span>
                      <span>• Deleted {displayDate}</span>
                    </div>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '10px', borderTop: '1px solid #E2E8F0' }}>
                    <div style={{ fontSize: '12px', fontWeight: '700', color: '#64748B', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Clock size={14} color="#94A3B8" /> {daysRemaining} days remaining
                    </div>

                    <button
                      onClick={() => onRestoreItem && onRestoreItem(item)}
                      style={{
                        background: 'var(--primary-burgundy-light)',
                        color: 'var(--primary-burgundy)',
                        border: '1px solid var(--primary-burgundy-border)',
                        padding: '6px 14px',
                        borderRadius: 'var(--radius-md)',
                        fontSize: '12px',
                        fontWeight: '700',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        transition: 'all 0.2s ease'
                      }}
                      className="hover-lift"
                    >
                      <RotateCcw size={14} /> Restore
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div style={{
            padding: '28px',
            textAlign: 'center',
            background: '#F8FAFC',
            borderRadius: 'var(--radius-lg)',
            border: '1px dashed #E2E8F0',
            color: 'var(--text-muted)',
            fontSize: '13px',
            fontWeight: '600'
          }}>
            Recently Deleted is empty
          </div>
        )}
      </div>

      {/* Add New Note Modal */}
      {showNoteModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(15, 23, 42, 0.6)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '24px'
        }}>
          <div className="animate-fade-in" style={{
            background: '#FFFFFF',
            borderRadius: 'var(--radius-xl)',
            padding: '28px',
            maxWidth: '500px',
            width: '100%',
            boxShadow: '0 20px 40px rgba(0,0,0,0.3)'
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-dark)', marginBottom: '16px' }}>
              Add Research Notebook Observation
            </h3>
            <form onSubmit={handleAddNote}>
              <div className="form-group">
                <label className="form-label">Note Title</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. BMP-2 100ng/ml Nodule Accretion"
                  value={newNoteTitle}
                  onChange={(e) => setNewNoteTitle(e.target.value)}
                  required
                />
              </div>
              <div className="form-group" style={{ marginBottom: '20px' }}>
                <label className="form-label">Observation Notes</label>
                <textarea
                  className="form-input"
                  style={{ height: '90px', padding: '10px' }}
                  placeholder="Enter scientific observations or tissue culture conditions..."
                  value={newNoteContent}
                  onChange={(e) => setNewNoteContent(e.target.value)}
                  required
                />
              </div>
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => setShowNoteModal(false)}
                  style={{ background: '#F1F5F9', border: 'none', padding: '8px 16px', borderRadius: 'var(--radius-md)', fontSize: '13px', fontWeight: '600', cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary-burgundy"
                  style={{ width: 'auto', padding: '0 20px', height: '40px', fontSize: '13px', marginBottom: 0 }}
                >
                  Save Note
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}

