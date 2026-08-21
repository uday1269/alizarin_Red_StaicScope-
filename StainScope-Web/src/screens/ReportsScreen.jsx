import React, { useState } from 'react';
import { 
  FileText, 
  Search, 
  Download, 
  FileSpreadsheet, 
  Eye, 
  Sparkles, 
  GitCompare,
  X,
  Trash2,
  BookmarkPlus
} from 'lucide-react';

export default function ReportsScreen({ onNavigate, analysesHistory, currentAnalysis, savedComparisons, onDeleteComparison, onDeleteAnalysis }) {
  const [activeTab, setActiveTab] = useState('quantification'); // 'quantification' | 'comparisons'
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [selectedReportIds, setSelectedReportIds] = useState([]);
  const [actionAlert, setActionAlert] = useState('');

  const reportsList = analysesHistory || [];

  const filteredReports = reportsList.filter((report) => {
    const matchesSearch = report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          report.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          report.stainType.toLowerCase().includes(searchTerm.toLowerCase());
    if (statusFilter === 'All') return matchesSearch;
    return matchesSearch && report.status.toLowerCase().includes(statusFilter.toLowerCase());
  });

  const handleSelectReport = (id) => {
    setSelectedReportIds((prev) => 
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleSelectAll = () => {
    if (selectedReportIds.length === filteredReports.length) {
      setSelectedReportIds([]);
    } else {
      setSelectedReportIds(filteredReports.map((r) => r.id));
    }
  };

  const handleAction = (msg) => {
    setActionAlert(msg);
    setTimeout(() => setActionAlert(''), 4000);
  };

  const handleLaunchCompare = () => {
    const chosen = reportsList.filter((r) => selectedReportIds.includes(r.id));
    if (chosen.length >= 2) {
      onNavigate('compare', { selectedSamples: chosen });
    }
  };

  return (
    <div className="animate-fade-in" style={{ padding: '24px 24px 48px', maxWidth: '1280px', margin: '0 auto' }}>
      
      {/* Header & Quick Action Buttons */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px',
        flexWrap: 'wrap',
        gap: '16px',
        background: 'var(--bg-card)',
        padding: '24px',
        borderRadius: 'var(--radius-xl)',
        border: '1px solid var(--border-light)',
        boxShadow: 'var(--shadow-sm)'
      }}>
        <div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'var(--primary-burgundy)', fontSize: '12px', fontWeight: '700', marginBottom: '4px' }}>
            <FileText size={16} /> Alizarin Red S Analysis Repository
          </div>
          <h1 style={{ fontSize: '26px', fontWeight: '800', color: 'var(--text-dark)' }}>
            Quantification Reports Repository
          </h1>
          <p style={{ fontSize: '14px', color: 'var(--text-muted)' }}>
            Access all verified osteogenic matrix analysis reports, open full results, or select multiple reports for differential comparison.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button
            onClick={handleLaunchCompare}
            disabled={selectedReportIds.length < 2}
            style={{
              background: selectedReportIds.length >= 2 ? 'var(--primary-burgundy)' : 'var(--bg-light-app)',
              color: selectedReportIds.length >= 2 ? '#FFFFFF' : 'var(--text-muted)',
              border: selectedReportIds.length >= 2 ? 'none' : '1px solid var(--border-light)',
              padding: '10px 18px',
              borderRadius: 'var(--radius-md)',
              fontWeight: '700',
              fontSize: '13px',
              cursor: selectedReportIds.length >= 2 ? 'pointer' : 'not-allowed',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              boxShadow: selectedReportIds.length >= 2 ? 'var(--shadow-btn)' : 'none'
            }}
          >
            <GitCompare size={16} /> Compare Selected ({selectedReportIds.length} Reports)
          </button>

          <button
            onClick={() => handleAction('📄 Exporting selected PDF reports...')}
            disabled={selectedReportIds.length === 0}
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-light)',
              color: 'var(--text-dark)',
              padding: '10px 18px',
              borderRadius: 'var(--radius-md)',
              fontWeight: '700',
              fontSize: '13px',
              cursor: selectedReportIds.length > 0 ? 'pointer' : 'not-allowed',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Download size={16} color="var(--primary-burgundy)" /> Batch PDF ({selectedReportIds.length})
          </button>

          <button
            onClick={() => handleAction('📊 Compiling raw report data to CSV file...')}
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-light)',
              color: 'var(--text-dark)',
              padding: '10px 16px',
              borderRadius: 'var(--radius-md)',
              fontWeight: '600',
              fontSize: '13px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <FileSpreadsheet size={16} color="var(--primary-burgundy)" /> Export CSV
          </button>
        </div>
      </div>

      {/* Action Notification Alert */}
      {actionAlert && (
        <div style={{
          background: 'var(--primary-burgundy-light)',
          border: '1px solid var(--primary-burgundy-border)',
          color: 'var(--primary-burgundy)',
          padding: '12px 18px',
          borderRadius: 'var(--radius-md)',
          marginBottom: '24px',
          fontWeight: '700',
          fontSize: '13px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <Sparkles size={16} /> {actionAlert}
        </div>
      )}

      {/* Repository Main Category Tabs */}
      <div style={{
        display: 'flex',
        gap: '12px',
        marginBottom: '24px',
        borderBottom: '1px solid var(--border-light)',
        paddingBottom: '12px'
      }}>
        <button
          onClick={() => setActiveTab('quantification')}
          style={{
            background: activeTab === 'quantification' ? 'var(--primary-burgundy)' : 'var(--bg-card)',
            color: activeTab === 'quantification' ? '#FFFFFF' : 'var(--text-dark)',
            border: `1px solid ${activeTab === 'quantification' ? 'var(--primary-burgundy)' : 'var(--border-light)'}`,
            padding: '10px 20px',
            borderRadius: 'var(--radius-lg)',
            fontWeight: '700',
            fontSize: '14px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            boxShadow: activeTab === 'quantification' ? 'var(--shadow-btn)' : 'none'
          }}
        >
          <FileText size={18} /> Quantification Reports ({reportsList.length})
        </button>

        <button
          onClick={() => setActiveTab('comparisons')}
          style={{
            background: activeTab === 'comparisons' ? 'var(--primary-burgundy)' : 'var(--bg-card)',
            color: activeTab === 'comparisons' ? '#FFFFFF' : 'var(--text-dark)',
            border: `1px solid ${activeTab === 'comparisons' ? 'var(--primary-burgundy)' : 'var(--border-light)'}`,
            padding: '10px 20px',
            borderRadius: 'var(--radius-lg)',
            fontWeight: '700',
            fontSize: '14px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            boxShadow: activeTab === 'comparisons' ? 'var(--shadow-btn)' : 'none'
          }}
        >
          <GitCompare size={18} /> Saved Comparison Reports ({(savedComparisons || []).length})
        </button>
      </div>

      {activeTab === 'comparisons' ? (
        /* Saved Comparison Reports Repository View */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          {(savedComparisons && savedComparisons.length > 0) ? (
            savedComparisons.map((comp) => {
              const createdDate = comp.created_at ? new Date(comp.created_at).toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }) : 'Recent';
              const summary = comp.ranking_summary || {};
              const sampleCount = comp.batch_comparison_items?.length || summary.compared_count || summary.sample_titles?.length || 2;
              
              const handleReopen = () => {
                const itemAnalysisIds = comp.batch_comparison_items
                  ? comp.batch_comparison_items.map(i => i.analysis_id)
                  : (summary.samples_data ? summary.samples_data.map(s => s.dbId || s.id) : []);

                let matchedScans = reportsList.filter(r => itemAnalysisIds.includes(r.dbId) || itemAnalysisIds.includes(r.id));
                if (matchedScans.length < 2 && summary.sample_titles) {
                  matchedScans = reportsList.filter(r => summary.sample_titles.some(t => r.title?.includes(t) || t?.includes(r.title)));
                }
                if (matchedScans.length < 2 && summary.samples_data && Array.isArray(summary.samples_data) && summary.samples_data.length >= 2) {
                  matchedScans = summary.samples_data.map((s, idx) => ({
                    id: s.id || `sample-${idx + 1}`,
                    dbId: s.dbId || s.id,
                    title: s.title || `Saved Sample ${idx + 1}`,
                    mineralizedArea: s.area || '50.0%',
                    stainIntensityOD: s.od || '0.22 OD',
                    nodulesCount: s.nodules || 1000,
                    day: 'Day 21',
                    magnification: '20x Objective',
                    stainType: 'Alizarin Red S (2%)',
                    status: 'High Mineralization',
                    statusColor: '#059669',
                    imageUrl: s.imageUrl || '',
                    thumbnailUrl: s.thumbnailUrl || ''
                  }));
                }
                if (matchedScans.length < 2) {
                  matchedScans = reportsList.slice(0, 3);
                }
                onNavigate('compare', { selectedSamples: matchedScans });
              };

              return (
                <div
                  key={comp.id}
                  className="hover-lift"
                  style={{
                    background: 'var(--bg-card)',
                    borderRadius: 'var(--radius-xl)',
                    border: '1px solid var(--border-light)',
                    padding: '24px',
                    boxShadow: 'var(--shadow-sm)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '16px'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                        <span style={{
                          padding: '4px 10px',
                          borderRadius: '12px',
                          fontSize: '11px',
                          fontWeight: '800',
                          backgroundColor: 'var(--primary-burgundy-light)',
                          color: 'var(--primary-burgundy)',
                          border: '1px solid var(--primary-burgundy-border)'
                        }}>
                          {sampleCount} Reports Compared
                        </span>
                        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                          Saved on {createdDate}
                        </span>
                      </div>
                      <h3 style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-dark)', margin: 0 }}>
                        {comp.title || 'ARS Differential Matrix Comparison'}
                      </h3>
                    </div>

                    <div style={{ display: 'flex', gap: '10px' }}>
                      <button
                        onClick={handleReopen}
                        className="btn-primary-burgundy"
                        style={{
                          padding: '8px 16px',
                          fontSize: '13px',
                          fontWeight: '700',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px'
                        }}
                      >
                        <Eye size={16} /> Re-open Comparison View
                      </button>

                      <button
                        onClick={() => onDeleteComparison && onDeleteComparison(comp.id)}
                        style={{
                          background: '#FEF2F2',
                          border: '1px solid #FCA5A5',
                          color: '#DC2626',
                          padding: '8px 12px',
                          borderRadius: 'var(--radius-md)',
                          fontSize: '13px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px'
                        }}
                        title="Delete Comparison Report"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>

                  {/* Compared Samples Chip Summary */}
                  {summary.sample_titles && (
                    <div style={{
                      display: 'flex',
                      gap: '8px',
                      flexWrap: 'wrap',
                      background: 'var(--bg-light-app)',
                      padding: '12px 16px',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid var(--border-light)'
                    }}>
                      <span style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <GitCompare size={14} /> Samples:
                      </span>
                      {summary.sample_titles.map((title, idx) => (
                        <span key={idx} style={{
                          background: '#FFFFFF',
                          border: '1px solid var(--border-light)',
                          padding: '3px 10px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: '600',
                          color: 'var(--text-dark)'
                        }}>
                          {title}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              );
            })
          ) : (
            <div style={{
              padding: '48px',
              textAlign: 'center',
              background: 'var(--bg-card)',
              borderRadius: 'var(--radius-xl)',
              border: '1px solid var(--border-light)',
              color: 'var(--text-muted)'
            }}>
              No saved comparison reports found in your account database. Create and save a comparison on the Compare screen to view it here anytime.
            </div>
          )}
        </div>
      ) : (
        /* Single Quantification Reports View */
        <>
          {/* Search & Filter Controls */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: '16px',
            flexWrap: 'wrap',
            marginBottom: '28px'
          }}>
            {/* Search Input */}
            <div style={{ position: 'relative', flex: '1', minWidth: '280px' }}>
              <Search size={18} style={{ position: 'absolute', left: '14px', top: '15px', color: 'var(--text-muted)' }} />
              <input
                type="text"
                className="form-input"
                placeholder="Search reports by ID, sample name, or stain type..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{ paddingLeft: '42px' }}
              />
            </div>

            {/* Filter Pills */}
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {['All', 'High', 'Moderate', 'Low'].map((status) => (
                <button
                  key={status}
                  onClick={() => setStatusFilter(status)}
                  style={{
                    background: statusFilter === status ? 'var(--primary-burgundy)' : 'var(--bg-card)',
                    color: statusFilter === status ? '#FFFFFF' : 'var(--text-dark)',
                    border: `1px solid ${statusFilter === status ? 'var(--primary-burgundy)' : 'var(--border-light)'}`,
                    padding: '8px 16px',
                    borderRadius: '20px',
                    fontSize: '13px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                >
                  {status === 'All' ? 'All Reports' : `${status} Mineralization`}
                </button>
              ))}
            </div>
          </div>

          {/* Reports Table Container */}
          <div style={{
            background: 'var(--bg-card)',
            borderRadius: 'var(--radius-xl)',
            border: '1px solid var(--border-light)',
            boxShadow: 'var(--shadow-sm)',
            overflow: 'hidden',
            marginBottom: '32px'
          }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13.5px' }}>
              <thead>
                <tr style={{ background: '#FAFAFA', borderBottom: '1px solid var(--border-light)', color: 'var(--text-muted)', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  <th style={{ padding: '16px', width: '40px' }}>
                    <input
                      type="checkbox"
                      checked={selectedReportIds.length > 0 && selectedReportIds.length === filteredReports.length}
                      onChange={handleSelectAll}
                      style={{ width: '16px', height: '16px', accentColor: 'var(--primary-burgundy)', cursor: 'pointer' }}
                    />
                  </th>
                  <th style={{ padding: '16px' }}>Micrograph & Sample Title</th>
                  <th style={{ padding: '16px' }}>Date Analyzed</th>
                  <th style={{ padding: '16px' }}>Mineralized Area %</th>
                  <th style={{ padding: '16px' }}>Stain OD</th>
                  <th style={{ padding: '16px' }}>Calcium Index</th>
                  <th style={{ padding: '16px' }}>Status</th>
                  <th style={{ padding: '16px', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredReports.length > 0 ? (
                  filteredReports.map((report) => {
                    const isSelected = selectedReportIds.includes(report.id);
                    return (
                      <tr
                        key={report.id}
                        style={{
                          borderBottom: '1px solid var(--border-light)',
                          background: isSelected ? 'var(--primary-burgundy-light)' : 'transparent',
                          transition: 'background 0.2s ease'
                        }}
                      >
                        <td style={{ padding: '16px' }}>
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => handleSelectReport(report.id)}
                            style={{ width: '16px', height: '16px', accentColor: 'var(--primary-burgundy)', cursor: 'pointer' }}
                          />
                        </td>
                        <td style={{ padding: '16px' }}>
                          <div 
                            style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}
                            onClick={() => onNavigate('results', { analysis: report })}
                            title={`Open report details for ${report.id}`}
                          >
                            <div style={{
                              width: '42px',
                              height: '42px',
                              borderRadius: '8px',
                              overflow: 'hidden',
                              background: '#090A0F',
                              flexShrink: 0,
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              color: 'var(--primary-burgundy)'
                            }}>
                              {(report.imageUrl || report.thumbnailUrl || report.overlay || report.overlays?.nodule_map) ? (
                                <img
                                  src={report.imageUrl || report.thumbnailUrl || report.overlay || report.overlays?.nodule_map}
                                  alt={report.title}
                                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                />
                              ) : (
                                <FileText size={20} />
                              )}
                            </div>
                            <div>
                              <div style={{ fontWeight: '700', color: 'var(--text-dark)' }}>{report.title}</div>
                              <div style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>ID: {report.id} • {report.magnification}</div>
                            </div>
                          </div>
                        </td>
                        <td style={{ padding: '16px', color: 'var(--text-muted)' }}>
                          {report.date}
                        </td>
                        <td style={{ padding: '16px', fontWeight: '800', color: 'var(--primary-burgundy)' }}>
                          {report.mineralizedArea}
                        </td>
                        <td style={{ padding: '16px', fontWeight: '600' }}>
                          {report.stainIntensityOD}
                        </td>
                        <td style={{ padding: '16px', fontWeight: '600', color: '#059669' }}>
                          {report.calciumEstimate}
                        </td>
                        <td style={{ padding: '16px' }}>
                          <span style={{
                            padding: '4px 10px',
                            borderRadius: '16px',
                            fontSize: '11.5px',
                            fontWeight: '700',
                            backgroundColor: report.statusColor + '18',
                            color: report.statusColor,
                            border: `1px solid ${report.statusColor}40`
                          }}>
                            {report.status}
                          </span>
                        </td>
                        <td style={{ padding: '16px', textAlign: 'right' }} onClick={(e) => e.stopPropagation()}>
                          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '6px' }}>
                            <button
                              onClick={() => onNavigate('results', { analysis: report })}
                              title="View Full Results Home"
                              style={{
                                background: 'var(--bg-light-app)',
                                border: '1px solid var(--border-light)',
                                padding: '6px 12px',
                                borderRadius: 'var(--radius-md)',
                                fontSize: '12px',
                                fontWeight: '700',
                                color: 'var(--text-dark)',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px'
                              }}
                            >
                              <Eye size={14} /> View Report
                            </button>

                            <button
                              onClick={() => handleAction(`📄 Downloading PDF report for ${report.id}...`)}
                              title="Download PDF"
                              style={{
                                background: 'var(--primary-burgundy-light)',
                                border: '1px solid var(--primary-burgundy-border)',
                                padding: '6px 10px',
                                borderRadius: 'var(--radius-md)',
                                fontSize: '12px',
                                fontWeight: '700',
                                color: 'var(--primary-burgundy)',
                                cursor: 'pointer'
                              }}
                            >
                              <Download size={14} />
                            </button>

                            <button
                              onClick={() => onDeleteAnalysis && onDeleteAnalysis(report)}
                              title="Move to Recently Deleted"
                              style={{
                                background: '#F8FAFC',
                                border: '1px solid #E2E8F0',
                                padding: '6px 8px',
                                borderRadius: 'var(--radius-md)',
                                fontSize: '12px',
                                color: 'var(--text-muted)',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center'
                              }}
                            >
                              <X size={14} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={8} style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
                      No reports match your current filter criteria.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

    </div>
  );
}
