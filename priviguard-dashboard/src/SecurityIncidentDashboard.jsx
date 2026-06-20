import React, { useState, useMemo, useEffect } from "react";
import {
  ShieldAlert, Ghost, TrendingUp, KeyRound, ChevronDown,
  Search, CircleDot, CheckCircle2, X, Terminal, Copy, Check, Info, ShieldAlert as AlertIcon
} from "lucide-react";

const FONT_IMPORT_URL =
  "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap";

const SEVERITY_META = {
  Critical: { color: "#E2504A", bg: "rgba(226,80,74,0.12)", label: "Critical" },
  High: { color: "#F0A93D", bg: "rgba(240,169,61,0.12)", label: "High" },
  Medium: { color: "#4FA3D1", bg: "rgba(79,163,209,0.12)", label: "Medium" },
};

const TYPE_META = {
  "Ghost Account": { icon: Ghost, color: "#E2504A" },
  "Privilege Creep": { icon: TrendingUp, color: "#F0A93D" },
  "Stale Token": { icon: KeyRound, color: "#4FA3D1" },
};

export default function SecurityIncidentDashboard() {
  const [incidents, setIncidents] = useState([]);
  const [statuses, setStatuses] = useState({});
  const [severityFilter, setSeverityFilter] = useState(null);
  const [typeFilter, setTypeFilter] = useState(null);
  const [query, setQuery] = useState("");
  const [selectedIncidentId, setSelectedIncidentId] = useState(null);
  const [viewMode, setViewMode] = useState("all"); // "all" or "offboarding"
  const [copiedCommand, setCopiedCommand] = useState(null);

  // Fetch incidents on mount
  useEffect(() => {
    fetch("http://localhost:8000/")
      .then((res) => res.json())
      .then((data) => {
        const mapped = data.map((row) => ({
          ...row,
          status: "OPEN",
        }));
        setIncidents(mapped);
        setStatuses(Object.fromEntries(mapped.map((inc) => [inc.id, "OPEN"])));
      })
      .catch((err) => console.error("Failed to fetch incidents:", err));
  }, []);

  // Compute metrics counts
  const metrics = useMemo(() => {
    const out = { total: 0, critical: 0, high: 0, medium: 0, resolved: 0 };
    incidents.forEach((inc) => {
      out.total += 1;
      const sev = inc.severity;
      if (sev === "Critical" || sev === "CRITICAL") out.critical += 1;
      if (sev === "High" || sev === "HIGH") out.high += 1;
      if (sev === "Medium" || sev === "MEDIUM") out.medium += 1;
      
      const status = statuses[inc.id];
      if (status === "REMEDIATED" || status === "ACKNOWLEDGED") out.resolved += 1;
    });
    return out;
  }, [incidents, statuses]);

  // Compute counts for the severity filter chips based on current viewMode
  const counts = useMemo(() => {
    const out = { Critical: 0, High: 0, Medium: 0, Open: 0 };
    incidents.forEach((inc) => {
      // If we are in offboarding gaps mode, only count Ghost Accounts
      if (viewMode === "offboarding" && inc.incident_type !== "Ghost Account") return;

      const sev = inc.severity;
      if (sev === "Critical" || sev === "CRITICAL") out.Critical += 1;
      if (sev === "High" || sev === "HIGH") out.High += 1;
      if (sev === "Medium" || sev === "MEDIUM") out.Medium += 1;
      if (statuses[inc.id] === "OPEN") out.Open += 1;
    });
    return out;
  }, [incidents, statuses, viewMode]);

  // Compute incident type counts
  const typeCounts = useMemo(() => {
    const out = {};
    incidents.forEach((inc) => {
      if (viewMode === "offboarding" && inc.incident_type !== "Ghost Account") return;
      out[inc.incident_type] = (out[inc.incident_type] || 0) + 1;
    });
    return out;
  }, [incidents, viewMode]);

  // Apply filters and searches
  const filteredIncidents = useMemo(() => {
    return incidents
      .filter((inc) => {
        if (viewMode === "offboarding") {
          return inc.incident_type === "Ghost Account";
        }
        return true;
      })
      .filter((inc) => (severityFilter ? inc.severity === severityFilter : true))
      .filter((inc) => (typeFilter ? inc.incident_type === typeFilter : true))
      .filter((inc) => {
        if (!query) return true;
        const q = query.toLowerCase();
        return (
          inc.full_name.toLowerCase().includes(q) ||
          inc.user_id.toLowerCase().includes(q) ||
          inc.incident_type.toLowerCase().includes(q) ||
          inc.platform.toLowerCase().includes(q) ||
          inc.description.toLowerCase().includes(q)
        );
      })
      .sort((a, b) => {
        const order = { Critical: 0, CRITICAL: 0, High: 1, HIGH: 1, Medium: 2, MEDIUM: 2 };
        return (order[a.severity] ?? 9) - (order[b.severity] ?? 9) || b.id - a.id;
      });
  }, [incidents, severityFilter, typeFilter, query, viewMode]);

  const selectedIncident = useMemo(() => {
    return incidents.find((inc) => inc.id === selectedIncidentId) || null;
  }, [incidents, selectedIncidentId]);

  const cycleStatus = (id) => {
    setStatuses((prev) => {
      const next = { ...prev };
      const order = ["OPEN", "ACKNOWLEDGED", "REMEDIATED"];
      const cur = order.indexOf(prev[id]);
      next[id] = order[(cur + 1) % order.length];
      return next;
    });
  };

  const handleCopy = (text, key) => {
    navigator.clipboard.writeText(text);
    setCopiedCommand(key);
    setTimeout(() => setCopiedCommand(null), 2000);
  };

  // Generate dynamic remediation script
  const getRemediationCommands = (inc) => {
    if (!inc) return [];
    
    // Normalize names to generate realistic user commands
    const parts = inc.full_name.toLowerCase().split(" ");
    const awsUser = parts.join(".");
    const oktaId = `00u${inc.user_id.replace("EMP", "")}`;

    const commands = [];

    if (inc.incident_type === "Ghost Account") {
      if (inc.platform.includes("AWS")) {
        commands.push({
          label: "Disable AWS User Login Profile",
          cmd: `aws iam delete-login-profile --user-name ${awsUser}`
        });
        commands.push({
          label: "Remove AWS User access keys",
          cmd: `aws iam list-access-keys --user-name ${awsUser} \\\n  | jq -r '.AccessKeyMetadata[].AccessKeyId' \\\n  | xargs -I {} aws iam delete-access-key --user-name ${awsUser} --access-key-id {}`
        });
      }
      if (inc.platform.includes("Okta")) {
        commands.push({
          label: "Suspend Okta User account",
          cmd: `curl -X POST "https://company.okta.com/api/v1/users/${oktaId}/lifecycle/suspend" \\\n  -H "Authorization: SSWS \${OKTA_API_TOKEN}"`
        });
      }
    } else if (inc.incident_type === "Privilege Creep") {
      if (inc.platform.includes("AWS")) {
        commands.push({
          label: "Detach AWS Administrator Policy",
          cmd: `aws iam detach-user-policy --user-name ${awsUser} --policy-arn arn:aws:iam::aws:policy/AdministratorAccess`
        });
      }
      if (inc.platform.includes("Okta")) {
        commands.push({
          label: "Revoke Okta Admin App Access",
          cmd: `curl -X DELETE "https://company.okta.com/api/v1/users/${oktaId}/roles" \\\n  -H "Authorization: SSWS \${OKTA_API_TOKEN}"`
        });
      }
    } else if (inc.incident_type === "Stale Token") {
      if (inc.platform.includes("AWS")) {
        commands.push({
          label: "Deactivate & Delete AWS Access Key",
          cmd: `aws iam update-access-key --status Inactive --user-name ${awsUser} --access-key-id AKIAEXAMPLEKEYID\naws iam delete-access-key --user-name ${awsUser} --access-key-id AKIAEXAMPLEKEYID`
        });
      }
      if (inc.platform.includes("Okta")) {
        commands.push({
          label: "Rotate Okta API Security Token",
          cmd: `curl -X POST "https://company.okta.com/api/v1/users/${oktaId}/credentials/keys/rotate" \\\n  -H "Authorization: SSWS \${OKTA_API_TOKEN}"`
        });
      }
    }

    return commands;
  };

  // Generate dynamic blast radius assessment
  const getBlastRadiusAssessment = (inc) => {
    if (!inc) return null;

    const sections = [];
    if (inc.platform.includes("AWS")) {
      sections.push({
        title: "AWS Blast Radius",
        items: inc.incident_type === "Privilege Creep"
          ? [
              "Access to all IAM management and policy alterations (Tier 0).",
              "Ability to read/write/delete files across all AWS S3 buckets.",
              "Ability to launch, terminate, and modify EC2 compute resources company-wide."
            ]
          : [
              "Access to user-specific cloud resources and files.",
              "Potential lateral movement if cloud role permits escalation.",
              "Risk of AWS compute credential abuse (crypto mining, data exfiltration)."
            ]
      });
    }

    if (inc.platform.includes("Okta")) {
      sections.push({
        title: "Okta Blast Radius",
        items: inc.incident_type === "Privilege Creep"
          ? [
              "Global administrative capabilities to modify directory services.",
              "Assigned corporate apps access, including Slack, Google Workspace, and SSO pathways.",
              "Ability to reset credentials or suspend active employee accounts."
            ]
          : [
              "Potential access to active user applications.",
              "Dormant session hijacking leading to enterprise system compromise.",
              "Authentication bypass targeting enterprise application data."
            ]
      });
    }

    return sections;
  };

  return (
    <div
      style={{
        fontFamily: "'Inter', sans-serif",
        background: "#0D1117",
        color: "#C9D1D9",
        minHeight: "100vh",
        padding: "24px",
        boxSizing: "border-box"
      }}
    >
      <style>{`
        @import url('${FONT_IMPORT_URL}');
        .pg-mono { font-family: 'JetBrains Mono', monospace; }
        .pg-display { font-family: 'Space Grotesk', sans-serif; }
        
        .pg-row { 
          transition: background 0.2s ease, border-color 0.2s ease, transform 0.1s ease; 
        }
        .pg-row:hover { 
          background: #1F242C !important;
          border-color: #30363D !important;
        }
        .pg-row-selected {
          background: #1F242C !important;
          border-color: #58A6FF !important;
        }
        
        .pg-chip { 
          transition: background 0.2s ease, border-color 0.2s ease, opacity 0.15s ease; 
          cursor: pointer; 
        }
        .pg-chip:hover { 
          opacity: 0.9;
        }

        .pg-sidebar {
          background: #161B22;
          border: 1px solid #30363D;
          border-radius: 12px;
          height: calc(100vh - 48px);
          position: sticky;
          top: 24px;
          overflow-y: auto;
          transition: all 0.3s ease;
        }

        .pg-metric-card {
          background: #161B22;
          border: 1px solid #21262D;
          border-radius: 12px;
          padding: 16px;
          flex: 1;
          min-width: 140px;
          transition: border-color 0.2s ease;
        }
        .pg-metric-card:hover {
          border-color: #30363D;
        }

        .pg-nav-tab {
          background: transparent;
          border: none;
          color: #8B949E;
          font-weight: 500;
          font-size: 14px;
          padding: 8px 16px;
          cursor: pointer;
          border-bottom: 2px solid transparent;
          transition: all 0.2s ease;
        }
        .pg-nav-tab.active {
          color: #58A6FF;
          border-bottom-color: #58A6FF;
        }

        .pg-cmd-block {
          background: #0D1117;
          border: 1px solid #30363D;
          border-radius: 6px;
          padding: 12px;
          position: relative;
        }
        .pg-copy-btn {
          position: absolute;
          right: 8px;
          top: 8px;
          background: #21262D;
          border: 1px solid #30363D;
          border-radius: 4px;
          padding: 4px;
          cursor: pointer;
          color: #8B949E;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;
        }
        .pg-copy-btn:hover {
          background: #30363D;
          color: #F0F6FC;
        }

        @keyframes pg-pulse {
          0% { box-shadow: 0 0 0 0 rgba(226,80,74,0.4); }
          70% { box-shadow: 0 0 0 6px rgba(226,80,74,0); }
          100% { box-shadow: 0 0 0 0 rgba(226,80,74,0); }
        }
        .pg-live-dot { animation: pg-pulse 2s infinite; }
      `}</style>

      <div style={{ maxWidth: 1400, margin: "0 auto" }}>
        
        {/* TOP METRICS SUMMARY CARDS */}
        <div style={{ display: "flex", gap: 16, marginBottom: 28, flexWrap: "wrap" }}>
          <div className="pg-metric-card">
            <div style={{ fontSize: 12, color: "#8B949E", fontWeight: 500, textTransform: "uppercase" }}>Total Threats</div>
            <div className="pg-display" style={{ fontSize: 28, fontWeight: 600, color: "#F0F6FC", marginTop: 4 }}>{metrics.total}</div>
          </div>
          <div className="pg-metric-card" style={{ borderLeft: "4px solid #E2504A" }}>
            <div style={{ fontSize: 12, color: "#E2504A", fontWeight: 500, textTransform: "uppercase" }}>Critical</div>
            <div className="pg-display" style={{ fontSize: 28, fontWeight: 600, color: "#F0F6FC", marginTop: 4 }}>{metrics.critical}</div>
          </div>
          <div className="pg-metric-card" style={{ borderLeft: "4px solid #F0A93D" }}>
            <div style={{ fontSize: 12, color: "#F0A93D", fontWeight: 500, textTransform: "uppercase" }}>High</div>
            <div className="pg-display" style={{ fontSize: 28, fontWeight: 600, color: "#F0F6FC", marginTop: 4 }}>{metrics.high}</div>
          </div>
          <div className="pg-metric-card" style={{ borderLeft: "4px solid #4FA3D1" }}>
            <div style={{ fontSize: 12, color: "#4FA3D1", fontWeight: 500, textTransform: "uppercase" }}>Medium</div>
            <div className="pg-display" style={{ fontSize: 28, fontWeight: 600, color: "#F0F6FC", marginTop: 4 }}>{metrics.medium}</div>
          </div>
          <div className="pg-metric-card">
            <div style={{ fontSize: 12, color: "#56D364", fontWeight: 500, textTransform: "uppercase" }}>Remediation Progress</div>
            <div className="pg-display" style={{ fontSize: 28, fontWeight: 600, color: "#56D364", marginTop: 4 }}>
              {metrics.total > 0 ? `${Math.round((metrics.resolved / metrics.total) * 100)}%` : "0%"}
            </div>
            <div style={{ fontSize: 11, color: "#8B949E", marginTop: 2 }}>{metrics.resolved} of {metrics.total} updated</div>
          </div>
        </div>

        {/* WORKSPACE CONTENT GRID */}
        <div style={{ display: "flex", gap: 24, alignItems: "flex-start" }}>
          
          {/* LEFT SIDE: SEARCH & FILTERS & FEED */}
          <div style={{ flex: 1, minWidth: 0 }}>
            
            {/* Top Bar with Navigation View Modes */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20, flexWrap: "wrap", gap: 16 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <ShieldAlert size={26} color="#E2504A" />
                <div>
                  <div className="pg-display" style={{ fontSize: 20, fontWeight: 600, letterSpacing: "0.01em", color: "#F0F6FC" }}>
                    PriviGuard · Enterprise Security Dashboard
                  </div>
                  <div className="pg-mono" style={{ fontSize: 12, color: "#8B949E", marginTop: 2 }}>
                    Identity Governance Access Monitor
                  </div>
                </div>
              </div>

              {/* View Mode Switcher */}
              <div style={{ display: "flex", background: "#161B22", padding: 4, borderRadius: 8, border: "1px solid #30363D" }}>
                <button
                  className={`pg-nav-tab ${viewMode === "all" ? "active" : ""}`}
                  onClick={() => { setViewMode("all"); setTypeFilter(null); }}
                  style={{ borderRadius: 6, padding: "6px 12px", borderBottom: "none" }}
                >
                  Threat Feed
                </button>
                <button
                  className={`pg-nav-tab ${viewMode === "offboarding" ? "active" : ""}`}
                  onClick={() => { setViewMode("offboarding"); setTypeFilter(null); }}
                  style={{ borderRadius: 6, padding: "6px 12px", borderBottom: "none" }}
                >
                  Offboarding Gaps
                </button>
              </div>
            </div>

            {/* Filter controls and Search Bar */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20, gap: 12, flexWrap: "wrap" }}>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {["Critical", "High", "Medium"].map((sev) => {
                  const meta = SEVERITY_META[sev];
                  const active = severityFilter === sev;
                  return (
                    <button
                      key={sev}
                      className="pg-chip"
                      onClick={() => setSeverityFilter(active ? null : sev)}
                      style={{
                        background: active ? meta.bg : "#161B22",
                        border: `1px solid ${active ? meta.color : "#30363D"}`,
                        borderRadius: 8,
                        padding: "6px 12px",
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                      }}
                    >
                      <span style={{ width: 6, height: 6, borderRadius: "50%", background: meta.color }} />
                      <span style={{ fontSize: 13, color: "#C9D1D9" }}>{meta.label}</span>
                      <span className="pg-mono" style={{ fontSize: 13, color: meta.color, fontWeight: 500 }}>
                        {counts[sev]}
                      </span>
                    </button>
                  );
                })}
              </div>

              {/* Search Bar */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  background: "#161B22",
                  border: "1px solid #30363D",
                  borderRadius: 8,
                  padding: "6px 12px",
                  minWidth: 260,
                  flex: 1,
                  maxWidth: 400
                }}
              >
                <Search size={15} color="#8B949E" />
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search name, EMP ID, platform..."
                  style={{
                    background: "transparent",
                    border: "none",
                    outline: "none",
                    color: "#C9D1D9",
                    fontSize: 13,
                    width: "100%",
                    fontFamily: "'Inter', sans-serif",
                  }}
                />
                {query && (
                  <X
                    size={14}
                    color="#8B949E"
                    style={{ cursor: "pointer" }}
                    onClick={() => setQuery("")}
                  />
                )}
              </div>
            </div>

            {/* View Mode specific notices */}
            {viewMode === "offboarding" && (
              <div style={{
                background: "rgba(226,80,74,0.08)",
                border: "1px solid rgba(226,80,74,0.3)",
                borderRadius: 8,
                padding: "12px 16px",
                display: "flex",
                alignItems: "flex-start",
                gap: 12,
                marginBottom: 20
              }}>
                <Info size={18} color="#E2504A" style={{ marginTop: 2, flexShrink: 0 }} />
                <div style={{ fontSize: 13, color: "#C9D1D9", lineHeight: 1.5 }}>
                  <strong style={{ color: "#E2504A" }}>Offboarding Violations Filter Active:</strong> The list below displays active login credentials belonging to employees whose HR status is marked <strong>DISABLED</strong>. Immediate remediation is required to revoke cloud access credentials.
                </div>
              </div>
            )}

            {/* List Header */}
            <div style={{
              display: "flex",
              alignItems: "center",
              padding: "8px 16px",
              background: "#161B22",
              border: "1px solid #21262D",
              borderRadius: "6px 6px 0 0",
              fontSize: 12,
              fontWeight: 600,
              color: "#8B949E",
              letterSpacing: "0.04em",
              textTransform: "uppercase"
            }}>
              <div style={{ flex: 1 }}>Violation / Identity</div>
              <div style={{ width: 140 }}>Platform</div>
              <div style={{ width: 140, textAlign: "right" }}>Status</div>
            </div>

            {/* Incident feed rows */}
            <div style={{ display: "flex", flexDirection: "column", gap: 1 }}>
              {filteredIncidents.length === 0 && (
                <div
                  style={{
                    padding: "48px 0",
                    textAlign: "center",
                    color: "#8B949E",
                    fontSize: 13,
                    background: "#0D1117",
                    border: "1px dashed #30363D",
                    borderRadius: "0 0 6px 6px"
                  }}
                >
                  No incidents match these filters.
                </div>
              )}

              {filteredIncidents.map((inc) => {
                const sev = SEVERITY_META[inc.severity] || { color: "#8B949E", bg: "#21262D", label: inc.severity };
                const typeMeta = TYPE_META[inc.incident_type] || { icon: ShieldAlert, color: "#8B949E" };
                const Icon = typeMeta.icon;
                const status = statuses[inc.id] || "OPEN";
                const isSelected = selectedIncidentId === inc.id;

                return (
                  <div
                    key={inc.id}
                    className={`pg-row ${isSelected ? "pg-row-selected" : ""}`}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      background: "#161B22",
                      border: "1px solid #21262D",
                      borderLeft: `4px solid ${sev.color}`,
                      padding: "14px 16px",
                      cursor: "pointer",
                      gap: 16
                    }}
                    onClick={() => setSelectedIncidentId(isSelected ? null : inc.id)}
                  >
                    <div style={{ flex: 1, minWidth: 0, display: "flex", gap: 14, alignItems: "flex-start" }}>
                      <div style={{ marginTop: 2, flexShrink: 0 }}>
                        <Icon size={18} color={typeMeta.color} />
                      </div>
                      <div style={{ minWidth: 0 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
                          <span style={{ fontSize: 15, fontWeight: 600, color: "#F0F6FC" }}>
                            {inc.incident_type}
                          </span>
                          <span
                            style={{
                              fontSize: 11,
                              fontWeight: 600,
                              color: sev.color,
                              background: sev.bg,
                              padding: "2px 6px",
                              borderRadius: 4,
                            }}
                          >
                            {sev.label.toUpperCase()}
                          </span>
                        </div>
                        <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 4, fontSize: 13, color: "#8B949E" }}>
                          <span style={{ color: "#C9D1D9", fontWeight: 500 }}>{inc.full_name}</span>
                          <span>·</span>
                          <span className="pg-mono" style={{ fontSize: 12 }}>{inc.user_id}</span>
                        </div>
                      </div>
                    </div>

                    {/* Platform Badge */}
                    <div style={{ width: 140, flexShrink: 0 }}>
                      <span
                        className="pg-mono"
                        style={{
                          fontSize: 12,
                          background: "#21262D",
                          border: "1px solid #30363D",
                          padding: "3px 8px",
                          borderRadius: 6,
                          color: "#F0F6FC"
                        }}
                      >
                        {inc.platform}
                      </span>
                    </div>

                    {/* Interactive Status Cycle Button */}
                    <div style={{ width: 140, flexShrink: 0, display: "flex", justifyContent: "flex-end" }} onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => cycleStatus(inc.id)}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 6,
                          background: "none",
                          border: "1px solid #30363D",
                          borderRadius: 6,
                          padding: "5px 12px",
                          fontSize: 12,
                          fontWeight: 500,
                          cursor: "pointer",
                          transition: "all 0.2s ease",
                          color:
                            status === "REMEDIATED"
                              ? "#56D364"
                              : status === "ACKNOWLEDGED"
                              ? "#F0A93D"
                              : "#8B949E",
                          borderColor:
                            status === "REMEDIATED"
                              ? "#56D364"
                              : status === "ACKNOWLEDGED"
                              ? "#F0A93D"
                              : "#30363D"
                        }}
                      >
                        {status === "REMEDIATED" ? (
                          <CheckCircle2 size={13} />
                        ) : (
                          <CircleDot size={13} />
                        )}
                        {status}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* RIGHT SIDE: COLLAPSIBLE DRILL-DOWN PANEL */}
          {selectedIncident && (
            <div className="pg-sidebar" style={{ width: 440, padding: 20, flexShrink: 0 }}>
              
              {/* Sidebar Header */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20, borderBottom: "1px solid #30363D", paddingBottom: 16 }}>
                <div>
                  <div className="pg-mono" style={{ fontSize: 11, color: "#8B949E", letterSpacing: "0.04em" }}>INCIDENT DETAIL</div>
                  <div className="pg-display" style={{ fontSize: 18, fontWeight: 600, color: "#F0F6FC", marginTop: 4 }}>
                    {selectedIncident.incident_type}
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 6 }}>
                    <span
                      style={{
                        fontSize: 10,
                        fontWeight: 600,
                        color: SEVERITY_META[selectedIncident.severity]?.color || "#C9D1D9",
                        background: SEVERITY_META[selectedIncident.severity]?.bg || "#21262D",
                        padding: "2px 6px",
                        borderRadius: 4,
                      }}
                    >
                      {selectedIncident.severity.toUpperCase()}
                    </span>
                    <span className="pg-mono" style={{ fontSize: 12, color: "#8B949E" }}>{selectedIncident.user_id}</span>
                  </div>
                </div>
                
                <button
                  onClick={() => setSelectedIncidentId(null)}
                  style={{
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    color: "#8B949E",
                    padding: 4,
                    display: "flex",
                    borderRadius: 4,
                    alignItems: "center"
                  }}
                  className="pg-chip"
                >
                  <X size={18} />
                </button>
              </div>

              {/* Incident Meta Details */}
              <div style={{ display: "flex", flexDirection: "column", gap: 14, marginBottom: 20 }}>
                
                <div>
                  <div style={{ fontSize: 12, color: "#8B949E", fontWeight: 500 }}>Employee Name</div>
                  <div style={{ fontSize: 14, color: "#F0F6FC", fontWeight: 500, marginTop: 4 }}>{selectedIncident.full_name}</div>
                </div>

                <div style={{ display: "flex", gap: 16 }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 12, color: "#8B949E", fontWeight: 500 }}>Platform</div>
                    <div style={{ fontSize: 13, color: "#F0F6FC", fontWeight: 500, marginTop: 4 }}>{selectedIncident.platform}</div>
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 12, color: "#8B949E", fontWeight: 500 }}>Detected At</div>
                    <div className="pg-mono" style={{ fontSize: 12, color: "#F0F6FC", marginTop: 4 }}>
                      {selectedIncident.detected_at.replace("T", " ")}
                    </div>
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: 12, color: "#8B949E", fontWeight: 500 }}>Description</div>
                  <div style={{ fontSize: 13, color: "#C9D1D9", lineHeight: 1.5, background: "#0D1117", border: "1px solid #21262D", borderRadius: 6, padding: 12, marginTop: 6 }}>
                    {selectedIncident.description}
                  </div>
                </div>
              </div>

              {/* BLAST RADIUS ASSESSMENT */}
              <div style={{ marginBottom: 24 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                  <AlertIcon size={14} color="#F0A93D" />
                  <div style={{ fontSize: 12, color: "#F0A93D", fontWeight: 600, letterSpacing: "0.04em", textTransform: "uppercase" }}>
                    Blast Radius Assessment
                  </div>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  {getBlastRadiusAssessment(selectedIncident)?.map((sect, i) => (
                    <div key={i} style={{ background: "#21262D", borderRadius: 8, padding: 12, border: "1px solid #30363D" }}>
                      <div style={{ fontSize: 12, fontWeight: 600, color: "#F0F6FC" }}>{sect.title}</div>
                      <ul style={{ paddingLeft: 16, margin: "8px 0 0 0", fontSize: 12, color: "#C9D1D9", display: "flex", flexDirection: "column", gap: 6, lineHeight: 1.4 }}>
                        {sect.items.map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>

              {/* ACTION REMEDIATION CONSOLE */}
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                  <Terminal size={14} color="#58A6FF" />
                  <div style={{ fontSize: 12, color: "#58A6FF", fontWeight: 600, letterSpacing: "0.04em", textTransform: "uppercase" }}>
                    Remediation CLI Console
                  </div>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  {getRemediationCommands(selectedIncident).map((cmdObj, i) => (
                    <div key={i} style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                      <div style={{ fontSize: 11, fontWeight: 500, color: "#8B949E" }}>{cmdObj.label}</div>
                      <div className="pg-cmd-block">
                        <pre className="pg-mono" style={{ margin: 0, fontSize: 11, color: "#58A6FF", overflowX: "auto", whiteSpace: "pre-wrap", paddingRight: 24 }}>
                          {cmdObj.cmd}
                        </pre>
                        <button
                          className="pg-copy-btn"
                          onClick={() => handleCopy(cmdObj.cmd, `${i}`)}
                        >
                          {copiedCommand === `${i}` ? (
                            <Check size={12} color="#56D364" />
                          ) : (
                            <Copy size={12} />
                          )}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          )}

        </div>
      </div>
    </div>
  );
}
