import React from 'react';
import { AlertTriangle, X } from 'lucide-react';

export default function ConfirmModal({ isOpen, title, message, confirmLabel = 'Confirm Action', onConfirm, onClose, isDanger = true }) {
  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(41, 24, 29, 0.55)',
      backdropFilter: 'blur(6px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1100,
      padding: '1.5rem'
    }}>
      <div className="glass-panel" style={{
        width: '100%',
        maxWidth: '480px',
        display: 'flex',
        flexDirection: 'column',
        border: isDanger ? '1px solid #fecdd3' : '1px solid #bae6fd',
        boxShadow: '0 20px 50px rgba(41, 24, 29, 0.2)',
        borderRadius: '16px',
        overflow: 'hidden',
        background: '#ffffff',
        animation: 'slideUp 0.25s cubic-bezier(0.16, 1, 0.3, 1)'
      }}>
        {/* Header */}
        <div style={{
          padding: '1.25rem 1.5rem',
          borderBottom: '1px solid #e6ded6',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: isDanger ? '#fff1f2' : '#f0f9ff'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <AlertTriangle size={22} color={isDanger ? '#9f1239' : '#0284c7'} />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#29181d' }} className="title-font">
              {title || 'Confirm Action'}
            </h3>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#6b5860',
              cursor: 'pointer',
              padding: '0.2rem',
              borderRadius: '4px'
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: '1.5rem 1.5rem 1.25rem 1.5rem' }}>
          <p style={{ fontSize: '0.9rem', color: '#475569', lineHeight: 1.5 }}>
            {message}
          </p>
        </div>

        {/* Footer Actions */}
        <div style={{
          padding: '1rem 1.5rem',
          borderTop: '1px solid #e6ded6',
          display: 'flex',
          justifyContent: 'flex-end',
          gap: '0.75rem',
          background: '#faf6f1'
        }}>
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button
            onClick={() => {
              onConfirm();
              onClose();
            }}
            className={isDanger ? 'btn-danger' : 'btn-primary'}
            style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
