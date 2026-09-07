import React from 'react';
import StatCard from './StatCard';
import { Users, Clock, AlertTriangle, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function DormancyView({ dormancyData }) {
  const metrics = dormancyData?.metrics || {
    total_monitored: 0,
    max_days_dormant: 0,
    dormant_60_plus: 0,
    avg_dormancy_score: 0
  };

  const distribution = dormancyData?.distribution || [];
  const heatmap = dormancyData?.heatmap || [];
  const ledger = dormancyData?.ledger || [];

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
          label="Identities Monitored"
          value={metrics.total_monitored}
          subtitle="AD, AWS & Okta"
          icon={Users}
          accent="cyan"
        />
        <StatCard
          label="Max Days Dormant"
          value={`${metrics.max_days_dormant}d`}
          subtitle="Stalest account"
          icon={Clock}
          accent="red"
        />
        <StatCard
          label="Dormant Identities"
          value={metrics.dormant_60_plus}
          subtitle="Inactive 60+ days"
          icon={AlertTriangle}
          accent="orange"
        />
        <StatCard
          label="Avg. Dormancy Score"
          value={metrics.avg_dormancy_score}
          subtitle="Higher = Staler access"
          icon={Activity}
          accent="yellow"
        />
      </div>

      {/* Dormancy Distribution Chart */}
      <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <div style={{ width: '4px', height: '1.2rem', background: '#38bdf8', borderRadius: '2px' }} />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc' }} className="title-font">
            Dormancy Distribution
          </h3>
          <span style={{ fontSize: '0.78rem', color: '#64748b', marginLeft: 'auto' }}>
            Overview of identity inactivity duration across all platforms
          </span>
        </div>

        <div style={{ width: '100%', height: 280 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={distribution} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="range" stroke="#64748b" tick={{ fontSize: 12 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: 'rgba(56, 189, 248, 0.4)',
                  borderRadius: '8px',
                  color: '#f8fafc'
                }}
              />
              <Bar dataKey="count" fill="#38bdf8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Heatmap Grid Matrix */}
      <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
          <div style={{ width: '4px', height: '1.2rem', background: '#eab308', borderRadius: '2px' }} />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc' }} className="title-font">
            Dormancy Heatmap Matrix
          </h3>
          <span style={{ fontSize: '0.78rem', color: '#64748b', marginLeft: 'auto' }}>
            Average days inactive mapped by Privilege Tier and HR Status
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          {heatmap.map((cell, idx) => {
            const isHighDormant = cell.avg_days >= 60;
            return (
              <div
                key={idx}
                style={{
                  background: isHighDormant ? 'rgba(239, 68, 68, 0.12)' : 'rgba(30, 41, 59, 0.5)',
                  border: isHighDormant ? '1px solid rgba(239, 68, 68, 0.3)' : '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: '10px',
                  padding: '1rem',
                  textAlign: 'center'
                }}
              >
                <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
                  {cell.tier} · {cell.status}
                </div>
                <div style={{
                  fontSize: '1.6rem',
                  fontWeight: 800,
                  color: isHighDormant ? '#ef4444' : '#38bdf8',
                  marginTop: '0.3rem'
                }}>
                  {cell.avg_days}d
                </div>
                <div style={{ fontSize: '0.72rem', color: '#64748b', marginTop: '0.2rem' }}>
                  Avg Inactivity
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Identity Dormancy Ledger Table */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
          <div style={{ width: '4px', height: '1.2rem', background: '#10b981', borderRadius: '2px' }} />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc' }} className="title-font">
            Identity Dormancy Ledger
          </h3>
          <span style={{ fontSize: '0.78rem', color: '#64748b', marginLeft: 'auto' }}>
            All monitored identities ranked by inactivity duration
          </span>
        </div>

        <div className="custom-table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Identity Name</th>
                <th>HR Status</th>
                <th>Days Dormant</th>
                <th>Highest Privilege</th>
                <th>Dormancy Score</th>
              </tr>
            </thead>
            <tbody>
              {ledger.map((item) => (
                <tr key={item.identity_id}>
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
                  <td style={{ fontWeight: 700, color: item.days_dormant >= 60 ? '#ef4444' : '#f8fafc' }}>
                    {item.days_dormant} days
                  </td>
                  <td>
                    <span className={`pill-badge ${item.highiest_privilage === 'Tier 0' ? 'pill-tier0' : item.highiest_privilage === 'Tier 1' ? 'pill-tier1' : 'pill-tier2'}`}>
                      {item.highiest_privilage || 'Tier 2'}
                    </span>
                  </td>
                  <td style={{ fontWeight: 700, color: item.dormancy_score >= 50 ? '#eab308' : '#94a3b8' }}>
                    {item.dormancy_score}
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
