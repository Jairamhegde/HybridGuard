import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import OverviewView from './components/OverviewView';
import DormancyView from './components/DormancyView';
import DamageView from './components/DamageView';
import RemediationView from './components/RemediationView';
import IdentitiesView from './components/IdentitiesView';
import { CheckCircle, AlertCircle } from 'lucide-react';

const API_BASE_URL = 'http://127.0.0.1:8000';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  // View States
  const [overviewData, setOverviewData] = useState(null);
  const [dormancyData, setDormancyData] = useState(null);
  const [damageData, setDamageData] = useState(null);
  const [remediationData, setRemediationData] = useState(null);
  const [identitiesData, setIdentitiesData] = useState(null);

  // Filters
  const [selectedSeverity, setSelectedSeverity] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchIdentities, setSearchIdentities] = useState('');

  const triggerToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 4000);
  };

  const fetchOverview = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/overview`);
      const data = await res.json();
      setOverviewData(data);
    } catch (err) {
      console.error("Error fetching overview data", err);
    }
  };

  const fetchDormancy = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/dormancy`);
      const data = await res.json();
      setDormancyData(data);
    } catch (err) {
      console.error("Error fetching dormancy data", err);
    }
  };

  const fetchDamage = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/damage`);
      const data = await res.json();
      setDamageData(data);
    } catch (err) {
      console.error("Error fetching damage data", err);
    }
  };

  const fetchRemediation = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/remediation?severity=${selectedSeverity}&search=${searchQuery}`);
      const data = await res.json();
      setRemediationData(data);
    } catch (err) {
      console.error("Error fetching remediation data", err);
    }
  };

  const fetchIdentities = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/identities?search=${searchIdentities}`);
      const data = await res.json();
      setIdentitiesData(data);
    } catch (err) {
      console.error("Error fetching identities data", err);
    }
  };

  const fetchAllData = async () => {
    setIsRefreshing(true);
    await Promise.all([
      fetchOverview(),
      fetchDormancy(),
      fetchDamage(),
      fetchRemediation(),
      fetchIdentities()
    ]);
    setIsRefreshing(false);
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  useEffect(() => {
    fetchRemediation();
  }, [selectedSeverity, searchQuery]);

  useEffect(() => {
    fetchIdentities();
  }, [searchIdentities]);

  // Action Handlers
  const handleDisableStatus = async (identityId, identityName) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/remediation/disable-status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identity_id: identityId })
      });
      const data = await res.json();
      if (res.ok) {
        triggerToast(`Status disabled for identity: ${identityName || '#' + identityId}`);
        fetchAllData();
      } else {
        triggerToast(`Action failed: ${data.detail}`);
      }
    } catch (err) {
      console.error("Failed to disable status", err);
      triggerToast("Error triggering disable status action.");
    }
  };

  const handleRemediateIncident = async (incident) => {
    const sev = incident.severity?.toUpperCase();
    const identityId = incident.identity_id;
    const platform = incident.platform;

    try {
      if (sev === 'CRITICAL') {
        // Revoke Access / Disable Account
        const res = await fetch(`${API_BASE_URL}/api/remediation/revoke-access`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ identity_id: identityId, platform: platform, incident_type: incident.rule_type })
        });
        if (res.ok) {
          triggerToast(`Account disabled for identity ID: ${identityId} on ${platform}`);
        }
      } else if (sev === 'HIGH') {
        // Revoke Tier Access
        const res = await fetch(`${API_BASE_URL}/api/remediation/revoke-tier`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ identity_id: identityId, platform: platform, elevated_tier: incident.elevated_tier || 'Tier 0' })
        });
        if (res.ok) {
          triggerToast(`Elevated tier access revoked for identity ID: ${identityId} on ${platform}`);
        }
      } else if (sev === 'MEDIUM') {
        // Rotate Token
        const res = await fetch(`${API_BASE_URL}/api/remediation/rotate-token`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ identity_id: identityId, platform: platform })
        });
        if (res.ok) {
          triggerToast(`Security token rotated for identity ID: ${identityId} on ${platform}`);
        }
      }
      fetchAllData();
    } catch (err) {
      console.error("Failed remediation action", err);
      triggerToast("Error executing remediation action.");
    }
  };

  const handleRefreshCache = async () => {
    setIsRefreshing(true);
    try {
      await fetch(`${API_BASE_URL}/api/refresh-cache`, { method: 'POST' });
      triggerToast("Data cache refreshed successfully.");
      await fetchAllData();
    } catch (err) {
      console.error("Failed to refresh cache", err);
    } finally {
      setIsRefreshing(false);
    }
  };

  const pageHeadings = {
    overview: { title: 'Overall Threat Posture', subtitle: 'Cross-platform privilege, dormancy & damage metrics summary' },
    dormancy: { title: 'Dormancy Analysis', subtitle: 'Identity inactivity duration and platform heatmap distribution' },
    damage: { title: 'Damage Score & Blast Radius', subtitle: 'Access tier privilege rating and account blast radius analysis' },
    remediation: { title: 'Remediation Backlog', subtitle: 'Active policy violations and one-click remediation actions' },
    identities: { title: 'Monitored Identities Directory', subtitle: 'Unified identity list with full risk score breakdown' },
  };

  const currentHead = pageHeadings[activeTab] || pageHeadings.overview;

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onRefresh={handleRefreshCache}
        isRefreshing={isRefreshing}
      />

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: '2rem 2.5rem', maxWidth: '1400px' }}>
        <Header
          pageTitle={currentHead.title}
          pageSubtitle={currentHead.subtitle}
        />

        {activeTab === 'overview' && (
          <OverviewView
            overviewData={overviewData}
            onDisableStatus={handleDisableStatus}
            API_BASE_URL={API_BASE_URL}
            triggerToast={triggerToast}
          />
        )}

        {activeTab === 'dormancy' && (
          <DormancyView dormancyData={dormancyData} />
        )}

        {activeTab === 'damage' && (
          <DamageView
            damageData={damageData}
            onDisableStatus={handleDisableStatus}
          />
        )}

        {activeTab === 'remediation' && (
          <RemediationView
            remediationData={remediationData}
            selectedSeverity={selectedSeverity}
            setSelectedSeverity={setSelectedSeverity}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            onRemediate={handleRemediateIncident}
          />
        )}

        {activeTab === 'identities' && (
          <IdentitiesView
            identitiesData={identitiesData}
            searchIdentities={searchIdentities}
            setSearchIdentities={setSearchIdentities}
            onDisableStatus={handleDisableStatus}
          />
        )}
      </main>

      {/* Toast Notification Banner */}
      {toastMessage && (
        <div className="toast-banner">
          <CheckCircle size={18} color="#38bdf8" />
          <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{toastMessage}</span>
        </div>
      )}
    </div>
  );
}
