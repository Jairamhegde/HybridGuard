import React, { useState, useEffect } from 'react';
import { Network, Server, Shield, User, Filter, RefreshCw, Info, ExternalLink } from 'lucide-react';

export default function IdentityGraphView({ API_BASE_URL, onSelectIdentity }) {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);
  const [platformFilter, setPlatformFilter] = useState('All');

  const fetchGraph = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/graph-data?limit=15`);
      const data = await res.json();
      setGraphData(data);
      if (data.nodes && data.nodes.length > 0) {
        setSelectedNode(data.nodes[0]);
      }
      setLoading(false);
    } catch (err) {
      console.error("Failed to fetch graph data", err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraph();
  }, []);

  const filteredNodes = graphData.nodes.filter(node => {
    if (platformFilter === 'All') return true;
    if (node.type === 'identity') return true;
    return node.platform?.toUpperCase() === platformFilter.toUpperCase();
  });

  const filteredLinks = graphData.links.filter(link => {
    const src = filteredNodes.find(n => n.id === link.source);
    const tgt = filteredNodes.find(n => n.id === link.target);
    return src && tgt;
  });

  // Calculate SVG layout coordinates for clean node positioning
  const userNodes = filteredNodes.filter(n => n.type === 'identity');
  const accountNodes = filteredNodes.filter(n => n.type === 'account');
  const roleNodes = filteredNodes.filter(n => n.type === 'role');

  const getNodeCoords = (node) => {
    if (node.type === 'identity') {
      const idx = userNodes.findIndex(n => n.id === node.id);
      const y = 80 + idx * 85;
      return { x: 120, y };
    } else if (node.type === 'account') {
      const idx = accountNodes.findIndex(n => n.id === node.id);
      const y = 60 + idx * 65;
      return { x: 420, y };
    } else {
      const idx = roleNodes.findIndex(n => n.id === node.id);
      const y = 50 + idx * 55;
      return { x: 740, y };
    }
  };

  return (
    <div>
      {/* Header & Controls Panel */}
      <div className="glass-panel" style={{ padding: '1.25rem 1.5rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Network size={22} color="#9f1239" />
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#29181d' }} className="title-font">
                Identity Access Relationship Graph
              </h3>
              <p style={{ fontSize: '0.78rem', color: '#6b5860' }}>
                Visual map connecting HR Master Identities → Platform Accounts → Attached Privilege Tiers
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Filter size={15} color="#6b5860" />
              <span style={{ fontSize: '0.8rem', color: '#6b5860', fontWeight: 600 }}>Platform Filter:</span>
              <select
                value={platformFilter}
                onChange={(e) => setPlatformFilter(e.target.value)}
                style={{
                  background: '#ffffff',
                  color: '#29181d',
                  border: '1px solid #d8ccc2',
                  borderRadius: '6px',
                  padding: '0.4rem 0.75rem',
                  fontSize: '0.8rem',
                  outline: 'none',
                  cursor: 'pointer'
                }}
              >
                <option value="All">All Platforms</option>
                <option value="AWS">AWS</option>
                <option value="Okta">Okta</option>
                <option value="AD">Active Directory</option>
              </select>
            </div>

            <button onClick={fetchGraph} className="btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>
              <RefreshCw size={14} />
              <span>Reload Graph</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Interactive Graph & Inspector Split View */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '1.5rem' }}>
        {/* SVG Network Canvas */}
        <div className="glass-panel" style={{ padding: '1.25rem', overflow: 'auto', minHeight: '620px', background: '#ffffff' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '5rem', color: '#6b5860' }}>
              <p>Loading identity access relationship network...</p>
            </div>
          ) : (
            <div style={{ width: '100%', minWidth: '850px', overflowX: 'auto' }}>
              <svg width="860" height={Math.max(600, userNodes.length * 90)} style={{ display: 'block' }}>
                {/* SVG Definitions for Gradients */}
                <defs>
                  <linearGradient id="linkGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#be123c" stopOpacity="0.4" />
                    <stop offset="100%" stopColor="#0284c7" stopOpacity="0.4" />
                  </linearGradient>
                </defs>

                {/* Render Connecting Line Links */}
                {filteredLinks.map((link, idx) => {
                  const srcNode = filteredNodes.find(n => n.id === link.source);
                  const tgtNode = filteredNodes.find(n => n.id === link.target);
                  if (!srcNode || !tgtNode) return null;

                  const srcC = getNodeCoords(srcNode);
                  const tgtC = getNodeCoords(tgtNode);

                  const isHighlighted = selectedNode && (selectedNode.id === srcNode.id || selectedNode.id === tgtNode.id);

                  return (
                    <g key={idx}>
                      <path
                        d={`M ${srcC.x + 80} ${srcC.y} C ${(srcC.x + tgtC.x) / 2} ${srcC.y}, ${(srcC.x + tgtC.x) / 2} ${tgtC.y}, ${tgtC.x - 70} ${tgtC.y}`}
                        fill="none"
                        stroke={isHighlighted ? '#be123c' : '#e6ded6'}
                        strokeWidth={isHighlighted ? 2.5 : 1.5}
                        strokeDasharray={link.label === 'assigned' ? '4 3' : 'none'}
                      />
                    </g>
                  );
                })}

                {/* Render Nodes */}
                {filteredNodes.map((node) => {
                  const c = getNodeCoords(node);
                  const isSelected = selectedNode?.id === node.id;

                  let fillBg = '#ffffff';
                  let strokeCol = '#d8ccc2';
                  let textColor = '#29181d';

                  if (node.type === 'identity') {
                    fillBg = isSelected ? '#fff1f2' : '#ffffff';
                    strokeCol = isSelected ? '#be123c' : '#9f1239';
                  } else if (node.type === 'account') {
                    fillBg = isSelected ? '#f0f9ff' : '#ffffff';
                    strokeCol = isSelected ? '#0284c7' : '#bae6fd';
                  } else if (node.type === 'role') {
                    fillBg = node.tier === 'Tier 0' ? '#fff1f2' : node.tier === 'Tier 1' ? '#fff7ed' : '#f0fdfa';
                    strokeCol = node.tier === 'Tier 0' ? '#fecdd3' : node.tier === 'Tier 1' ? '#ffedd5' : '#ccfbf1';
                  }

                  return (
                    <g
                      key={node.id}
                      transform={`translate(${c.x}, ${c.y})`}
                      onClick={() => setSelectedNode(node)}
                      style={{ cursor: 'pointer' }}
                    >
                      <rect
                        x="-75"
                        y="-22"
                        width="150"
                        height="44"
                        rx="8"
                        fill={fillBg}
                        stroke={strokeCol}
                        strokeWidth={isSelected ? 2.5 : 1.5}
                        filter={isSelected ? 'drop-shadow(0px 4px 10px rgba(190, 18, 60, 0.2))' : 'none'}
                      />

                      <text
                        x="0"
                        y="4"
                        textAnchor="middle"
                        fill={textColor}
                        fontSize="11"
                        fontWeight={isSelected ? '700' : '600'}
                        fontFamily="'Inter', sans-serif"
                      >
                        {node.label.length > 20 ? node.label.slice(0, 18) + '...' : node.label}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>
          )}
        </div>

        {/* Node Detail Inspector Panel */}
        <div className="glass-panel" style={{ padding: '1.25rem', height: '100%', background: '#ffffff' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', paddingBottom: '0.75rem', borderBottom: '1px solid #e6ded6' }}>
            <Info size={18} color="#9f1239" />
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#29181d' }} className="title-font">
              Node Inspector
            </h4>
          </div>

          {selectedNode ? (
            <div>
              <div style={{ marginBottom: '1rem' }}>
                <span className={`pill-badge ${selectedNode.type === 'identity' ? 'pill-crit' : selectedNode.type === 'account' ? 'pill-tier2' : 'pill-high'}`}>
                  {selectedNode.type.toUpperCase()} NODE
                </span>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#29181d', marginTop: '0.4rem' }} className="title-font">
                  {selectedNode.label}
                </h3>
              </div>

              <div style={{ background: '#faf6f1', padding: '0.85rem', borderRadius: '8px', border: '1px solid #e6ded6', marginBottom: '1.25rem' }}>
                {selectedNode.type === 'identity' && (
                  <>
                    <div style={{ fontSize: '0.8rem', color: '#6b5860', marginBottom: '0.3rem' }}>
                      <strong>HR Status:</strong> {selectedNode.status}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#6b5860', marginBottom: '0.3rem' }}>
                      <strong>Risk Score:</strong> <span style={{ color: '#9f1239', fontWeight: 700 }}>{selectedNode.risk_score?.toFixed(1)} / 100</span>
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#6b5860' }}>
                      <strong>Highest Privilege:</strong> {selectedNode.tier || 'Tier 2'}
                    </div>
                  </>
                )}

                {selectedNode.type === 'account' && (
                  <>
                    <div style={{ fontSize: '0.8rem', color: '#6b5860', marginBottom: '0.3rem' }}>
                      <strong>Platform:</strong> {selectedNode.platform}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#6b5860' }}>
                      <strong>Account Status:</strong> {selectedNode.status}
                    </div>
                  </>
                )}

                {selectedNode.type === 'role' && (
                  <>
                    <div style={{ fontSize: '0.8rem', color: '#6b5860', marginBottom: '0.3rem' }}>
                      <strong>Platform:</strong> {selectedNode.platform}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#6b5860' }}>
                      <strong>Privilege Tier:</strong> {selectedNode.tier}
                    </div>
                  </>
                )}
              </div>

              {selectedNode.type === 'identity' && (
                <button
                  onClick={() => onSelectIdentity(selectedNode.identity_id)}
                  className="btn-primary"
                  style={{ width: '100%', justifyContent: 'center' }}
                >
                  <ExternalLink size={15} />
                  <span>Open Identity Lineage Drawer</span>
                </button>
              )}
            </div>
          ) : (
            <p style={{ fontSize: '0.82rem', color: '#6b5860' }}>
              Click any node on the graph canvas to inspect its permissions and attached privileges.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
