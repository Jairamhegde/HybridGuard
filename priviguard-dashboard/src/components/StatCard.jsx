import React from 'react';

export default function StatCard({ label, value, subtitle, icon: Icon, accent = 'rose' }) {
  const accentColors = {
    rose: { text: '#be123c', border: '#fecdd3', bg: '#fff1f2' },
    red: { text: '#9f1239', border: '#fecdd3', bg: '#fff1f2' },
    orange: { text: '#c2410c', border: '#ffedd5', bg: '#fff7ed' },
    yellow: { text: '#b45309', border: '#fef08a', bg: '#fefce8' },
    green: { text: '#0f766e', border: '#ccfbf1', bg: '#f0fdfa' },
  };

  const style = accentColors[accent] || accentColors.rose;

  return (
    <div className="glass-panel glass-panel-hover" style={{
      padding: '1.25rem 1.4rem',
      borderLeft: `4px solid ${style.text}`,
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }}>
      <div>
        <p style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: '#6b5860', marginBottom: '0.35rem' }}>
          {label}
        </p>
        <h3 style={{ fontSize: '1.9rem', fontWeight: 800, color: '#29181d', lineHeight: 1.1 }} className="title-font">
          {value}
        </h3>
        {subtitle && (
          <p style={{ fontSize: '0.78rem', color: '#6b5860', marginTop: '0.3rem' }}>
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
