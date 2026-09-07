import React from 'react';

export default function StatCard({ label, value, subtitle, icon: Icon, accent = 'cyan' }) {
  const accentColors = {
    cyan: { text: '#0284c7', border: '#bae6fd', bg: '#f0f9ff' },
    red: { text: '#dc2626', border: '#fca5a5', bg: '#fef2f2' },
    orange: { text: '#ea580c', border: '#fdba74', bg: '#fff7ed' },
    yellow: { text: '#ca8a04', border: '#fde047', bg: '#fefce8' },
    green: { text: '#16a34a', border: '#bbf7d0', bg: '#f0fdf4' },
  };

  const style = accentColors[accent] || accentColors.cyan;

  return (
    <div className="glass-panel glass-panel-hover" style={{
      padding: '1.25rem 1.4rem',
      borderLeft: `4px solid ${style.text}`,
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }}>
      <div>
        <p style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: '#64748b', marginBottom: '0.35rem' }}>
          {label}
        </p>
        <h3 style={{ fontSize: '1.9rem', fontWeight: 800, color: '#0f172a', lineHeight: 1.1 }} className="title-font">
          {value}
        </h3>
        {subtitle && (
          <p style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '0.3rem' }}>
            {subtitle}
          </p>
        )}
      </div>

      {Icon && (
        <div style={{
          width: '44px',
          height: '44px',
          borderRadius: '10px',
          background: style.bg,
          border: `1px solid ${style.border}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Icon size={22} color={style.text} />
        </div>
      )}
    </div>
  );
}
