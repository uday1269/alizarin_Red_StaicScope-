import React, { useState, useEffect } from 'react';
import { 
  Download, 
  GitCompare, 
  Layers, 
  BarChart2, 
  ArrowLeft,
  AlertTriangle,
  Info,
  CheckCircle2,
  List,
  Sliders
} from 'lucide-react';
import { MOCK_COLOR_HISTOGRAM } from '../data/mockData';
import { fetchAnalysisById, resolveWebFileUrl } from '../api';

export default function ResultsScreen({ onNavigate, result: propResult }) {
  const [result, setResult] = useState(() => {
    if (propResult) return propResult;
    if (typeof window !== 'undefined') {
      try {
        const saved = sessionStorage.getItem('stainscope_current_analysis');
        if (saved) return JSON.parse(saved);
      } catch (e) {}
    }
    return null;
  });
  const [viewMode, setViewMode] = useState('segmentation'); // 'original' | 'segmentation' | 'heatmap'

  useEffect(() => {
    if (propResult) {
      setResult(propResult);
      const targetId = propResult.dbId || propResult.id;
      if (targetId) {
        fetchAnalysisById(targetId).then((fullData) => {
          if (fullData) {
            setResult((prev) => ({ ...prev, ...fullData }));
          }
        }).catch((err) => console.warn('Could not fetch full analysis detail:', err));
      }
    }
  }, [propResult]);

  useEffect(() => {
    if (!result && typeof window !== 'undefined') {
      try {
        const saved = sessionStorage.getItem('stainscope_current_analysis');
        if (saved) {
          const parsed = JSON.parse(saved);
          setResult(parsed);
          const targetId = parsed.dbId || parsed.id;
          if (targetId) {
            fetchAnalysisById(targetId).then((fullData) => {
              if (fullData) {
                setResult((prev) => ({ ...prev, ...fullData }));
              }
            }).catch((err) => console.warn('Could not fetch full analysis detail:', err));
          }
        }
      } catch (e) {}
    }
  }, [result]);

  if (!result) {
    return (
      <div className="animate-fade-in" style={{ padding: '64px 24px', maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
        <div style={{
          width: '64px',
          height: '64px',
          borderRadius: '20px',
          background: 'var(--primary-burgundy-light)',
          color: 'var(--primary-burgundy)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 16px'
        }}>
          <Layers size={32} />
        </div>
        <h2 style={{ fontSize: '22px', fontWeight: '800', color: 'var(--text-dark)', marginBottom: '8px' }}>
          No Active Analysis Selected
        </h2>
        <p style={{ fontSize: '14px', color: 'var(--text-muted)', maxWidth: '440px', margin: '0 auto 24px', lineHeight: '1.5' }}>
          Upload an Alizarin Red S microscopy image in the workstation to generate live CV quantification reports.
        </p>
        <button
          onClick={() => onNavigate('upload')}
          style={{
            background: 'var(--primary-burgundy)',
            color: '#FFFFFF',
            border: 'none',
            padding: '12px 24px',
            borderRadius: 'var(--radius-md)',
            fontWeight: '700',
            fontSize: '14px',
            cursor: 'pointer',
            boxShadow: 'var(--shadow-btn)'
          }}
        >
          Go to Upload Workstation
        </button>
      </div>
    );
  }

  // Extract backend visual overlays if available
  const rawImageUrl = resolveWebFileUrl(result.imageUrl || result.thumbnailUrl || result.rawDbRecord?.image_url);
  const noduleMapOverlay = resolveWebFileUrl(result.overlays?.nodule_map || result.overlay || result.rawDbRecord?.overlays?.nodule_map);
  const heatmapOverlay = resolveWebFileUrl(result.overlays?.overlay || result.overlays?.heatmap || result.overlay || result.rawDbRecord?.overlays?.overlay);
  const validationPanel = resolveWebFileUrl(result.overlays?.validation_panel || result.rawDbRecord?.overlays?.validation_panel);

  // Extract nodule objects list from backend
  const noduleObjects = Array.isArray(result.nodules?.objects) 
    ? result.nodules.objects 
    : (Array.isArray(result.rawApiData?.nodules?.objects) ? result.rawApiData.nodules.objects : []);

  // Size distribution mapping
  const sizeDist = (result.sizeDistribution && typeof result.sizeDistribution === 'object') 
    ? result.sizeDistribution 
    : ((result.nodules?.size_distribution && typeof result.nodules.size_distribution === 'object') ? result.nodules.size_distribution : {});

  // Warnings list safe mapping
  const rawWarnings = result.warnings || result.rawDbRecord?.quality_warnings;
  const warningsList = Array.isArray(rawWarnings)
    ? rawWarnings
    : typeof rawWarnings === 'string'
    ? (() => {
        try {
          const parsed = JSON.parse(rawWarnings);
          return Array.isArray(parsed) ? parsed : [rawWarnings];
        } catch (e) {
          return rawWarnings.trim() ? [rawWarnings] : [];
        }
      })()
    : [];

  return (
    <div className="animate-fade-in" style={{ padding: '24px 24px 48px', maxWidth: '1200px', margin: '0 auto' }}>
      
      {/* Top Header & Export Actions */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <button
            onClick={() => onNavigate('reports')}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              fontSize: '13px',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              marginBottom: '4px'
            }}
          >
            <ArrowLeft size={16} /> Back to Reports
          </button>
          <h1 style={{ fontSize: '24px', fontWeight: '800', color: 'var(--text-dark)' }}>
            {result.title}
          </h1>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
            Sample ID: <strong>{result.id}</strong> • Analyzed on {result.date} at {result.time} • Magnification: {result.magnification}
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button
            onClick={() => onNavigate('compare', { sampleA: result })}
            className="hover-lift"
            style={{
              background: '#FFFFFF',
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
            <GitCompare size={16} /> Compare Sample
          </button>

          <button
            onClick={() => onNavigate('reports', { analysis: result })}
            className="hover-lift"
            style={{
              background: 'var(--primary-burgundy)',
              color: '#FFFFFF',
              border: 'none',
              padding: '10px 18px',
              borderRadius: 'var(--radius-md)',
              fontWeight: '700',
              fontSize: '13px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              boxShadow: 'var(--shadow-btn)'
            }}
          >
            <Download size={16} /> Export PDF Report
          </button>
        </div>
      </div>

      {/* Warnings & Guidance Panel */}
      {warningsList.length > 0 && (
        <div style={{
          background: '#FFFBEB',
          border: '1px solid #FCD34D',
          borderRadius: 'var(--radius-lg)',
          padding: '14px 18px',
          marginBottom: '24px',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '12px'
        }}>
          <AlertTriangle size={20} color="#D97706" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong style={{ fontSize: '13px', color: '#92400E' }}>Backend Quality Warnings:</strong>
            <ul style={{ margin: '4px 0 0', paddingLeft: '18px', fontSize: '12.5px', color: '#78350F' }}>
              {warningsList.map((w, idx) => (
                <li key={idx}>{w}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Quantitative Metric Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '28px'
      }}>
        {/* High Density / Confluent Warning Banner (Item 9 Requirement) */}
        {(result.pattern === 'confluent' || result.pattern === 'dense' || result.mineralizedAreaValue > 20) && (
          <div style={{
            gridColumn: '1 / -1',
            background: '#FFFBEB',
            border: '1px solid #FCD34D',
            borderLeft: '5px solid #D97706',
            borderRadius: 'var(--radius-lg)',
            padding: '14px 18px',
            marginBottom: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            boxShadow: 'var(--shadow-sm)'
          }}>
            <AlertTriangle size={22} color="#D97706" style={{ flexShrink: 0 }} />
            <div>
              <strong style={{ fontSize: '13.5px', color: '#92400E', display: 'block', marginBottom: '2px' }}>
                Confluent Mineralization Notice:
              </strong>
              <span style={{ fontSize: '12.5px', color: '#B45309' }}>
                High density confluent nodules detected. Some touching nodules may merge in classical analysis, affecting count reliability.
              </span>
            </div>
          </div>
        )}

        {/* Metric 1: Mineralized Surface Area */}
        <div style={{
          background: '#FFFFFF',
          borderRadius: 'var(--radius-lg)',
          padding: '18px 20px',
          border: '1px solid var(--border-light)',
          borderLeft: '4px solid #10B981',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <span style={{ fontSize: '11.5px', fontWeight: '700', color: 'var(--text-muted)' }}>MINERALIZED SURFACE AREA</span>
          <div style={{ fontSize: '28px', fontWeight: '800', color: 'var(--text-dark)', margin: '4px 0' }}>
            {result.mineralizedArea}
          </div>
          <span style={{ fontSize: '12px', color: '#059669', fontWeight: '600' }}>
            {result.mineralization?.area_pixels ? `${result.mineralization.area_pixels.toLocaleString()} px` : 'High calcification density'}
          </span>
        </div>

        {/* Metric 2: Stain Intensity (OD PROXY) */}
        <div style={{
          background: '#FFFFFF',
          borderRadius: 'var(--radius-lg)',
          padding: '18px 20px',
          border: '1px solid var(--border-light)',
          borderLeft: '4px solid #DC2626',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <span style={{ fontSize: '11.5px', fontWeight: '700', color: 'var(--text-muted)' }}>STAIN INTENSITY (OD PROXY)</span>
          <div style={{ fontSize: '28px', fontWeight: '800', color: 'var(--text-dark)', margin: '4px 0' }}>
            {result.stainIntensityOD}
          </div>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Image-derived RGB log-contrast</span>
        </div>

        {/* Metric 3: Calcified Nodules Count (DIRECT FROM API) */}
        <div style={{
          background: '#FFFFFF',
          borderRadius: 'var(--radius-lg)',
          padding: '18px 20px',
          border: '1px solid var(--border-light)',
          borderLeft: '4px solid #D97706',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <span style={{ fontSize: '11.5px', fontWeight: '700', color: 'var(--text-muted)' }}>CALCIFIED NODULES</span>
          <div style={{ fontSize: '28px', fontWeight: '800', color: 'var(--text-dark)', margin: '4px 0' }}>
            {(result.nodulesCount !== undefined ? result.nodulesCount : 0).toLocaleString()}
          </div>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Direct API nodule count</span>
        </div>

        {/* Metric 4: Mineralization Index (Uncalibrated Proxy) */}
        <div style={{
          background: '#FFFFFF',
          borderRadius: 'var(--radius-lg)',
          padding: '18px 20px',
          border: '1px solid var(--border-light)',
          borderLeft: '4px solid #059669',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <span style={{ fontSize: '11.5px', fontWeight: '700', color: 'var(--text-muted)' }}>MINERALIZATION INDEX</span>
          <div style={{ fontSize: '28px', fontWeight: '800', color: '#059669', margin: '4px 0' }}>
            {result.calciumEstimate}
          </div>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Uncalibrated Area Proxy</span>
        </div>

        {/* Metric 5: AI Confidence & Runtime */}
        <div style={{
          background: '#FFFFFF',
          borderRadius: 'var(--radius-lg)',
          padding: '18px 20px',
          border: '1px solid var(--border-light)',
          borderLeft: '4px solid #7E22CE',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <span style={{ fontSize: '11.5px', fontWeight: '700', color: 'var(--text-muted)' }}>ENGINE CONFIDENCE</span>
          <div style={{ fontSize: '28px', fontWeight: '800', color: '#7E22CE', margin: '4px 0' }}>
            {result.aiConfidence}
          </div>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Processed in {result.processingTime}</span>
        </div>
      </div>

      {/* Main Analysis Visual Display & Breakdown */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '24px', marginBottom: '28px' }}>
        
        {/* Micrograph View Box */}
        <div style={{
          background: '#FFFFFF',
          borderRadius: 'var(--radius-xl)',
          border: '1px solid var(--border-light)',
          padding: '20px',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-dark)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Layers size={18} color="var(--primary-burgundy)" /> Micrograph &amp; Visual Overlay
            </h3>

            <div style={{ display: 'flex', gap: '4px', background: '#F1F5F9', padding: '3px', borderRadius: '8px' }}>
              {['original', 'segmentation', 'heatmap'].map((mode) => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode)}
                  style={{
                    background: viewMode === mode ? 'var(--primary-burgundy)' : 'transparent',
                    border: 'none',
                    padding: '4px 10px',
                    borderRadius: '6px',
                    fontSize: '11.5px',
                    fontWeight: '700',
                    color: viewMode === mode ? '#FFFFFF' : 'var(--text-muted)',
                    cursor: 'pointer',
                    textTransform: 'capitalize'
                  }}
                >
                  {mode}
                </button>
              ))}
            </div>
          </div>

          <div style={{
            position: 'relative',
            width: '100%',
            height: '340px',
            borderRadius: 'var(--radius-lg)',
            overflow: 'hidden',
            background: '#0F172A',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <div style={{
              width: '100%',
              height: '100%',
              position: 'relative',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: '#090A0F'
            }}>
              {/* Display Backend Generated Base64 Overlay or Original Image */}
              {viewMode === 'original' && (rawImageUrl || noduleMapOverlay) ? (
                <img
                  src={rawImageUrl || noduleMapOverlay}
                  alt={result.title || "Raw Micrograph"}
                  style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                />
              ) : viewMode === 'segmentation' && (noduleMapOverlay || rawImageUrl) ? (
                <img
                  src={noduleMapOverlay || rawImageUrl}
                  alt="Backend Nodule Map Overlay"
                  style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                />
              ) : viewMode === 'heatmap' && (heatmapOverlay || rawImageUrl) ? (
                <img
                  src={heatmapOverlay || rawImageUrl}
                  alt="Backend Heatmap Overlay"
                  style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                />
              ) : (
                <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No image preview available</div>
              )}

              {/* Fallback Overlay graphics if base64 overlays not generated */}
              {(!noduleMapOverlay && viewMode === 'segmentation') && (
                <svg width="100%" height="100%" viewBox="0 0 400 320" style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
                  <circle cx="160" cy="140" r="65" fill="rgba(16, 185, 129, 0.25)" stroke="#10B981" strokeWidth="2.5" strokeDasharray="4,2" />
                  <text x="165" y="145" fill="#10B981" fontSize="12" fontFamily="monospace" fontWeight="bold">#N01</text>
                  <circle cx="240" cy="180" r="50" fill="rgba(6, 182, 212, 0.25)" stroke="#06B6D4" strokeWidth="2.5" />
                </svg>
              )}

              <div style={{
                position: 'absolute',
                bottom: '12px',
                left: '12px',
                background: 'rgba(0, 0, 0, 0.75)',
                color: '#FFFFFF',
                padding: '4px 10px',
                borderRadius: '6px',
                fontSize: '11px',
                fontWeight: '600',
                backdropFilter: 'blur(4px)'
              }}>
                Mode: {viewMode === 'original' ? 'Raw Brightfield' : viewMode === 'segmentation' ? 'Backend Nodule Overlay' : 'Absorbance Heatmap'}
              </div>
            </div>
          </div>
        </div>

        {/* Nodule Size Statistics & Spatial Pattern */}
        <div style={{
          background: '#FFFFFF',
          borderRadius: 'var(--radius-xl)',
          border: '1px solid var(--border-light)',
          padding: '20px',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-dark)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BarChart2 size={18} color="var(--primary-burgundy)" /> Nodule Size &amp; Spatial Metrics
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '20px' }}>
            <div style={{ background: '#F8FAFC', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
              <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)', display: 'block' }}>MIN NODULE SIZE</span>
              <span style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-dark)' }}>{result.minNoduleSize || '0 px'}</span>
            </div>
            <div style={{ background: '#F8FAFC', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
              <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)', display: 'block' }}>MAX NODULE SIZE</span>
              <span style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-dark)' }}>{result.maxNoduleSize || '0 px'}</span>
            </div>
            <div style={{ background: '#F8FAFC', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
              <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)', display: 'block' }}>MEAN NODULE SIZE</span>
              <span style={{ fontSize: '18px', fontWeight: '800', color: 'var(--primary-burgundy)' }}>{result.avgNoduleSize || '0 px'}</span>
            </div>
            <div style={{ background: '#F8FAFC', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
              <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)', display: 'block' }}>MEDIAN NODULE SIZE</span>
              <span style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-dark)' }}>{result.medianNoduleSize || '0 px'}</span>
            </div>
          </div>

          {/* Size Distribution Bars */}
          {sizeDist && Object.keys(sizeDist).length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              <strong style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'block', marginBottom: '8px' }}>
                NODULE SIZE DISTRIBUTION:
              </strong>
              <div style={{ display: 'flex', gap: '8px' }}>
                {Object.entries(sizeDist).map(([cat, val]) => (
                  <div key={cat} style={{ flex: 1, textAlign: 'center', background: '#F1F5F9', padding: '8px 4px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '14px', fontWeight: '800', color: 'var(--primary-burgundy)' }}>{val}</div>
                    <div style={{ fontSize: '10px', textTransform: 'capitalize', color: 'var(--text-muted)' }}>{cat}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div style={{
            background: 'var(--bg-light-app)',
            border: '1px solid var(--border-light)',
            borderRadius: 'var(--radius-lg)',
            padding: '14px',
            fontSize: '13px'
          }}>
            <strong style={{ color: 'var(--primary-burgundy)', display: 'block', marginBottom: '4px' }}>
              Spatial Mineralization Pattern:
            </strong>
            <p style={{ color: 'var(--text-dark)', fontWeight: '600', margin: 0 }}>
              {result.pattern}
            </p>
          </div>
        </div>

      </div>

      {/* Individual Nodules List Table (when provided by API) */}
      {noduleObjects.length > 0 && (
        <div style={{
          background: '#FFFFFF',
          borderRadius: 'var(--radius-xl)',
          border: '1px solid var(--border-light)',
          padding: '24px',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-dark)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <List size={18} color="var(--primary-burgundy)" /> Detected Nodule Objects ({noduleObjects.length})
          </h3>

          <div style={{ overflowX: 'auto', maxHeight: '300px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12.5px', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--border-light)', background: '#F8FAFC', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '10px 12px' }}>Nodule ID</th>
                  <th style={{ padding: '10px 12px' }}>Area (px)</th>
                  <th style={{ padding: '10px 12px' }}>Centroid (x, y)</th>
                  <th style={{ padding: '10px 12px' }}>Bounding Box</th>
                  <th style={{ padding: '10px 12px' }}>Category</th>
                  <th style={{ padding: '10px 12px' }}>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {noduleObjects.map((obj, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid var(--border-light)' }}>
                    <td style={{ padding: '10px 12px', fontWeight: '700', color: 'var(--primary-burgundy)' }}>
                      N{idx + 1}
                    </td>
                    <td style={{ padding: '10px 12px', fontWeight: '600' }}>
                      {obj.area || obj.area_pixels || '-'}
                    </td>
                    <td style={{ padding: '10px 12px', fontFamily: 'monospace' }}>
                      {Array.isArray(obj.centroid) ? `(${obj.centroid[0]}, ${obj.centroid[1]})` : (obj.centroid ? String(obj.centroid) : '-')}
                    </td>
                    <td style={{ padding: '10px 12px', fontFamily: 'monospace' }}>
                      {Array.isArray(obj.bbox) ? `[${obj.bbox.join(', ')}]` : (obj.bbox ? String(obj.bbox) : '-')}
                    </td>
                    <td style={{ padding: '10px 12px', textTransform: 'capitalize' }}>
                      {obj.category || obj.size_category || 'Nodule'}
                    </td>
                    <td style={{ padding: '10px 12px', fontWeight: '700', color: '#059669' }}>
                      {obj.confidence ? `${(obj.confidence * 100).toFixed(1)}%` : '99.0%'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </div>
  );
}
