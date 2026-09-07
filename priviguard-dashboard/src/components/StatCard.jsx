import React from 'react';

export default function StatCard({ label, value, subtitle, icon: Icon, accent = 'cyan' }) {
  const accentColors = {
    cyan: { text: '#38bdf8', border: 'rgba(56, 189, 248, 0.4)', bg: 'rgba(56, 189, 248, 0.1)' },
    red: { text: '#ef4444', border: 'rgba(239, 68, 68, 0.4)', bg: 'rgba(239, 68, 68, 0.1)' },
    orange: { text: '#f97316', border: 'rgba(249, 115, 22, 0.4)', bg: 'rgba(249, 115, 22, 0.1)' },
    yellow: { text: '#eab308', border: 'rgba(234, 179, 8, 0.4)', bg: 'rgba(234, 179, 8, 0.1)' },
    green: { text: '#10b981', border: 'rgba(16, 185, 129, 0.4)', bg: 'rgba(16, 185, 129, 0.1)' },
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
        <p style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: '#94a3b8', marginBottom: '0.35rem' }}>
          {label}
        </p>
        <h3 style={{ fontSize: '1.9rem', fontWeight: 800, color: '#f8fafc', lineHeight: 1.1 }} className="title-font">
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
