import React from 'react';
import StatCard from './StatCard';
import { Flame, ShieldAlert, Shield, AlertTriangle, UserX } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';

export default function DamageView({ damageData, onDisableStatus, onSelectIdentity }) {

  const metrics = damageData?.metrics || {
    avg_damage_score: 0,
    tier_0_count: 0,
    tier_1_count: 0,
    high_risk_accounts: 0
  };

  const tierCounts = damageData?.tier_counts || [];
  const registry = damageData?.registry || [];

  const tierColors = {
    'Tier 0': '#9f1239',
    'Tier 1': '#c2410c',
    'Tier 2': '#0f766e'
  };

  return (
    <div>
      {/* Metric Cards Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '1.25rem',
        marginBottom: '2rem'
      }}>
        <StatCard
          label="Avg. Damage Score"
          value={metrics.avg_damage_score}
          subtitle="Blast radius metric"
          icon={Flame}
          accent="red"
        />
        <StatCard
          label="Tier 0 Identities"
          value={metrics.tier_0_count}
          subtitle="Admin tools access"
          icon={ShieldAlert}
          accent="orange"
        />
        <StatCard
          label="Tier 1 Identities"
          value={metrics.tier_1_count}
          subtitle="Internal tools access"
          icon={Shield}
          accent="yellow"
        />
        <StatCard
          label="High-Risk Accounts"
          value={metrics.high_risk_accounts}
          subtitle="Damage score ≥ 60"
          icon={AlertTriangle}
          accent="rose"
        />
      </div>

      {/* Privilege Tier Distribution Bar Chart */}
      <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <div style={{ width: '4px', height: '1.2rem', background: '#9f1239', borderRadius: '2px' }} />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#29181d' }} className="title-font">
            Blast Radius Analysis
          </h3>
          <span style={{ fontSize: '0.78rem', color: '#6b5860', marginLeft: 'auto' }}>
            Score based on access tier privilege: Tier 0 (100 pts), Tier 1 (50 pts), Tier 2 (10 pts)
          </span>
        </div>

        <div style={{ width: '100%', height: 260 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={tierCounts} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e6ded6" />
              <XAxis dataKey="tier" stroke="#6b5860" tick={{ fontSize: 12 }} />
              <YAxis stroke="#6b5860" tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#fecdd3',
                  borderRadius: '8px',
                  color: '#29181d',
                  boxShadow: '0 4px 12px rgba(41, 24, 29, 0.1)'
                }}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {tierCounts.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={tierColors[entry.tier] || '#0f766e'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Blast Radius Registry Table */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
          <div style={{ width: '4px', height: '1.2rem', background: '#c2410c', borderRadius: '2px' }} />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#29181d' }} className="title-font">
            Blast Radius Registry
          </h3>
          <span style={{ fontSize: '0.78rem', color: '#6b5860', marginLeft: 'auto' }}>
            Monitored identities ranked by privilege damage score
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
                <th>Damage Score</th>
                <th style={{ textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {registry.map((item) => (
                <tr key={item.identity_id}>
                  <td style={{ color: '#6b5860', fontSize: '0.8rem' }}>
                    #{item.identity_id}
                  </td>
                  <td
                    onClick={() => onSelectIdentity && onSelectIdentity(item.identity_id)}
                    style={{ fontWeight: 600, color: '#9f1239', cursor: 'pointer' }}
                  >
                    {item.identity_name}
                  </td>

                  <td>
                    <span style={{
                      padding: '0.2rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.74rem',
                      fontWeight: 700,
                      background: item.hr_status === 'DISABLED' ? '#fff1f2' : '#f0fdfa',
                      color: item.hr_status === 'DISABLED' ? '#9f1239' : '#0f766e',
                      border: item.hr_status === 'DISABLED' ? '1px solid #fecdd3' : '1px solid #ccfbf1'
                    }}>
                      {item.hr_status}
                    </span>
                  </td>
                  <td>
                    <span className={`pill-badge ${item.highest_tier_held === 'Tier 0' ? 'pill-tier0' : item.highest_tier_held === 'Tier 1' ? 'pill-tier1' : 'pill-tier2'}`}>
                      {item.highest_tier_held || 'Tier 2'}
                    </span>
                  </td>
                  <td style={{ color: '#6b5860' }}>
                    {item.days_dormant} days
                  </td>
                  <td style={{ fontWeight: 800, fontSize: '0.95rem', color: item.damage_score >= 50 ? '#9f1239' : '#0f766e' }}>
                    {item.damage_score}
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
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
