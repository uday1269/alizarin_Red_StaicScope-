import React, { useState } from 'react';
import { 
  Search, 
  Grid, 
  List, 
  Microscope, 
  Star, 
  X, 
  RotateCw, 
  ArrowUpDown,
  GitCompare
} from 'lucide-react';

export default function HistoryScreen({ onNavigate, analysesHistory, onDeleteAnalysis }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('All');
  const [sortBy, setSortBy] = useState('date'); // 'date' | 'area' | 'nodules'
  const [viewMode, setViewMode] = useState('list'); // 'list' | 'grid'
  
  const allScans = analysesHistory || [];
  const [favorites, setFavorites] = useState([]);
  const [selectedScanIds, setSelectedScanIds] = useState([]);

  const toggleFavorite = (id) => {
    setFavorites((prev) => 
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const toggleSelectScan = (id) => {
    setSelectedScanIds((prev) => 
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleDelete = (item) => {
    if (onDeleteAnalysis) {
      onDeleteAnalysis(item);
      setSelectedScanIds((prev) => prev.filter((i) => i !== item.id));
    }
  };

  const handleLaunchCompare = () => {
    const chosenSamples = allScans.filter((item) => selectedScanIds.includes(item.id));
    if (chosenSamples.length < 2) return;
    onNavigate('compare', { selectedSamples: chosenSamples });
  };

  const filteredItems = allScans
    .filter((item) => {
      const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                            item.id.toLowerCase().includes(searchTerm.toLowerCase());
      if (activeFilter === 'All') return matchesSearch;
      return matchesSearch && item.status.toLowerCase().includes(activeFilter.toLowerCase());
    })
    .sort((a, b) => {
      if (sortBy === 'area') return b.mineralizedAreaValue - a.mineralizedAreaValue;
      if (sortBy === 'nodules') return b.nodulesCount - a.nodulesCount;
      return b.id.localeCompare(a.id); // Default newest date/ID
    });

  return (
    <div className="animate-fade-in" style={{ padding: '24px 24px 48px', maxWidth: '1200px', margin: '0 auto' }}>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: '800', color: 'var(--text-dark)' }}>Stain Analysis Repository</h1>
          <p style={{ fontSize: '14px', color: 'var(--text-muted)' }}>
            Search, sort, filter, favorite, and compare processed Alizarin Red S tissue micrographs.
          </p>
        </div>

        <button
          onClick={handleLaunchCompare}
          disabled={selectedScanIds.length < 2}
          style={{
            background: selectedScanIds.length >= 2 ? 'var(--primary-burgundy)' : '#E2E8F0',
            color: selectedScanIds.length >= 2 ? '#FFFFFF' : '#94A3B8',
            border: 'none',
            padding: '12px 22px',
            borderRadius: 'var(--radius-md)',
            fontWeight: '700',
            fontSize: '14px',
            cursor: selectedScanIds.length >= 2 ? 'pointer' : 'not-allowed',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            boxShadow: selectedScanIds.length >= 2 ? '0 4px 14px rgba(128,29,30,0.25)' : 'none',
            transition: 'all 0.2s ease'
          }}
        >
          <GitCompare size={18} /> Compare Selected Analyses ({selectedScanIds.length})
        </button>
      </div>

      {/* Search, Sort & Filter Controls Bar */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: '16px',
        flexWrap: 'wrap',
        marginBottom: '28px'
      }}>
        {/* Search Input */}
        <div style={{ position: 'relative', flex: '1', minWidth: '260px' }}>
          <Search size={18} style={{ position: 'absolute', left: '14px', top: '15px', color: 'var(--text-muted)' }} />
          <input
            type="text"
            className="form-input"
            placeholder="Search by sample ID, cell line, or treatment..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ paddingLeft: '42px' }}
          />
        </div>

        {/* Sort Dropdown */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <ArrowUpDown size={16} color="var(--text-muted)" />
          <select
            className="form-input"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            style={{ width: '160px', height: '44px', fontSize: '13px', fontWeight: '600' }}
          >
            <option value="date">Sort: Newest Date</option>
            <option value="area">Sort: Highest Area %</option>
            <option value="nodules">Sort: Nodule Count</option>
          </select>
        </div>

        {/* Filter Pills */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {['All', 'High', 'Moderate', 'Low'].map((filter) => (
            <button
              key={filter}
              onClick={() => setActiveFilter(filter)}
              style={{
                background: activeFilter === filter ? 'var(--primary-burgundy)' : 'var(--bg-card)',
                color: activeFilter === filter ? '#FFFFFF' : 'var(--text-dark)',
                border: `1px solid ${activeFilter === filter ? 'var(--primary-burgundy)' : 'var(--border-light)'}`,
                padding: '8px 16px',
                borderRadius: '20px',
                fontSize: '13px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              {filter === 'All' ? 'All Scans' : `${filter}`}
            </button>
          ))}
        </div>

        {/* View Mode Toggle */}
        <div style={{ display: 'flex', gap: '4px', background: 'var(--bg-card)', padding: '4px', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-md)' }}>
          <button
            onClick={() => setViewMode('list')}
            style={{
              background: viewMode === 'list' ? 'var(--primary-burgundy-light)' : 'transparent',
              color: viewMode === 'list' ? 'var(--primary-burgundy)' : 'var(--text-muted)',
              border: 'none',
              padding: '6px 10px',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            <List size={16} />
          </button>
          <button
            onClick={() => setViewMode('grid')}
            style={{
              background: viewMode === 'grid' ? 'var(--primary-burgundy-light)' : 'transparent',
              color: viewMode === 'grid' ? 'var(--primary-burgundy)' : 'var(--text-muted)',
              border: 'none',
              padding: '6px 10px',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            <Grid size={16} />
          </button>
        </div>
      </div>

      {/* History Items Container */}
      {viewMode === 'list' ? (
        <div style={{
          background: '#FFFFFF',
          borderRadius: 'var(--radius-xl)',
          border: '1px solid var(--border-light)',
          boxShadow: 'var(--shadow-sm)',
          overflow: 'hidden'
        }}>
          {filteredItems.length > 0 ? (
            filteredItems.map((item, idx) => {
              const isFav = favorites.includes(item.id);
              const isSelected = selectedScanIds.includes(item.id);
              return (
                <div
                  key={item.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '20px',
                    borderBottom: idx < filteredItems.length - 1 ? '1px solid #F1F5F9' : 'none',
                    gap: '16px',
                    flexWrap: 'wrap',
                    background: isSelected ? 'var(--primary-burgundy-light)' : 'transparent',
                    transition: 'background 0.2s ease'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flex: '1', minWidth: '280px' }}>
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggleSelectScan(item.id)}
                      style={{ width: '18px', height: '18px', accentColor: 'var(--primary-burgundy)', cursor: 'pointer' }}
                      title="Select for multi-sample comparison"
                    />

                    <button
                      onClick={() => toggleFavorite(item.id)}
                      style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px' }}
                      title={isFav ? 'Unstar sample' : 'Star sample as favorite'}
                    >
                      <Star size={18} fill={isFav ? '#F59E0B' : 'transparent'} color={isFav ? '#F59E0B' : '#94A3B8'} />
                    </button>

                    <div style={{
                      width: '44px',
                      height: '44px',
                      borderRadius: '12px',
                      background: '#FFF1F1',
                      border: '1px solid #FCA5A5',
                      overflow: 'hidden',
                      flexShrink: 0,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'var(--primary-burgundy)',
                      fontWeight: '700'
                    }}>
                      {(item.imageUrl || item.thumbnailUrl || item.overlay || item.overlays?.nodule_map) ? (
                        <img
                          src={item.imageUrl || item.thumbnailUrl || item.overlay || item.overlays?.nodule_map}
                          alt={item.title}
                          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        />
                      ) : (
                        <Microscope size={20} />
                      )}
                    </div>
                    <div>
                      <h4 style={{ fontSize: '15px', fontWeight: '700', color: 'var(--text-dark)', marginBottom: '2px' }}>
                        {item.title}
                      </h4>
                      <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        ID: <strong>{item.id}</strong> • {item.date} • Magnification: {item.magnification}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '16px', fontWeight: '800', color: 'var(--primary-burgundy)' }}>
                        {item.mineralizedArea}
                      </div>
                      <div style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>
                        OD: {item.stainIntensityOD}
                      </div>
                    </div>

                    <button
                      onClick={() => onNavigate('results', { analysis: item })}
                      className="btn-primary-burgundy"
                      style={{ padding: '8px 16px', fontSize: '13px' }}
                    >
                      View Report
                    </button>

                    <button
                      onClick={() => onNavigate('compare', { sampleA: item })}
                      style={{ background: '#F1F5F9', border: 'none', padding: '8px', borderRadius: 'var(--radius-md)', cursor: 'pointer', color: 'var(--text-dark)' }}
                      title="Compare sample"
                    >
                      <GitCompare size={16} />
                    </button>

                    <button
                      onClick={() => onNavigate('processing', { analysis: item })}
                      style={{ background: '#F1F5F9', border: 'none', padding: '8px', borderRadius: 'var(--radius-md)', cursor: 'pointer', color: 'var(--text-muted)' }}
                      title="Re-analyze sample"
                    >
                      <RotateCw size={16} />
                    </button>

                    <button
                      onClick={() => handleDelete(item)}
                      style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', padding: '8px', borderRadius: 'var(--radius-md)', cursor: 'pointer', color: 'var(--text-muted)' }}
                      title="Move to Recently Deleted"
                    >
                      <X size={16} />
                    </button>
                  </div>
                </div>
              );
            })
          ) : (
            <div style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
              No history records match your search filter.
            </div>
          )}
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '20px'
        }}>
          {filteredItems.map((item) => (
            <div
              key={item.id}
              className="hover-lift"
              style={{
                background: '#FFFFFF',
                borderRadius: 'var(--radius-xl)',
                border: selectedScanIds.includes(item.id) ? '2px solid var(--primary-burgundy)' : '1px solid var(--border-light)',
                padding: '20px',
                boxShadow: 'var(--shadow-sm)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between'
              }}
            >
              <div>
                {/* Image Banner */}
                {(item.imageUrl || item.thumbnailUrl || item.overlay || item.overlays?.nodule_map) && (
                  <div style={{
                    width: '100%',
                    height: '130px',
                    borderRadius: '12px',
                    overflow: 'hidden',
                    marginBottom: '14px',
                    border: '1px solid var(--border-light)',
                    background: '#090A0F'
                  }}>
                    <img
                      src={item.imageUrl || item.thumbnailUrl || item.overlay || item.overlays?.nodule_map}
                      alt={item.title}
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  </div>
                )}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input
                      type="checkbox"
                      checked={selectedScanIds.includes(item.id)}
                      onChange={() => toggleSelectScan(item.id)}
                      style={{ width: '16px', height: '16px', accentColor: 'var(--primary-burgundy)', cursor: 'pointer' }}
                      title="Select for comparison"
                    />
                    <span style={{
                      padding: '4px 10px',
                      borderRadius: '16px',
                      fontSize: '11px',
                      fontWeight: '700',
                      backgroundColor: item.statusColor + '18',
                      color: item.statusColor,
                      border: `1px solid ${item.statusColor}40`
                    }}>
                      {item.status}
                    </span>
                  </div>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{item.date}</span>
                </div>

                <h4 style={{ fontSize: '15px', fontWeight: '700', color: 'var(--text-dark)', marginBottom: '8px' }}>
                  {item.title}
                </h4>

                <div style={{
                  background: 'var(--bg-light-app)',
                  padding: '12px',
                  borderRadius: 'var(--radius-md)',
                  marginBottom: '16px',
                  fontSize: '13px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Mineralized Area:</span>
                    <strong style={{ color: 'var(--primary-burgundy)' }}>{item.mineralizedArea}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Stain OD:</span>
                    <strong>{item.stainIntensityOD}</strong>
                  </div>
                </div>
              </div>

              <button
                onClick={() => onNavigate('results', { analysis: item })}
                className="btn-primary-burgundy"
                style={{ height: '42px', fontSize: '13px', marginBottom: 0 }}
              >
                View Results Report
              </button>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}
