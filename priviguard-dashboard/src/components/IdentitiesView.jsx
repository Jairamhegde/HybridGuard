import React from 'react';
import { Search, UserX } from 'lucide-react';

export default function IdentitiesView({ identitiesData, searchIdentities, setSearchIdentities, onDisableStatus }) {
  const identities = identitiesData?.identities || [];

  return (
    <div>
      {/* Search Header Bar */}
      <div className="glass-panel" style={{ padding: '1.25rem 1.5rem', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyBetween: 'space-between', gap: '1rem' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={16} color="#94a3b8" style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              placeholder="Search identities by name or ID..."
              value={searchIdentities}
              onChange={(e) => setSearchIdentities(e.target.value)}
              style={{
                width: '100%',
                background: '#ffffff',
                color: '#0f172a',
                border: '1px solid #cbd5e1',
                borderRadius: '8px',
                padding: '0.55rem 0.85rem 0.55rem 2.4rem',
                fontSize: '0.875rem',
                outline: 'none'
              }}
            />
          </div>

          <div style={{ fontSize: '0.82rem', color: '#475569', fontWeight: 600 }}>
            Total Monitored: <span style={{ color: '#0284c7', fontWeight: 800 }}>{identities.length}</span>
          </div>
        </div>
      </div>

      {/* Identities Directory Table */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
          <div style={{ width: '4px', height: '1.2rem', background: '#7c3aed', borderRadius: '2px' }} />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a' }} className="title-font">
            All Monitored Identities Directory
          </h3>
          <span style={{ fontSize: '0.78rem', color: '#64748b', marginLeft: 'auto' }}>
            Unified view across HR, Active Directory, AWS IAM & Okta
          </span>
        </div>

        <div className="custom-table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Identity ID</th>
                <th>Identity Name</th>
                <th>HR Status</th>
                <th>Highest Tier</th>
                <th>Days Dormant</th>
                <th>Risk Score</th>
                <th>Damage Score</th>
                <th>Dormancy Score</th>
                <th>Flagged Risk Factors</th>
                <th style={{ textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {identities.map((item) => {
                const isHighRisk = item.risk_score >= 60;
                return (
                  <tr key={item.identity_id}>
                    <td style={{ color: '#64748b', fontSize: '0.8rem' }}>
                      #{item.identity_id}
                    </td>
                    <td style={{ fontWeight: 600, color: '#0f172a' }}>
                      {item.identity_name}
                    </td>
                    <td>
                      <span style={{
                        padding: '0.2rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.74rem',
                        fontWeight: 700,
                        background: item.hr_status === 'DISABLED' ? '#fef2f2' : '#f0fdf4',
                        color: item.hr_status === 'DISABLED' ? '#dc2626' : '#16a34a',
                        border: item.hr_status === 'DISABLED' ? '1px solid #fca5a5' : '1px solid #bbf7d0'
                      }}>
                        {item.hr_status}
                      </span>
                    </td>
                    <td>
                      <span className={`pill-badge ${item.highest_tier_held === 'Tier 0' ? 'pill-tier0' : item.highest_tier_held === 'Tier 1' ? 'pill-tier1' : 'pill-tier2'}`}>
                        {item.highest_tier_held || 'Tier 2'}
                      </span>
                    </td>
                    <td style={{ color: '#475569' }}>
                      {item.days_dormant} days
                    </td>
                    <td>
                      <span style={{
                        fontWeight: 800,
                        fontSize: '0.92rem',
                        color: isHighRisk ? '#dc2626' : '#0284c7'
                      }}>
                        {item.risk_score ? item.risk_score.toFixed(1) : 0}
                      </span>
                    </td>
                    <td style={{ color: item.damage_score >= 50 ? '#ea580c' : '#475569', fontWeight: 600 }}>
                      {item.damage_score}
                    </td>
                    <td style={{ color: item.dormancy_score >= 50 ? '#ca8a04' : '#475569', fontWeight: 600 }}>
                      {item.dormancy_score}
                    </td>
                    <td style={{ fontSize: '0.78rem', color: '#475569' }}>
                      {item.risk_factors || '—'}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        onClick={() => onDisableStatus(item.identity_id, item.identity_name)}
                        disabled={item.hr_status === 'DISABLED'}
                        className="btn-danger"
                        style={{ opacity: item.hr_status === 'DISABLED' ? 0.4 : 1 }}
                      >
                        <UserX size={13} />
                        <span>Disable Status</span>
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
