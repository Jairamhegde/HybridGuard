import React from 'react';
import StatCard from './StatCard';
import { Flame, ShieldAlert, Shield, AlertTriangle, UserX } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';

export default function DamageView({ damageData, onDisableStatus }) {
  const metrics = damageData?.metrics || {
    avg_damage_score: 0,
    tier_0_count: 0,
    tier_1_count: 0,
    high_risk_accounts: 0
  };

  const tierCounts = damageData?.tier_counts || [];
  const registry = damageData?.registry || [];

  const tierColors = {
    'Tier 0': '#ef4444',
    'Tier 1': '#f97316',
    'Tier 2': '#38bdf8'
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
          accent="cyan"
        />
      </div>

      {/* Privilege Tier Distribution Bar Chart */}
      <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <div style={{ width: '4px', height: '1.2rem', background: '#ef4444', borderRadius: '2px' }} />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc' }} className="title-font">
            Blast Radius Analysis
          </h3>
          <span style={{ fontSize: '0.78rem', color: '#64748b', marginLeft: 'auto' }}>
            Score based on access tier privilege: Tier 0 (100 pts), Tier 1 (50 pts), Tier 2 (10 pts)
          </span>
        </div>

        <div style={{ width: '100%', height: 260 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={tierCounts} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="tier" stroke="#64748b" tick={{ fontSize: 12 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: 'rgba(239, 68, 68, 0.4)',
                  borderRadius: '8px',
                  color: '#f8fafc'
                }}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {tierCounts.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={tierColors[entry.tier] || '#38bdf8'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Blast Radius Registry Table */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
          <div style={{ width: '4px', height: '1.2rem', background: '#f97316', borderRadius: '2px' }} />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc' }} className="title-font">
            Blast Radius Registry
          </h3>
          <span style={{ fontSize: '0.78rem', color: '#64748b', marginLeft: 'auto' }}>
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
                  <td style={{ color: '#64748b', fontSize: '0.8rem' }}>
                    #{item.identity_id}
                  </td>
                  <td style={{ fontWeight: 600, color: '#f8fafc' }}>
                    {item.identity_name}
                  </td>
                  <td>
                    <span style={{
                      padding: '0.2rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.74rem',
                      fontWeight: 700,
                      background: item.hr_status === 'DISABLED' ? 'rgba(239,68,68,0.2)' : 'rgba(16,185,129,0.2)',
                      color: item.hr_status === 'DISABLED' ? '#fca5a5' : '#6ee7b7'
                    }}>
                      {item.hr_status}
                    </span>
                  </td>
                  <td>
                    <span className={`pill-badge ${item.highest_tier_held === 'Tier 0' ? 'pill-tier0' : item.highest_tier_held === 'Tier 1' ? 'pill-tier1' : 'pill-tier2'}`}>
                      {item.highest_tier_held || 'Tier 2'}
                    </span>
                  </td>
                  <td style={{ color: '#94a3b8' }}>
                    {item.days_dormant} days
                  </td>
                  <td style={{ fontWeight: 800, fontSize: '0.95rem', color: item.damage_score >= 50 ? '#ef4444' : '#38bdf8' }}>
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
