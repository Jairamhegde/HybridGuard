import React, { useEffect, useState } from 'react';
import { X, User, Server, Shield, Flame, Clock, AlertTriangle, UserX, KeyRound, CheckCircle2 } from 'lucide-react';

export default function IdentityDrawer({ identityId, onClose, onDisableStatus, API_BASE_URL }) {
  const [lineage, setLineage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!identityId) return;
    setLoading(true);
    fetch(`${API_BASE_URL}/api/identity/${identityId}`)
      .then((res) => res.json())
      .then((data) => {
        setLineage(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load identity lineage", err);
        setLoading(false);
      });
  }, [identityId, API_BASE_URL]);

  if (!identityId) return null;

  const identity = lineage?.identity || {};
  const accounts = lineage?.accounts || [];
  const incidents = lineage?.incidents || [];

  const isHighRisk = (identity.risk_score || 0) >= 60;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(41, 24, 29, 0.4)',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      justifyContent: 'flex-end',
      zIndex: 1050,
      animation: 'fadeIn 0.2s ease'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '560px',
        background: '#ffffff',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '-10px 0 40px rgba(41, 24, 29, 0.15)',
        borderLeft: '1px solid #e6ded6',
        animation: 'slideLeft 0.3s cubic-bezier(0.16, 1, 0.3, 1)'
      }}>
        {/* Header */}
        <div style={{
          padding: '1.25rem 1.5rem',
          borderBottom: '1px solid #e6ded6',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'linear-gradient(135deg, #2a141c 0%, #1d0c14 100%)',
          color: '#ffffff'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #9f1239 0%, #be123c 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 12px rgba(225, 29, 72, 0.4)'
            }}>
              <User size={22} color="#ffffff" />
            </div>
            <div>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.01em' }} className="title-font">
                {identity.full_name || `Identity #${identityId}`}
              </h2>
              <p style={{ fontSize: '0.75rem', color: '#fb7185' }}>
                ID: #{identityId} · {identity.email || 'No email registered'}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{
              background: 'rgba(255, 255, 255, 0.1)',
              border: 'none',
              color: '#f8fafc',
              cursor: 'pointer',
              padding: '0.4rem',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Content Body */}
        {loading ? (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6b5860' }}>
            <p>Loading identity lineage details...</p>
          </div>
        ) : (
          <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', background: '#f7f3ed' }}>
            {/* Risk Summary Card */}
            <div className="glass-panel" style={{ padding: '1.25rem', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <div>
                  <span style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', color: '#6b5860', letterSpacing: '0.05em' }}>
                    UNIFIED RISK POSTURE
                  </span>
                  <div style={{ fontSize: '2rem', fontWeight: 800, color: isHighRisk ? '#9f1239' : '#b45309', lineHeight: 1 }} className="title-font">
                    {identity.risk_score ? identity.risk_score.toFixed(1) : 0} <span style={{ fontSize: '0.9rem', color: '#6b5860' }}>/ 100</span>
                  </div>
                </div>

                <span style={{
                  padding: '0.3rem 0.75rem',
                  borderRadius: '9999px',
                  fontSize: '0.78rem',
                  fontWeight: 700,
                  background: identity.hr_status === 'DISABLED' ? '#fff1f2' : '#f0fdfa',
                  color: identity.hr_status === 'DISABLED' ? '#9f1239' : '#0f766e',
                  border: identity.hr_status === 'DISABLED' ? '1px solid #fecdd3' : '1px solid #ccfbf1'
                }}>
                  HR STATUS: {identity.hr_status}
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid #e6ded6' }}>
                <div style={{ background: '#faf6f1', padding: '0.6rem 0.75rem', borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.68rem', color: '#6b5860', fontWeight: 700 }}>DAMAGE</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#c2410c' }}>{identity.damage_score || 0}</div>
                </div>
                <div style={{ background: '#faf6f1', padding: '0.6rem 0.75rem', borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.68rem', color: '#6b5860', fontWeight: 700 }}>DORMANCY</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#b45309' }}>{identity.dormancy_score || 0}</div>
                </div>
                <div style={{ background: '#faf6f1', padding: '0.6rem 0.75rem', borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.68rem', color: '#6b5860', fontWeight: 700 }}>DAYS INACTIVE</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#29181d' }}>{identity.days_dormant || 0}d</div>
                </div>
              </div>

              {identity.risk_factors && (
                <div style={{ marginTop: '0.75rem', fontSize: '0.78rem', color: '#6b5860' }}>
                  <strong>Flagged Risk Factors:</strong> {identity.risk_factors}
                </div>
              )}
            </div>

            {/* Linked Platform Accounts */}
            <div style={{ marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
                <Server size={18} color="#9f1239" />
                <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#29181d' }} className="title-font">
                  Linked Platform Accounts ({accounts.length})
                </h3>
              </div>

              {accounts.map((acc, idx) => (
                <div key={idx} className="glass-panel" style={{ padding: '1rem', marginBottom: '0.85rem', background: '#ffffff' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ fontWeight: 800, color: '#9f1239', fontSize: '0.85rem' }}>{acc.platform_name}</span>
                      <span style={{ fontSize: '0.85rem', color: '#29181d', fontWeight: 600 }}>{acc.username}</span>
                    </div>

                    <span style={{
                      padding: '0.15rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      background: acc.account_status === 'DISABLED' ? '#fff1f2' : '#f0fdfa',
                      color: acc.account_status === 'DISABLED' ? '#9f1239' : '#0f766e',
                      border: acc.account_status === 'DISABLED' ? '1px solid #fecdd3' : '1px solid #ccfbf1'
                    }}>
                      {acc.account_status}
                    </span>
                  </div>

                  {/* Attached Roles & Tiers */}
                  <div style={{ marginTop: '0.6rem' }}>
                    <div style={{ fontSize: '0.72rem', color: '#6b5860', fontWeight: 700, marginBottom: '0.3rem' }}>
                      ATTACHED ROLES:
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                      {acc.roles.map((r, rIdx) => (
                        <span key={rIdx} className={`pill-badge ${r.normalized_tier === 'Tier 0' ? 'pill-tier0' : r.normalized_tier === 'Tier 1' ? 'pill-tier1' : 'pill-tier2'}`}>
                          {r.raw_role_name} ({r.normalized_tier})
                        </span>
                      ))}
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '1rem', marginTop: '0.6rem', fontSize: '0.75rem', color: '#9e8a92', paddingTop: '0.5rem', borderTop: '1px solid #f0e8e0' }}>
                    <span>Last Login: {acc.last_login_date || 'N/A'}</span>
                    <span>Token Rotated: {acc.token_rotated_date || 'Never'}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Active Security Incidents */}
            {incidents.length > 0 && (
              <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
                  <AlertTriangle size={18} color="#c2410c" />
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#29181d' }} className="title-font">
                    Active Security Incidents ({incidents.length})
                  </h3>
                </div>

                {incidents.map((inc, idx) => (
                  <div key={idx} style={{
                    background: '#fff1f2',
                    border: '1px solid #fecdd3',
                    borderRadius: '8px',
                    padding: '0.85rem 1rem',
                    marginBottom: '0.6rem'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                      <span style={{ fontWeight: 700, color: '#9f1239', fontSize: '0.85rem' }}>{inc.incident_type}</span>
                      <span className={`pill-badge ${inc.severity?.toUpperCase() === 'CRITICAL' ? 'pill-crit' : 'pill-high'}`}>
                        {inc.severity}
                      </span>
                    </div>
                    <p style={{ fontSize: '0.78rem', color: '#6b5860' }}>{inc.description}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Footer Actions Bar */}
        <div style={{
          padding: '1rem 1.5rem',
          borderTop: '1px solid #e6ded6',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#ffffff'
        }}>
          <button
            onClick={() => onDisableStatus(identityId, identity.full_name)}
            disabled={identity.hr_status === 'DISABLED'}
            className="btn-danger"
            style={{ opacity: identity.hr_status === 'DISABLED' ? 0.5 : 1 }}
          >
            <UserX size={14} />
            <span>Disable HR Status</span>
          </button>

          <button onClick={onClose} className="btn-secondary">
            Close Drawer
          </button>
        </div>
      </div>
    </div>
  );
}
