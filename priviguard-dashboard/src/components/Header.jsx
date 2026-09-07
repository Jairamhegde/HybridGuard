import React from 'react';
import { Server, Activity, Calendar } from 'lucide-react';

export default function Header({ pageTitle, pageSubtitle }) {
  const currentDate = new Date().toLocaleDateString('en-US', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  });

  return (
    <header style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      paddingBottom: '1.25rem',
      marginBottom: '1.75rem',
      borderBottom: '1px solid rgba(255, 255, 255, 0.08)'
    }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em' }} className="title-font">
          {pageTitle}
        </h1>
        <p style={{ fontSize: '0.875rem', color: '#94a3b8', marginTop: '0.2rem' }}>
          {pageSubtitle}
        </p>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          background: 'rgba(30, 41, 59, 0.6)',
          padding: '0.4rem 0.85rem',
          borderRadius: '20px',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          fontSize: '0.78rem',
          color: '#cbd5e1'
        }}>
          <Server size={14} color="#38bdf8" />
          <span>Platforms: <strong style={{ color: '#f8fafc' }}>AD · AWS · Okta</strong></span>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          background: 'rgba(30, 41, 59, 0.6)',
          padding: '0.4rem 0.85rem',
          borderRadius: '20px',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          fontSize: '0.78rem',
          color: '#cbd5e1'
        }}>
          <Activity size={14} color="#10b981" />
          <span>Status: <strong style={{ color: '#10b981' }}>Live Watchlist</strong></span>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.4rem',
          fontSize: '0.78rem',
          color: '#64748b'
        }}>
          <Calendar size={14} color="#64748b" />
          <span>{currentDate}</span>
        </div>
      </div>
    </header>
  );
}
