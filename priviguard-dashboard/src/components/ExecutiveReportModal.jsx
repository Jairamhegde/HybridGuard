import React from 'react';
import { X, Download, FileText } from 'lucide-react';

export default function ExecutiveReportModal({ reportText, onClose }) {
  const handleDownload = () => {
    const blob = new Blob([reportText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `identity_risk_summary_${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(15, 23, 42, 0.5)',
      backdropFilter: 'blur(6px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '1.5rem'
    }}>
      <div className="glass-panel" style={{
        width: '100%',
        maxWidth: '750px',
        maxHeight: '85vh',
        display: 'flex',
        flexDirection: 'column',
        border: '1px solid #bae6fd',
        boxShadow: '0 20px 50px rgba(0, 0, 0, 0.15)',
        borderRadius: '16px',
        overflow: 'hidden',
        background: '#ffffff'
      }}>
        {/* Header */}
        <div style={{
          padding: '1.25rem 1.5rem',
          borderBottom: '1px solid #e2e8f0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#f8fafc'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <FileText size={20} color="#0284c7" />
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a' }} className="title-font">
              Executive Risk Summary Report
            </h3>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#64748b',
              cursor: 'pointer',
              padding: '0.2rem',
              borderRadius: '4px'
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Text area body */}
        <div style={{ padding: '1.5rem', flex: 1, overflowY: 'auto' }}>
          <pre style={{
            fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
            fontSize: '0.85rem',
            color: '#0f172a',
            background: '#f8fafc',
            padding: '1.25rem',
            borderRadius: '10px',
            border: '1px solid #e2e8f0',
            whiteSpace: 'pre-wrap',
            lineHeight: 1.6
          }}>
            {reportText || 'Generating report...'}
          </pre>
        </div>

        {/* Footer actions */}
        <div style={{
          padding: '1rem 1.5rem',
          borderTop: '1px solid #e2e8f0',
          display: 'flex',
          justifyContent: 'flex-end',
          gap: '0.75rem',
          background: '#f8fafc'
        }}>
          <button onClick={onClose} className="btn-secondary">
            Close
          </button>
          <button onClick={handleDownload} className="btn-primary">
            <Download size={16} />
            <span>Download Report (.txt)</span>
          </button>
        </div>
      </div>
    </div>
  );
}
