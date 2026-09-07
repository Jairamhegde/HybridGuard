import React from 'react';
import { 
  ShieldAlert, 
  Clock, 
  Flame, 
  CheckSquare, 
  Users, 
  RefreshCw,
  ShieldCheck
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, onRefresh, isRefreshing }) {
  const navItems = [
    { id: 'overview', label: 'Overall Threat Posture', icon: ShieldAlert },
    { id: 'dormancy', label: 'Dormancy Analysis', icon: Clock },
    { id: 'damage', label: 'Damage Score', icon: Flame },
    { id: 'remediation', label: 'Remediation Backlog', icon: CheckSquare },
    { id: 'identities', label: 'Identities Directory', icon: Users },
  ];

  return (
    <aside style={{
      width: '260px',
      background: '#ffffff',
      borderRight: '1px solid #e2e8f0',
      display: 'flex',
      flexDirection: 'column',
      minHeight: '100vh',
      padding: '1.5rem 1rem',
      position: 'sticky',
      top: 0,
      boxShadow: '2px 0 10px rgba(0,0,0,0.02)'
    }}>
      {/* Brand Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem', padding: '0 0.5rem' }}>
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '8px',
          background: 'linear-gradient(135deg, #0284c7 0%, #2563eb 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 2px 10px rgba(2, 132, 199, 0.3)'
        }}>
          <ShieldCheck size={22} color="#ffffff" />
        </div>
        <div>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.02em' }} className="title-font">
            HybridGuard
          </h2>
          <p style={{ fontSize: '0.7rem', color: '#0284c7', fontWeight: 700, letterSpacing: '0.05em' }}>
            ISPM CONSOLE
          </p>
        </div>
      </div>

      {/* Navigation Links */}
      <div style={{ flex: 1 }}>
        <p style={{ fontSize: '0.68rem', fontWeight: 700, color: '#94a3b8', letterSpacing: '0.08em', marginBottom: '0.75rem', padding: '0 0.5rem' }}>
          NAVIGATION
        </p>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  padding: '0.65rem 0.85rem',
                  borderRadius: '8px',
                  fontSize: '0.85rem',
                  fontWeight: isActive ? 700 : 500,
                  color: isActive ? '#0284c7' : '#475569',
                  background: isActive ? '#e0f2fe' : 'transparent',
                  border: isActive ? '1px solid #bae6fd' : '1px solid transparent',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.2s ease',
                  width: '100%'
                }}
              >
                <Icon size={18} color={isActive ? '#0284c7' : '#64748b'} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Refresh Data Footer */}
      <div style={{ paddingTop: '1.5rem', borderTop: '1px solid #e2e8f0' }}>
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="btn-secondary"
          style={{ width: '100%', justifyContent: 'center', opacity: isRefreshing ? 0.7 : 1 }}
        >
          <RefreshCw size={15} style={{ animation: isRefreshing ? 'spin 1s linear infinite' : 'none' }} />
          <span>{isRefreshing ? 'Refreshing Cache...' : 'Refresh Data Cache'}</span>
        </button>
      </div>
    </aside>
  );
}
