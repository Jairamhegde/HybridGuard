import React, { useState } from 'react';
import StatCard from './StatCard';
import ExecutiveReportModal from './ExecutiveReportModal';
import { ShieldAlert, Flame, Clock, Users, FileText, UserX } from 'lucide-react';

export default function OverviewView({ overviewData, onDisableStatus, API_BASE_URL, triggerToast }) {
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportText, setReportText] = useState('');
  const [loadingReport, setLoadingReport] = useState(false);

  const metrics = overviewData?.metrics || {
    total_incidents: 0,
    high_risk_accounts: 0,
    dormant_identities: 0,
    total_identities: 0,
  };

  const topIdentities = overviewData?.top_risk_identities || [];

  const handleGenerateReport = async () => {
    setLoadingReport(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/report`);
      const data = await res.json();
      setReportText(data.report);
      setShowReportModal(true);
    } catch (err) {
      console.error("Failed to generate report", err);
      triggerToast("Failed to fetch executive risk report.");
    } finally {
      setLoadingReport(false);
    }
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
          label="Total Open Incidents"
          value={metrics.total_incidents}
          subtitle="Active policy violations"
          icon={ShieldAlert}
          accent="red"
        />
        <StatCard
          label="High Risk Accounts"
          value={metrics.high_risk_accounts}
          subtitle="Action required < 24h"
          icon={Flame}
          accent="orange"
        />
        <StatCard
          label="Dormant Identities"
          value={metrics.dormant_identities}
          subtitle="Inactive for 60+ days"
          icon={Clock}
          accent="yellow"
        />
        <StatCard
          label="Identities Monitored"
          value={metrics.total_identities}
          subtitle="Active in Directory"
          icon={Users}
          accent="green"
        />
      </div>

      {/* Executive Report Generator Banner */}
      <div className="glass-panel" style={{
        padding: '1.25rem 1.5rem',
        marginBottom: '2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%)',
        border: '1px solid #bae6fd'
      }}>
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.25rem' }} className="title-font">
            Executive Security Posture Report
          </h3>
          <p style={{ fontSize: '0.82rem', color: '#475569' }}>
            Generate a full audit summary containing blast radius metrics, dormancy highlights, and critical risk findings.
          </p>
        </div>
        <button
          onClick={handleGenerateReport}
          disabled={loadingReport}
          className="btn-primary"
        >
          <FileText size={16} />
          <span>{loadingReport ? 'Generating...' : 'Generate Risk Report'}</span>
        </button>
      </div>

      {/* Top 10 Risk Identities Table */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
          <div style={{ width: '4px', height: '1.2rem', background: '#0284c7', borderRadius: '2px' }} />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a' }} className="title-font">
            Top 10 High Risk Identities
          </h3>
          <span style={{ fontSize: '0.78rem', color: '#64748b', marginLeft: 'auto' }}>
            Ranked by Unified Risk Score (Privilege × Inactivity × HR Status)
          </span>
        </div>

        <div className="custom-table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Identity</th>
                <th>HR Status</th>
                <th>Risk Score</th>
                <th>Damage</th>
                <th>Dormancy</th>
                <th>Flagged Factors</th>
                <th style={{ textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {topIdentities.map((item) => {
                const isHighRisk = item.risk_score >= 60;
                return (
                  <tr key={item.identity_id}>
                    <td style={{ fontWeight: 600, color: '#0f172a' }}>
                      {item.identity_name}
                      <span style={{ display: 'block', fontSize: '0.72rem', color: '#64748b', fontWeight: 400 }}>
                        ID: #{item.identity_id}
                      </span>
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
                      <span style={{
                        fontWeight: 800,
                        fontSize: '0.95rem',
                        color: isHighRisk ? '#dc2626' : '#ca8a04'
                      }}>
                        {item.risk_score ? item.risk_score.toFixed(1) : 0}
                      </span>
                    </td>
                    <td>
                      <span style={{ color: item.damage_score >= 50 ? '#ea580c' : '#475569', fontWeight: 600 }}>
                        {item.damage_score}
                      </span>
                    </td>
                    <td>
                      <span style={{ color: item.dormancy_score >= 50 ? '#ca8a04' : '#475569', fontWeight: 600 }}>
                        {item.dormancy_score}
                      </span>
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

      {showReportModal && (
        <ExecutiveReportModal
          reportText={reportText}
          onClose={() => setShowReportModal(false)}
        />
      )}
    </div>
  );
}
