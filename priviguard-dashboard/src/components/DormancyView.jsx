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
          <div style={{ width: '4px', height: '1.2rem', background: '#0284c7', borderRadius: '2px' }} />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a' }} className="title-font">
            Dormancy Distribution
          </h3>
          <span style={{ fontSize: '0.78rem', color: '#64748b', marginLeft: 'auto' }}>
            Overview of identity inactivity duration across all platforms
          </span>
        </div>

        <div style={{ width: '100%', height: 280 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={distribution} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="range" stroke="#64748b" tick={{ fontSize: 12 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#bae6fd',
                  borderRadius: '8px',
                  color: '#0f172a',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                }}
              />
              <Bar dataKey="count" fill="#0284c7" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Heatmap Grid Matrix */}
      <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
          <div style={{ width: '4px', height: '1.2rem', background: '#ca8a04', borderRadius: '2px' }} />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a' }} className="title-font">
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
                  background: isHighDormant ? '#fef2f2' : '#f8fafc',
                  border: isHighDormant ? '1px solid #fca5a5' : '1px solid #e2e8f0',
                  borderRadius: '10px',
                  padding: '1rem',
                  textAlign: 'center'
                }}
              >
                <div style={{ fontSize: '0.75rem', color: '#475569', textTransform: 'uppercase', fontWeight: 700 }}>
                  {cell.tier} · {cell.status}
                </div>
                <div style={{
                  fontSize: '1.6rem',
                  fontWeight: 800,
                  color: isHighDormant ? '#dc2626' : '#0284c7',
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
          <div style={{ width: '4px', height: '1.2rem', background: '#16a34a', borderRadius: '2px' }} />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a' }} className="title-font">
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
                  <td style={{ fontWeight: 700, color: item.days_dormant >= 60 ? '#dc2626' : '#0f172a' }}>
                    {item.days_dormant} days
                  </td>
                  <td>
                    <span className={`pill-badge ${item.highiest_privilage === 'Tier 0' ? 'pill-tier0' : item.highiest_privilage === 'Tier 1' ? 'pill-tier1' : 'pill-tier2'}`}>
                      {item.highiest_privilage || 'Tier 2'}
                    </span>
                  </td>
                  <td style={{ fontWeight: 700, color: item.dormancy_score >= 50 ? '#ca8a04' : '#475569' }}>
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
