import React from 'react';
import { 
  Microscope, 
  UploadCloud, 
  GitCompare, 
  TrendingUp, 
  Activity, 
  CheckCircle, 
  ChevronRight,
  Sparkles,
  FileText,
  Cpu
} from 'lucide-react';
export default function DashboardScreen({ onNavigate, analysesHistory, userProfile }) {
  const recentAnalyses = analysesHistory || [];
  const totalScans = recentAnalyses.length;

  const avgMineralization = totalScans > 0
    ? (recentAnalyses.reduce((acc, curr) => acc + (curr.mineralizedAreaValue || 0), 0) / totalScans).toFixed(1) + '%'
    : '0.0%';

  const highCalcificationCount = recentAnalyses.filter((item) => (item.mineralizedAreaValue || 0) > 50).length;
  const userName = userProfile?.full_name || 'Researcher';
  const userLab = userProfile?.lab_name || 'Regenerative Medicine & Osteogenesis Lab';

  return (
    <div className="animate-fade-in" style={{ padding: '24px 24px 48px', maxWidth: '1280px', margin: '0 auto' }}>
      
      {/* Welcome Banner */}
      <div style={{
        background: 'linear-gradient(135deg, #801D1E 0%, #4A0E0F 100%)',
        borderRadius: 'var(--radius-xl)',
        padding: '28px 32px',
        color: '#FFFFFF',
        marginBottom: '28px',
        boxShadow: '0 10px 30px rgba(128, 29, 30, 0.25)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '20px'
      }}>
        <div>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: 'rgba(255, 255, 255, 0.15)',
            padding: '4px 12px',
            borderRadius: '20px',
            fontSize: '12px',
            fontWeight: '600',
            marginBottom: '10px'
          }}>
            <Sparkles size={14} color="#FCA5A5" /> Alizarin Red S Quantification Platform
          </div>
          <h1 style={{ fontSize: '26px', fontWeight: '800', marginBottom: '4px' }}>
            Welcome, {userName}
          </h1>
          <p style={{ opacity: 0.85, fontSize: '14px', maxWidth: '520px' }}>
            {userLab} • {totalScans} total stain micrograph{totalScans === 1 ? '' : 's'} quantified to date.
          </p>
        </div>

        {/* Quick Actions Shortcuts */}
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button
            onClick={() => onNavigate('upload')}
            className="hover-lift"
            style={{
              background: '#FFFFFF',
              color: '#801D1E',
              border: 'none',
              padding: '12px 20px',
              borderRadius: 'var(--radius-md)',
              fontWeight: '700',
              fontSize: '14px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
            }}
          >
            <UploadCloud size={18} /> New Analysis
          </button>
          
          <button
            onClick={() => onNavigate('compare')}
            className="hover-lift"
            style={{
              background: 'rgba(255, 255, 255, 0.15)',
              color: '#FFFFFF',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              padding: '12px 18px',
              borderRadius: 'var(--radius-md)',
              fontWeight: '600',
              fontSize: '14px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <GitCompare size={18} /> Compare Samples
          </button>

          <button
            onClick={() => onNavigate('reports')}
            className="hover-lift"
            style={{
              background: 'rgba(255, 255, 255, 0.15)',
              color: '#FFFFFF',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              padding: '12px 18px',
              borderRadius: 'var(--radius-md)',
              fontWeight: '600',
              fontSize: '14px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <FileText size={18} /> View Reports
          </button>
        </div>
      </div>

      {/* AI Model Status & Node Health Card */}
      <div style={{
        background: '#FFFFFF',
        borderRadius: 'var(--radius-xl)',
        border: '1px solid var(--border-light)',
        padding: '20px 24px',
        boxShadow: 'var(--shadow-sm)',
        marginBottom: '28px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '14px',
            background: 'var(--primary-burgundy-light)',
            color: 'var(--primary-burgundy)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Cpu size={24} />
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
              <h3 style={{ fontSize: '15px', fontWeight: '800', color: 'var(--text-dark)' }}>
                Classical CV Analysis Engine v1.0
              </h3>
              <span style={{ fontSize: '11px', background: '#ECFDF5', color: '#059669', padding: '2px 8px', borderRadius: '12px', fontWeight: '700' }}>
                ONLINE (http://localhost:8000)
              </span>
            </div>
            <p style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>
              Calibrated for Alizarin Red S spectral absorbance peak (560nm) &amp; multi-marker watershed nodule detection
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '20px', fontSize: '12.5px', color: 'var(--text-muted)' }}>
          <div><span style={{ display: 'block', fontSize: '11px' }}>CV BACKEND</span> <strong style={{ color: '#059669' }}>Connected</strong></div>
          <div><span style={{ display: 'block', fontSize: '11px' }}>CONFIDENCE SCORE</span> <strong style={{ color: '#059669' }}>Real-time</strong></div>
          <div><span style={{ display: 'block', fontSize: '11px' }}>SYSTEM STATUS</span> <strong style={{ color: 'var(--text-dark)' }}>Active</strong></div>
        </div>
      </div>

      {/* Research Metrics Grid Row */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '20px',
        marginBottom: '32px'
      }}>
        <div className="hover-lift" style={{
          background: '#FFFFFF',
          borderRadius: 'var(--radius-lg)',
          padding: '20px',
          border: '1px solid var(--border-light)',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '13px', fontWeight: '600', marginBottom: '8px' }}>
            <span>TOTAL ANALYSES</span>
            <Microscope size={18} color="#801D1E" />
          </div>
          <div style={{ fontSize: '28px', fontWeight: '800', color: 'var(--text-dark)' }}>{totalScans}</div>
          <div style={{ fontSize: '12px', color: totalScans > 0 ? '#059669' : 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '4px' }}>
            {totalScans > 0 ? <TrendingUp size={14} /> : null} {totalScans > 0 ? `${totalScans} completed scan${totalScans === 1 ? '' : 's'}` : 'No scans yet'}
          </div>
        </div>

        <div className="hover-lift" style={{
          background: '#FFFFFF',
          borderRadius: 'var(--radius-lg)',
          padding: '20px',
          border: '1px solid var(--border-light)',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '13px', fontWeight: '600', marginBottom: '8px' }}>
            <span>AVG MINERALIZATION</span>
            <Activity size={18} color="#DC2626" />
          </div>
          <div style={{ fontSize: '28px', fontWeight: '800', color: 'var(--primary-burgundy)' }}>{avgMineralization}</div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
            Extracellular matrix area
          </div>
        </div>

        <div className="hover-lift" style={{
          background: '#FFFFFF',
          borderRadius: 'var(--radius-lg)',
          padding: '20px',
          border: '1px solid var(--border-light)',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '13px', fontWeight: '600', marginBottom: '8px' }}>
            <span>HIGH CALCIFICATION</span>
            <CheckCircle size={18} color="#059669" />
          </div>
          <div style={{ fontSize: '28px', fontWeight: '800', color: '#059669' }}>{highCalcificationCount} Scans</div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
            &gt;50% area coverage
          </div>
        </div>

        <div className="hover-lift" style={{
          background: '#FFFFFF',
          borderRadius: 'var(--radius-lg)',
          padding: '20px',
          border: '1px solid var(--border-light)',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '13px', fontWeight: '600', marginBottom: '8px' }}>
            <span>CV ENGINE PRECISION</span>
            <Sparkles size={18} color="#D97706" />
          </div>
          <div style={{ fontSize: '28px', fontWeight: '800', color: 'var(--text-dark)' }}>Live</div>
          <div style={{ fontSize: '12px', color: '#059669', marginTop: '4px' }}>
            Multi-marker watershed
          </div>
        </div>
      </div>

      {/* Recent Analyses & Reports Section */}
      <div style={{
        background: '#FFFFFF',
        borderRadius: 'var(--radius-xl)',
        border: '1px solid var(--border-light)',
        boxShadow: 'var(--shadow-sm)',
        padding: '24px',
        marginBottom: '32px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '10px' }}>
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-dark)' }}>Recent Stain Quantification Scans</h2>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Latest Alizarin Red S microscopic sample runs &amp; reports</p>
          </div>

          {recentAnalyses.length > 0 && (
            <button
              onClick={() => onNavigate('reports')}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--primary-burgundy)',
                fontSize: '14px',
                fontWeight: '700',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              View All Reports <ChevronRight size={16} />
            </button>
          )}
        </div>

        {recentAnalyses.length === 0 ? (
          /* Clean Empty State */
          <div style={{ padding: '48px 24px', textAlign: 'center' }}>
            <div style={{
              width: '60px',
              height: '60px',
              borderRadius: '18px',
              background: 'var(--primary-burgundy-light)',
              color: 'var(--primary-burgundy)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px'
            }}>
              <UploadCloud size={30} />
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-dark)', marginBottom: '6px' }}>
              No analyses yet
            </h3>
            <p style={{ fontSize: '13.5px', color: 'var(--text-muted)', maxWidth: '440px', margin: '0 auto 20px', lineHeight: '1.5' }}>
              Upload an Alizarin Red S stained microscopy image to begin automated CV stain quantification.
            </p>
            <button
              onClick={() => onNavigate('upload')}
              style={{
                background: 'var(--primary-burgundy)',
                color: '#FFFFFF',
                border: 'none',
                padding: '10px 22px',
                borderRadius: 'var(--radius-md)',
                fontWeight: '700',
                fontSize: '13.5px',
                cursor: 'pointer',
                boxShadow: 'var(--shadow-btn)'
              }}
            >
              Upload &amp; Analyze Image
            </button>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-light)', color: 'var(--text-muted)', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  <th style={{ padding: '12px 16px' }}>Sample Info</th>
                  <th style={{ padding: '12px 16px' }}>Date</th>
                  <th style={{ padding: '12px 16px' }}>Mineralized Area %</th>
                  <th style={{ padding: '12px 16px' }}>Stain Intensity (OD)</th>
                  <th style={{ padding: '12px 16px' }}>Nodule Count</th>
                  <th style={{ padding: '12px 16px' }}>Status</th>
                  <th style={{ padding: '12px 16px', textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {recentAnalyses.map((item) => (
                  <tr key={item.id} style={{ borderBottom: '1px solid #F1F5F9', transition: 'background 0.2s ease' }}>
                    <td style={{ padding: '16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{
                          width: '40px',
                          height: '40px',
                          borderRadius: '8px',
                          background: '#FFF1F1',
                          border: '1px solid #FCA5A5',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: '#801D1E',
                          fontWeight: '700',
                          fontSize: '12px'
                        }}>
                          {(item.magnification || '20x').split(' ')[0]}
                        </div>
                        <div>
                          <div style={{ fontWeight: '700', color: 'var(--text-dark)', fontSize: '14px' }}>{item.title}</div>
                          <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{item.id} • {item.stainType}</div>
                        </div>
                      </div>
                    </td>
                    <td style={{ padding: '16px', color: 'var(--text-muted)', fontSize: '13px' }}>
                      {item.date}
                    </td>
                    <td style={{ padding: '16px', fontWeight: '700', color: 'var(--primary-burgundy)' }}>
                      {item.mineralizedArea}
                    </td>
                    <td style={{ padding: '16px', fontWeight: '600' }}>
                      {item.stainIntensityOD}
                    </td>
                    <td style={{ padding: '16px', fontWeight: '600' }}>
                      {(item.nodulesCount !== undefined ? item.nodulesCount : 0).toLocaleString()}
                    </td>
                    <td style={{ padding: '16px' }}>
                      <span style={{
                        display: 'inline-block',
                        padding: '4px 10px',
                        borderRadius: '20px',
                        fontSize: '12px',
                        fontWeight: '700',
                        backgroundColor: (item.statusColor || '#059669') + '18',
                        color: item.statusColor || '#059669',
                        border: `1px solid ${item.statusColor || '#059669'}40`
                      }}>
                        {item.status}
                      </span>
                    </td>
                    <td style={{ padding: '16px', textAlign: 'right' }}>
                      <button
                        onClick={() => onNavigate('results', { analysis: item })}
                        style={{
                          background: 'var(--primary-burgundy-light)',
                          color: 'var(--primary-burgundy)',
                          border: 'none',
                          padding: '6px 14px',
                          borderRadius: 'var(--radius-md)',
                          fontSize: '13px',
                          fontWeight: '700',
                          cursor: 'pointer'
                        }}
                      >
                        View Report
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
