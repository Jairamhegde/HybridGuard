import React, { useState, useMemo , useEffect} from "react";
import {
  ShieldAlert, Ghost, TrendingUp, KeyRound, ChevronDown,
  Search, CircleDot, CheckCircle2, X,
} from "lucide-react";

const FONT_IMPORT_URL =
  "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap";

const SEVERITY_META = {
  CRITICAL: { color: "#E2504A", bg: "rgba(226,80,74,0.12)", label: "Critical" },
  HIGH: { color: "#F0A93D", bg: "rgba(240,169,61,0.12)", label: "High" },
  MEDIUM: { color: "#4FA3D1", bg: "rgba(79,163,209,0.12)", label: "Medium" },
};

const TYPE_META = {
  "Ghost Account": { icon: Ghost, color: "#E2504A" },
  "Privilege Creep": { icon: TrendingUp, color: "#F0A93D" },
  "Stale Security Token": { icon: KeyRound, color: "#4FA3D1" },
};

// Mock data shaped exactly like the SQL output: incident_type, severity, description.
// identity/platform/status/created_at are parsed or derived for display purposes.
// const RAW_INCIDENTS = [
//   { incident_type: "Ghost Account", severity: "CRITICAL", description: "User Maria Chen is marked DISABLED in HR, but still has an ACTIVE AWS account.", status: "OPEN", created_at: "2026-06-18T09:14:00" },
//   { incident_type: "Ghost Account", severity: "CRITICAL", description: "User Derek Holt is marked DISABLED in HR, but still has an ACTIVE Okta account.", status: "OPEN", created_at: "2026-06-17T22:41:00" },
//   { incident_type: "Ghost Account", severity: "CRITICAL", description: "User Priya Nair is marked DISABLED in HR, but still has an ACTIVE AWS account.", status: "ACKNOWLEDGED", created_at: "2026-06-15T11:02:00" },
//   { incident_type: "Privilege Creep", severity: "HIGH", description: "User Sam Okafor is a standard Tier 2 employee, but holds elevated Tier 0 access (AdministratorAccess) in AWS.", status: "OPEN", created_at: "2026-06-18T14:30:00" },
//   { incident_type: "Privilege Creep", severity: "HIGH", description: "User Lena Fischer is a standard Tier 2 employee, but holds elevated Tier 1 access (Domain Admin) in AD.", status: "OPEN", created_at: "2026-06-16T08:55:00" },
//   { incident_type: "Privilege Creep", severity: "HIGH", description: "User Ravi Shah is a standard Tier 2 employee, but holds elevated Tier 0 access (Admin) in Okta.", status: "OPEN", created_at: "2026-06-14T17:20:00" },
//   { incident_type: "Privilege Creep", severity: "HIGH", description: "User Jonas Weber is a standard Tier 2 employee, but holds elevated Tier 1 access (IAMFullAccess) in AWS.", status: "ACKNOWLEDGED", created_at: "2026-06-12T10:10:00" },
//   { incident_type: "Stale Security Token", severity: "MEDIUM", description: "Active AWS account for Maria Chen has no record of token rotation.", status: "OPEN", created_at: "2026-06-18T06:00:00" },
//   { incident_type: "Stale Security Token", severity: "MEDIUM", description: "Active Okta account for Tom Bridges has no record of token rotation.", status: "OPEN", created_at: "2026-06-17T06:00:00" },
//   { incident_type: "Stale Security Token", severity: "MEDIUM", description: "Active AWS account for Aisha Bello has no record of token rotation.", status: "OPEN", created_at: "2026-06-16T06:00:00" },
//   { incident_type: "Stale Security Token", severity: "MEDIUM", description: "Active Okta account for Derek Holt has no record of token rotation.", status: "OPEN", created_at: "2026-06-15T06:00:00" },
//   { incident_type: "Stale Security Token", severity: "MEDIUM", description: "Active AWS account for Ravi Shah has no record of token rotation.", status: "REMEDIATED", created_at: "2026-06-10T06:00:00" },
// ];

function parseIdentity(description) {
  const match = description.match(/^(?:User |Active )(.+?) (?:is |has )/);
  return match ? match[1] : null;
}

function parsePlatform(description) {
  const match = description.match(/\b(AWS|Okta|AD)\b/);
  return match ? match[1] : null;
}

function timeAgo(iso) {
  const diffMs = Date.now() - new Date(iso).getTime();
  const hrs = Math.floor(diffMs / 3.6e6);
  if (hrs < 1) return "just now";
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export default function SecurityIncidentDashboard() {
  const [incidents, setIncidents] = useState([])
    useEffect(() => {
    fetch("http://localhost:8000/")
      .then(res => res.json())
      .then(data => {
        const mapped = data.map((row, i) => ({
          id: i + 1,
          ...row,
          status: "OPEN",
          created_at: new Date().toISOString(),
          identity: parseIdentity(row.description) || "Unknown",
          platform: parsePlatform(row.description) || "—",
        }));
        setIncidents(mapped);
        setStatuses(Object.fromEntries(mapped.map((inc) => [inc.id, "OPEN"])));
      })
      .catch(err => console.error("Failed to fetch incidents:", err));
  }, []);
  const [statuses, setStatuses] = useState({});
  const [severityFilter, setSeverityFilter] = useState(null);
  const [typeFilter, setTypeFilter] = useState(null);
  const [query, setQuery] = useState("");
  const [expandedId, setExpandedId] = useState(null);

  const counts = useMemo(() => {
    const out = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, OPEN: 0 };
    incidents.forEach((inc) => {
      out[inc.severity] = (out[inc.severity] || 0) + 1;
      if (statuses[inc.id] === "OPEN") out.OPEN += 1;
    });
    return out;
  }, [incidents, statuses]);

  const typeCounts = useMemo(() => {
    const out = {};
    incidents.forEach((inc) => {
      out[inc.incident_type] = (out[inc.incident_type] || 0) + 1;
    });
    return out;
  }, [incidents]);

  const filtered = useMemo(() => {
    return incidents
      .filter((inc) => (severityFilter ? inc.severity === severityFilter : true))
      .filter((inc) => (typeFilter ? inc.incident_type === typeFilter : true))
      .filter((inc) =>
        query
          ? (inc.identity + inc.description + inc.platform)
              .toLowerCase()
              .includes(query.toLowerCase())
          : true
      )
      .sort((a, b) => {
        const order = { CRITICAL: 0, HIGH: 1, MEDIUM: 2 };
        return order[a.severity] - order[b.severity] || b.id - a.id;
      });
  }, [incidents, severityFilter, typeFilter, query]);

  const cycleStatus = (id) => {
    setStatuses((prev) => {
      const next = { ...prev };
      const order = ["OPEN", "ACKNOWLEDGED", "REMEDIATED"];
      const cur = order.indexOf(prev[id]);
      next[id] = order[(cur + 1) % order.length];
      return next;
    });
  };

  return (
    <div
      style={{
        fontFamily: "'Inter', sans-serif",
        background: "#12151C",
        color: "#E4E7EB",
        minHeight: "100vh",
        padding: "32px 24px",
      }}
    >
      <style>{`
        @import url('${FONT_IMPORT_URL}');
        .pg-mono { font-family: 'JetBrains Mono', monospace; }
        .pg-display { font-family: 'Space Grotesk', sans-serif; }
        .pg-row { transition: background 0.15s ease, border-color 0.15s ease; }
        .pg-row:hover { background: #1E2532 !important; }
        .pg-chip { transition: opacity 0.15s ease, border-color 0.15s ease; cursor: pointer; }
        .pg-chip:hover { opacity: 0.85; }
        @keyframes pg-pulse {
          0% { box-shadow: 0 0 0 0 rgba(226,80,74,0.55); }
          70% { box-shadow: 0 0 0 5px rgba(226,80,74,0); }
          100% { box-shadow: 0 0 0 0 rgba(226,80,74,0); }
        }
        .pg-live-dot { animation: pg-pulse 2s infinite; }
        @media (prefers-reduced-motion: reduce) {
          .pg-live-dot { animation: none; }
        }
        .pg-bar-segment { transition: flex-grow 0.3s ease; }
      `}</style>

      <div style={{ maxWidth: 920, margin: "0 auto" }}>
        {/* Top bar */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: 28,
            flexWrap: "wrap",
            gap: 16,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <ShieldAlert size={22} color="#E2504A" />
            <div>
              <div
                className="pg-display"
                style={{ fontSize: 19, fontWeight: 600, letterSpacing: "0.01em" }}
              >
                PriviGuard · Incident feed
              </div>
              <div
                className="pg-mono"
                style={{ fontSize: 12, color: "#6B7585", marginTop: 2 }}
              >
                security_incidents · {incidents.length} records
              </div>
            </div>
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              background: "#1A2230",
              border: "1px solid #2A313D",
              borderRadius: 8,
              padding: "8px 12px",
              minWidth: 220,
            }}
          >
            <Search size={15} color="#6B7585" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search identity, platform..."
              style={{
                background: "transparent",
                border: "none",
                outline: "none",
                color: "#E4E7EB",
                fontSize: 13,
                width: "100%",
                fontFamily: "'Inter', sans-serif",
              }}
            />
            {query && (
              <X
                size={14}
                color="#6B7585"
                style={{ cursor: "pointer" }}
                onClick={() => setQuery("")}
              />
            )}
          </div>
        </div>

        {/* Stat chips */}
        <div style={{ display: "flex", gap: 10, marginBottom: 20, flexWrap: "wrap" }}>
          {["CRITICAL", "HIGH", "MEDIUM"].map((sev) => {
            const meta = SEVERITY_META[sev];
            const active = severityFilter === sev;
            return (
              <button
                key={sev}
                className="pg-chip"
                onClick={() => setSeverityFilter(active ? null : sev)}
                style={{
                  background: active ? meta.bg : "#1A2230",
                  border: `1px solid ${active ? meta.color : "#2A313D"}`,
                  borderRadius: 8,
                  padding: "8px 14px",
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                }}
              >
                <span
                  style={{
                    width: 7,
                    height: 7,
                    borderRadius: "50%",
                    background: meta.color,
                    display: "inline-block",
                  }}
                />
                <span style={{ fontSize: 13, color: "#E4E7EB" }}>{meta.label}</span>
                <span className="pg-mono" style={{ fontSize: 13, color: meta.color, fontWeight: 500 }}>
                  {counts[sev]}
                </span>
              </button>
            );
          })}
          <div
            style={{
              marginLeft: "auto",
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: "8px 14px",
              background: "#1A2230",
              border: "1px solid #2A313D",
              borderRadius: 8,
            }}
          >
            <CircleDot size={12} color="#E2504A" className="pg-live-dot" style={{ borderRadius: "50%" }} />
            <span className="pg-mono" style={{ fontSize: 12, color: "#8B94A3" }}>
              {counts.OPEN} open
            </span>
          </div>
        </div>

        {/* Incident type distribution */}
        <div style={{ marginBottom: 28 }}>
          <div
            className="pg-mono"
            style={{ fontSize: 11, color: "#6B7585", marginBottom: 8, letterSpacing: "0.04em" }}
          >
            INCIDENT TYPE DISTRIBUTION
          </div>
          <div
            style={{
              display: "flex",
              height: 8,
              borderRadius: 4,
              overflow: "hidden",
              background: "#1A2230",
              marginBottom: 10,
            }}
          >
            {Object.entries(typeCounts).map(([type, count]) => (
              <div
                key={type}
                className="pg-bar-segment"
                style={{
                  flexGrow: count,
                  background: TYPE_META[type]?.color || "#6B7585",
                }}
              />
            ))}
          </div>
          <div style={{ display: "flex", gap: 18, flexWrap: "wrap" }}>
            {Object.entries(typeCounts).map(([type, count]) => {
              const meta = TYPE_META[type] || { icon: ShieldAlert, color: "#6B7585" };
              const Icon = meta.icon;
              const active = typeFilter === type;
              return (
                <button
                  key={type}
                  className="pg-chip"
                  onClick={() => setTypeFilter(active ? null : type)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                    background: "none",
                    border: "none",
                    padding: 0,
                    opacity: active || !typeFilter ? 1 : 0.45,
                  }}
                >
                  <Icon size={14} color={meta.color} />
                  <span style={{ fontSize: 13, color: "#C4CAD3" }}>{type}</span>
                  <span className="pg-mono" style={{ fontSize: 12, color: "#6B7585" }}>
                    {count}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Case-file rows */}
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {filtered.length === 0 && (
            <div
              style={{
                padding: "32px 0",
                textAlign: "center",
                color: "#6B7585",
                fontSize: 13,
              }}
            >
              No incidents match these filters.
            </div>
          )}

          {filtered.map((inc) => {
            const sev = SEVERITY_META[inc.severity];
            const typeMeta = TYPE_META[inc.incident_type] || { icon: ShieldAlert, color: "#6B7585" };
            const Icon = typeMeta.icon;
            const status = statuses[inc.id];
            const expanded = expandedId === inc.id;

            return (
              <div
                key={inc.id}
                className="pg-row"
                style={{
                  display: "flex",
                  background: "#171C26",
                  border: "1px solid #232A38",
                  borderLeft: `3px solid ${sev.color}`,
                  borderRadius: 0,
                  cursor: "pointer",
                }}
                onClick={() => setExpandedId(expanded ? null : inc.id)}
              >
                <div style={{ flex: 1, padding: "12px 16px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
                    <span
                      style={{
                        fontSize: 11,
                        fontWeight: 500,
                        color: sev.color,
                        background: sev.bg,
                        padding: "2px 8px",
                        borderRadius: 4,
                        letterSpacing: "0.03em",
                      }}
                    >
                      {sev.label.toUpperCase()}
                    </span>
                    <Icon size={14} color={typeMeta.color} />
                    <span style={{ fontSize: 14, fontWeight: 500, color: "#E4E7EB" }}>
                      {inc.incident_type}
                    </span>
                    <span className="pg-mono" style={{ fontSize: 12, color: "#6B7585" }}>
                      {inc.identity} · {inc.platform}
                    </span>

                    <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 10 }}>
                      <span className="pg-mono" style={{ fontSize: 11, color: "#5A6273" }}>
                        {timeAgo(inc.created_at)}
                      </span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          cycleStatus(inc.id);
                        }}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 5,
                          background: "none",
                          border: "1px solid #2A313D",
                          borderRadius: 4,
                          padding: "3px 9px",
                          fontSize: 11,
                          color:
                            status === "REMEDIATED"
                              ? "#5DCAA5"
                              : status === "ACKNOWLEDGED"
                              ? "#F0A93D"
                              : "#8B94A3",
                        }}
                      >
                        {status === "REMEDIATED" ? (
                          <CheckCircle2 size={12} />
                        ) : (
                          <CircleDot size={12} />
                        )}
                        {status}
                      </button>
                      <ChevronDown
                        size={15}
                        color="#5A6273"
                        style={{
                          transform: expanded ? "rotate(180deg)" : "none",
                          transition: "transform 0.15s ease",
                        }}
                      />
                    </div>
                  </div>

                  {expanded && (
                    <div
                      style={{
                        marginTop: 10,
                        paddingTop: 10,
                        borderTop: "1px solid #232A38",
                        fontSize: 13,
                        color: "#A9B0BC",
                        lineHeight: 1.6,
                      }}
                    >
                      {inc.description}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
