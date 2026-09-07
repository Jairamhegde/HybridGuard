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
      borderBottom: '1px solid #e2e8f0'
    }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.02em' }} className="title-font">
          {pageTitle}
        </h1>
        <p style={{ fontSize: '0.875rem', color: '#475569', marginTop: '0.2rem' }}>
          {pageSubtitle}
        </p>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          background: '#f1f5f9',
          padding: '0.4rem 0.85rem',
          borderRadius: '20px',
          border: '1px solid #e2e8f0',
          fontSize: '0.78rem',
          color: '#475569'
        }}>
          <Server size={14} color="#0284c7" />
          <span>Platforms: <strong style={{ color: '#0f172a' }}>AD · AWS · Okta</strong></span>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          background: '#f1f5f9',
          padding: '0.4rem 0.85rem',
          borderRadius: '20px',
          border: '1px solid #e2e8f0',
          fontSize: '0.78rem',
          color: '#475569'
        }}>
          <Activity size={14} color="#16a34a" />
          <span>Status: <strong style={{ color: '#16a34a' }}>Live Watchlist</strong></span>
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
