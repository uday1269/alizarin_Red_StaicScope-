import React, { useState, useRef } from 'react';
import { 
  UploadCloud, 
  Sliders, 
  Play, 
  Trash2, 
  CheckCircle2,
  Maximize2,
  RefreshCw,
  Sparkles,
  AlertCircle,
  Microscope
} from 'lucide-react';

export default function UploadScreen({ onNavigate, analysesHistory }) {
  const fileInputRef = useRef(null);
  
  // Primary Workflow: Single uploaded image with visible preview (starts clean null)
  const [uploadedFile, setUploadedFile] = useState(null);

  // Optional Research Metadata
  const [sampleName, setSampleName] = useState('');
  const [cellLine, setCellLine] = useState('');
  const [treatment, setTreatment] = useState('');
  const [day, setDay] = useState('');
  const [magnification, setMagnification] = useState('20x Objective (Auto-detected)');
  const [dragOver, setDragOver] = useState(false);

  // Duplicate Confirmation Modal State
  const [showDuplicateModal, setShowDuplicateModal] = useState(false);

  /**
   * Duplicate image detection strictly against user's actual analysis history.
   */
  const checkIsDuplicateImage = (fileObj, history = []) => {
    if (!fileObj || !history || history.length === 0) return null;

    const targetName = (fileObj.name || '').toLowerCase().trim();
    if (!targetName) return null;

    return history.find((item) => {
      if (fileObj.fileHash && item.imageHash && fileObj.fileHash === item.imageHash) {
        return true;
      }
      const itemTitle = (item.title || '').toLowerCase().trim();
      const itemFileName = (item.rawDbRecord?.micrographs?.original_name || item.rawDbRecord?.micrographs?.file_name || item.fileName || '').toLowerCase().trim();

      return itemFileName === targetName || (itemTitle && itemTitle === targetName);
    }) || null;
  };

  const processUploadedFile = (file) => {
    if (!file) return;

    // Generate Object URL for instant thumbnail preview
    const objectUrl = URL.createObjectURL(file);
    const img = new Image();

    img.onload = () => {
      const resStr = `${img.naturalWidth} × ${img.naturalHeight} px`;
      setUploadedFile({
        name: file.name,
        size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
        resolution: resStr,
        previewUrl: objectUrl,
        fileRef: file
      });
    };

    img.onerror = () => {
      setUploadedFile({
        name: file.name,
        size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
        resolution: '2048 × 1536 px',
        previewUrl: objectUrl,
        fileRef: file
      });
    };

    img.src = objectUrl;
  };

  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files && files[0]) {
      processUploadedFile(files[0]);
    }
  };

  const handleRemoveImage = () => {
    if (uploadedFile?.previewUrl && uploadedFile.previewUrl.startsWith('blob:')) {
      URL.revokeObjectURL(uploadedFile.previewUrl);
    }
    setUploadedFile(null);
  };

  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleStartAnalysis = () => {
    if (!uploadedFile || isSubmitting) return;

    // Check for duplicate upload against existing analysis history
    const isDuplicate = checkIsDuplicateImage(uploadedFile, analysesHistory);

    if (isDuplicate) {
      setShowDuplicateModal(true);
      return;
    }

    executeStartAnalysis();
  };

  const executeStartAnalysis = async () => {
    if (!uploadedFile || isSubmitting) return;

    setIsSubmitting(true);

    const sampleTitle = sampleName.trim() || uploadedFile.name.replace(/\.[^/.]+$/, "");
    const cellLineText = cellLine.trim() || "Not specified";
    const treatmentText = treatment.trim() || "Unspecified Treatment";
    const dayText = day.trim() 
      ? (day.toLowerCase().startsWith('day') ? day.trim() : `Day ${day.trim()}`) 
      : "Not specified";
    const magText = magnification.trim() || "20x Objective";

    let fileToUpload = uploadedFile.fileRef;

    // If initial demo image or URL without fileRef, fetch previewUrl as File
    if (!fileToUpload && uploadedFile.previewUrl) {
      try {
        const resp = await fetch(uploadedFile.previewUrl);
        const blob = await resp.blob();
        fileToUpload = new File([blob], uploadedFile.name || 'micrograph.png', { type: blob.type || 'image/png' });
      } catch (e) {
        console.warn('Could not fetch preview image as File:', e);
      }
    }

    const payload = {
      file: fileToUpload,
      metadata: {
        sampleTitle,
        cellLineText,
        treatmentText,
        dayText,
        magText,
        fileName: uploadedFile.name,
        resolution: uploadedFile.resolution,
        previewUrl: uploadedFile.previewUrl
      }
    };

    onNavigate('processing', payload);
    setIsSubmitting(false);
  };

  return (
    <div className="animate-fade-in" style={{ padding: '24px 24px 48px', maxWidth: '1100px', margin: '0 auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '26px', fontWeight: '800', color: 'var(--text-dark)' }}>
          Micrograph Analysis Workstation
        </h1>
        <p style={{ fontSize: '14px', color: 'var(--text-muted)' }}>
          Upload an Alizarin Red S stained microscopy image to run automated AI stain quantification.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '28px' }}>
        
        {/* Left Column: Image Upload & Uploaded Image Card */}
        <div>
          {/* Section 1: Drag & Drop Zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragOver(false);
              const files = e.dataTransfer.files;
              if (files && files[0]) {
                processUploadedFile(files[0]);
              }
            }}
            onClick={() => fileInputRef.current?.click()}
            style={{
              background: dragOver ? 'var(--primary-burgundy-light)' : 'var(--bg-card)',
              border: `2px dashed ${dragOver ? 'var(--primary-burgundy)' : 'var(--border-light)'}`,
              borderRadius: 'var(--radius-xl)',
              padding: '36px 24px',
              textAlign: 'center',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              marginBottom: '24px',
              boxShadow: 'var(--shadow-sm)'
            }}
          >
            <div style={{
              width: '60px',
              height: '60px',
              borderRadius: '18px',
              background: 'var(--primary-burgundy-light)',
              color: 'var(--primary-burgundy)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 14px'
            }}>
              <UploadCloud size={30} />
            </div>

            <h3 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-dark)', marginBottom: '4px' }}>
              {uploadedFile ? 'Click or drag to replace image' : 'Drag & drop Alizarin Red micrograph here'}
            </h3>
            <p style={{ fontSize: '12.5px', color: 'var(--text-muted)', marginBottom: '16px' }}>
              Supports TIFF, PNG, JPG files up to 50MB (EVOS, Leica, Zeiss, Olympus)
            </p>

            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileSelect} 
              style={{ display: 'none' }} 
              accept=".tif,.tiff,.png,.jpg,.jpeg" 
            />

            <button 
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                fileInputRef.current?.click();
              }}
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--primary-burgundy)',
                color: 'var(--primary-burgundy)',
                padding: '8px 20px',
                borderRadius: 'var(--radius-md)',
                fontSize: '13px',
                fontWeight: '700',
                cursor: 'pointer'
              }}
            >
              Browse Microscopy File
            </button>
          </div>

          {/* Section 2: Uploaded Image Card with Clear Visible Thumbnail & Exact Filename */}
          {uploadedFile ? (
            <div style={{
              background: 'var(--bg-card)',
              borderRadius: 'var(--radius-xl)',
              border: '1px solid var(--border-light)',
              padding: '20px',
              boxShadow: 'var(--shadow-sm)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <span style={{ fontSize: '12px', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>
                  Uploaded Image
                </span>
                <span style={{ fontSize: '11.5px', color: '#059669', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <CheckCircle2 size={14} /> Ready for Analysis
                </span>
              </div>

              {/* Preview Thumbnail Container */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                padding: '16px',
                borderRadius: 'var(--radius-lg)',
                background: 'var(--bg-light-app)',
                border: '1px solid var(--border-light)'
              }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  borderRadius: '12px',
                  overflow: 'hidden',
                  border: '1px solid var(--primary-burgundy-border)',
                  flexShrink: 0,
                  background: 'var(--primary-burgundy-light)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  {uploadedFile.previewUrl ? (
                    <img
                      src={uploadedFile.previewUrl}
                      alt={uploadedFile.name}
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      onError={(e) => {
                        e.target.style.display = 'none';
                      }}
                    />
                  ) : (
                    <Microscope size={32} color="var(--primary-burgundy)" />
                  )}
                </div>

                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: '14.5px', fontWeight: '700', color: 'var(--text-dark)', wordBreak: 'break-all', marginBottom: '4px' }}>
                    {uploadedFile.name}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                    <span>{uploadedFile.size}</span>
                    <span>•</span>
                    <span style={{ color: 'var(--primary-burgundy)', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Maximize2 size={12} /> {uploadedFile.resolution}
                    </span>
                  </div>
                </div>
              </div>

              {/* Controls */}
              <div style={{ display: 'flex', gap: '10px', marginTop: '14px' }}>
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  style={{
                    flex: '1',
                    background: 'var(--bg-light-app)',
                    border: '1px solid var(--border-light)',
                    color: 'var(--text-dark)',
                    padding: '9px 12px',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '12.5px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px'
                  }}
                >
                  <RefreshCw size={14} /> Replace Image
                </button>

                <button
                  type="button"
                  onClick={handleRemoveImage}
                  style={{
                    background: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid rgba(239, 68, 68, 0.2)',
                    color: '#EF4444',
                    padding: '9px 12px',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '12.5px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px'
                  }}
                >
                  <Trash2 size={14} /> Remove
                </button>
              </div>
            </div>
          ) : (
            <div style={{
              background: 'var(--bg-card)',
              borderRadius: 'var(--radius-xl)',
              border: '1px solid var(--border-light)',
              padding: '24px',
              textAlign: 'center',
              color: 'var(--text-muted)',
              fontSize: '13px'
            }}>
              No image uploaded. Drag &amp; drop or click above to select an Alizarin Red S micrograph.
            </div>
          )}
        </div>

        {/* Right Column: Section 3: Optional Metadata + Section 4: Start AI Stain Quantification */}
        <div>
          <div style={{
            background: 'var(--bg-card)',
            borderRadius: 'var(--radius-xl)',
            border: '1px solid var(--border-light)',
            padding: '24px',
            boxShadow: 'var(--shadow-sm)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-dark)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sliders size={18} color="var(--primary-burgundy)" /> Research Metadata
              </h3>
              <span style={{
                fontSize: '11px',
                fontWeight: '700',
                background: 'var(--bg-light-app)',
                color: 'var(--text-muted)',
                padding: '3px 8px',
                borderRadius: '12px',
                border: '1px solid var(--border-light)'
              }}>
                Optional
              </span>
            </div>

            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '18px', lineHeight: '1.4' }}>
              Adding experimental details is optional. You can start analysis immediately or enter details below to enrich your reports and multi-sample comparisons.
            </p>

            {/* Sample / Experiment Name */}
            <div className="form-group">
              <label className="form-label">Sample / Experiment Name <span style={{ fontWeight: '400', color: 'var(--text-muted)' }}>(Optional)</span></label>
              <input
                type="text"
                className="form-input"
                value={sampleName}
                onChange={(e) => setSampleName(e.target.value)}
                placeholder={uploadedFile ? uploadedFile.name.replace(/\.[^/.]+$/, "") : "e.g. Control_Day14"}
              />
            </div>

            {/* Cell Line / Tissue Origin */}
            <div className="form-group">
              <label className="form-label">Cell Line / Tissue Origin <span style={{ fontWeight: '400', color: 'var(--text-muted)' }}>(Optional)</span></label>
              <input
                type="text"
                className="form-input"
                value={cellLine}
                onChange={(e) => setCellLine(e.target.value)}
                placeholder="e.g. hMSC, MC3T3-E1, or leave blank"
              />
            </div>

            {/* Treatment / Induction Agent */}
            <div className="form-group">
              <label className="form-label">Treatment / Induction Agent <span style={{ fontWeight: '400', color: 'var(--text-muted)' }}>(Optional)</span></label>
              <input
                type="text"
                className="form-input"
                value={treatment}
                onChange={(e) => setTreatment(e.target.value)}
                placeholder="e.g. BMP-2 (100ng/ml) + Osteogenic Medium"
              />
            </div>

            {/* Differentiation Day & Objective Lens */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div className="form-group">
                <label className="form-label">Differentiation Day <span style={{ fontWeight: '400', color: 'var(--text-muted)' }}>(Optional)</span></label>
                <input
                  type="text"
                  className="form-input"
                  value={day}
                  onChange={(e) => setDay(e.target.value)}
                  placeholder="e.g. 14, Day 21"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Objective / Magnification <span style={{ fontWeight: '400', color: 'var(--text-muted)' }}>(Optional)</span></label>
                <select 
                  className="form-input" 
                  value={magnification} 
                  onChange={(e) => setMagnification(e.target.value)}
                >
                  <option value="20x Objective (Auto-detected)">Auto-detected (20x Standard)</option>
                  <option value="10x Objective (Wide Field)">10x Objective</option>
                  <option value="20x Objective (Standard)">20x Objective</option>
                  <option value="40x Objective (High Detail)">40x Objective</option>
                </select>
              </div>
            </div>

            {/* Internal Processing Notice */}
            <div style={{
              background: 'var(--primary-burgundy-light)',
              border: '1px solid var(--primary-burgundy-border)',
              borderRadius: 'var(--radius-md)',
              padding: '12px 14px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              fontSize: '12px',
              color: 'var(--primary-burgundy)',
              marginBottom: '20px'
            }}>
              <Sparkles size={16} style={{ flexShrink: 0 }} />
              <div>
                <strong>Auto-Analysis Active:</strong> Alizarin Red S (~560nm) optical segmentation pipeline automatically configured.
              </div>
            </div>

            {/* Section 4: Start AI Stain Quantification */}
            <button
              onClick={handleStartAnalysis}
              disabled={!uploadedFile}
              className="btn-primary-burgundy hover-lift"
              style={{
                height: '52px',
                fontSize: '16px',
                opacity: !uploadedFile ? 0.5 : 1,
                cursor: !uploadedFile ? 'not-allowed' : 'pointer'
              }}
            >
              <Play size={20} fill="#FFF" /> Start AI Stain Quantification
            </button>
          </div>
        </div>

      </div>

      {/* Duplicate Image Confirmation Modal */}
      {showDuplicateModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(15, 23, 42, 0.65)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          padding: '20px'
        }}>
          <div className="animate-fade-in" style={{
            background: 'var(--bg-card)',
            borderRadius: '20px',
            border: '1px solid var(--border-light)',
            padding: '32px',
            maxWidth: '480px',
            width: '100%',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
          }}>
            <div style={{
              width: '52px',
              height: '52px',
              borderRadius: '16px',
              background: 'var(--primary-burgundy-light)',
              color: 'var(--primary-burgundy)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '20px'
            }}>
              <AlertCircle size={28} />
            </div>

            <h3 style={{ fontSize: '20px', fontWeight: '800', color: 'var(--text-dark)', marginBottom: '10px' }}>
              This image has already been analyzed.
            </h3>

            <p style={{ fontSize: '14px', color: 'var(--text-muted)', lineHeight: '1.55', marginBottom: '28px' }}>
              This microscopy image already has a completed analysis. Do you want to analyze it again?
            </p>

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
              <button
                type="button"
                onClick={() => setShowDuplicateModal(false)}
                style={{
                  flex: 1,
                  padding: '12px 18px',
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--bg-light-app)',
                  border: '1px solid var(--border-light)',
                  color: 'var(--text-dark)',
                  fontWeight: '600',
                  fontSize: '14px',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={() => {
                  setShowDuplicateModal(false);
                  executeStartAnalysis();
                }}
                className="btn-primary-burgundy"
                style={{
                  flex: 1,
                  padding: '12px 18px',
                  borderRadius: 'var(--radius-md)',
                  fontWeight: '700',
                  fontSize: '14px',
                  cursor: 'pointer',
                  justifyContent: 'center'
                }}
              >
                Analyze Again
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
