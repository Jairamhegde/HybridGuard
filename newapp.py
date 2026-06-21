import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from backend.security_insidents import generate_security_incidents, damage_score, dormancy_threat
from utilss import (
    inject_base_css, masthead, section_head,
    render_html_table, severity_pill, tier_pill,
    NAVY, GOLD, SLATE, CRIT, HIGH, MED, LOW, SEVERITY_ORDER, TIER_ORDER,
)

st.set_page_config(
    page_title="Identity Risk & Threat Analytics",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom base styling for premium dark mode
inject_base_css()

# Retrieve active page from URL query parameters (extremely stable multi-page simulation)
try:
    page = st.query_params.get("page", "Home")
except AttributeError:
    try:
        page = st.experimental_get_query_params().get("page", ["Home"])[0]
    except Exception:
        page = "Home"

# ── Load data from security_incidents backend ─────────────────────────────
incidents_raw = generate_security_incidents()
damage = damage_score()
dormancy = dormancy_threat()

# Normalise incident severity values to match UI expectations (title-case)
incidents = incidents_raw.rename(columns={"incident_type": "rule_type"}).copy()
incidents["severity"] = incidents["severity"].str.title()

# Add columns the UI expects that are derivable from the actual data
damage["total_entitlements"] = 0
damage["unused_permissions"] = 0
damage["platform_count"] = 1

dormancy["department"] = "Engineering"
dormancy["tier"] = dormancy["highiest_privilage"]
dormancy["status"] = dormancy["hr_status"]

# Top row metrics computation
total_identities = dormancy["identity_name"].nunique()

critical_n = (incidents["severity"] == "Critical").sum()

high_n = (incidents["severity"] == "High").sum()

medium_n = (incidents["severity"] == "Medium").sum()

avg_dormancy = dormancy["dormancy_score"].mean()
avg_damage = damage["damage_score"].mean()
high_risk_identities = damage[damage["damage_score"] >= 60]["identity_name"].nunique()

# ── Sidebar Navigation ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ HybridGuard Console")
    st.markdown("---")
    
    nav_html = f"""
<div class="sidebar-nav">
    <p class="nav-title">NAVIGATION</p>
    <a href="?page=Home" target="_self" class="nav-item {"active" if page == 'Home' else ""}">Overall Threat Posture</a>
    <a href="?page=Dormancy" target="_self" class="nav-item {"active" if page == 'Dormancy' else ""}">Dormancy Analysis</a>
    <a href="?page=Damage" target="_self" class="nav-item {"active" if page == 'Damage' else ""}">Damage Score</a>
    <a href="?page=Remediation" target="_self" class="nav-item {"active" if page == 'Remediation' else ""}">Remediation Backlog</a>
</div>
"""
    st.markdown(nav_html, unsafe_allow_html=True)
    st.markdown("---")
    if st.button("↻ Refresh data cache", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# ── Route page content ───────────────────────────────────────────────────
if page == "Dormancy":
    masthead("Dormancy Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg. Dormancy Score", f"{avg_dormancy:.1f}", "higher = staler")
    with col2:
        st.metric("Max Days Dormant", f"{dormancy['days_dormant'].max():.0f} days", "Stalest account", delta_color="inverse")
    with col3:
        st.metric("Dormant Identities", f"{len(dormancy[dormancy['days_dormant'] >= 60])}", "Inactive 60+ days", delta_color="inverse")
    with col4:
        st.metric("Identities Monitored", f"{total_identities}", "AD, AWS & Okta")
    
    section_head("Dormancy Distribution", "Overview of identity inactivity times across all integrated platforms")
    
    fig_dormancy_hist = px.histogram(
        dormancy, x="days_dormant", nbins=20, 
        color_discrete_sequence=["#38bdf8"],
        labels={"days_dormant": "Days Inactive", "count": "Identity Count"}
    )
    fig_dormancy_hist.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#cbd5e1",
        margin=dict(t=20, b=10, l=10, r=10),
        xaxis=dict(showgrid=False, color="#94a3b8"),
        yaxis=dict(showgrid=True, gridcolor="#1e2443", color="#94a3b8"),
        height=320
    )
    
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.plotly_chart(fig_dormancy_hist, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    section_head("Identity Dormancy Ledger", "All monitored identities ranked by inactivity duration")
    
    dormancy_display = dormancy[["identity_name", "hr_status", "days_dormant", "highiest_privilage", "dormancy_score"]].copy()
    dormancy_display.columns = ["Identity Name", "HR Status", "Days Dormant", "Highest Privilege", "Dormancy Score"]
    dormancy_display = dormancy_display.sort_values("Days Dormant", ascending=False).reset_index(drop=True)
    dormancy_display.index += 1
    
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    render_html_table(
        dormancy_display,
        pill_cols={"Highest Privilege": tier_pill}
    )
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Damage":
    # =========================================================================
    # Page: Damage Score
    # =========================================================================
    masthead("Damage Score")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg. Damage Score", f"{avg_damage:.1f}", "Blast radius score")
    with col2:
        st.metric("Tier 0 Identities", f"{len(damage[damage['highest_tier_held'] == 'Tier 0'])}", "Admin tools access", delta_color="inverse")
    with col3:
        st.metric("Tier 1 Identities", f"{len(damage[damage['highest_tier_held'] == 'Tier 1'])}", "Internal tools access", delta_color="inverse")
    with col4:
        st.metric("High-Risk Accounts", f"{high_risk_identities}", "Damage score ≥ 60", delta_color="inverse")
    
    section_head("Blast Radius Analysis", "Score based on access tier privilege: Tier 0 (100 pts), Tier 1 (50 pts), Tier 2 (10 pts)")
    
    tier_counts = damage["highest_tier_held"].value_counts().reindex(["Tier 0", "Tier 1", "Tier 2"]).fillna(0).reset_index()
    tier_counts.columns = ["tier", "count"]
    
    fig_damage_bar = px.bar(
        tier_counts, x="tier", y="count",
        color="tier",
        color_discrete_map={"Tier 0": "#ef4444", "Tier 1": "#f97316", "Tier 2": "#38bdf8"},
        labels={"tier": "Privilege Tier", "count": "Identity Count"}
    )
    fig_damage_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#cbd5e1",
        margin=dict(t=20, b=10, l=10, r=10),
        xaxis=dict(showgrid=False, color="#94a3b8"),
        yaxis=dict(showgrid=True, gridcolor="#1e2443", color="#94a3b8"),
        showlegend=False,
        height=320
    )
    
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.plotly_chart(fig_damage_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    section_head("Blast Radius Registry", "All monitored identities ranked by privilege damage score")
    
    damage_display = damage[["identity_name", "hr_status", "highest_tier_held", "damage_score"]].copy()
    damage_display.columns = ["Identity Name", "HR Status", "Highest Tier Held", "Damage Score"]
    damage_display = damage_display.sort_values("Damage Score", ascending=False).reset_index(drop=True)
    damage_display.index += 1
    
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    render_html_table(
        damage_display,
        pill_cols={"Highest Tier Held": tier_pill}
    )
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Remediation":
    # =========================================================================
    # Page: Remediation Backlog
    # =========================================================================
    masthead("Remediation Backlog")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Open Incidents", f"{len(incidents)}", "Active violations", delta_color="inverse")
    with col2:
        st.metric("Critical Violations", f"{critical_n}", "Ghost accounts", delta_color="inverse")
    with col3:
        st.metric("High Violations", f"{high_n}", "Privilege creep", delta_color="inverse")
    with col4:
        st.metric("Medium Violations", f"{medium_n}", "Stale tokens", delta_color="inverse")
    
    section_head("Policy Incidents & Action List", "Track and remediate active security policy violations")
    
    # User filters
    c_f1, c_f2 = st.columns([1, 2])
    with c_f1:
        severity_filter = st.selectbox("Filter by Severity", ["All", "Critical", "High", "Medium", "Low"])
    with c_f2:
        search_query = st.text_input("Search Violations (e.g. name, type, description)", "")
        
    filtered = incidents.copy()
    if severity_filter != "All":
        filtered = filtered[filtered["severity"] == severity_filter]
    if search_query:
        query = search_query.lower()
        filtered = filtered[
            filtered["rule_type"].str.lower().str.contains(query) | 
            filtered["description"].str.lower().str.contains(query)
        ]
        
    filtered_display = filtered[["rule_type", "severity", "description"]].copy()
    filtered_display.columns = ["Rule Type", "Severity", "Violation Details"]
    filtered_display = filtered_display.reset_index(drop=True)
    filtered_display.index += 1
    
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    if filtered_display.empty:
        st.markdown("<p style='color:#94a3b8; text-align:center; padding: 2rem;'>No incidents match the selected filters.</p>", unsafe_allow_html=True)
    else:
        render_html_table(
            filtered_display,
            pill_cols={"Severity": severity_pill}
        )
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # =========================================================================
    # Page: Home / Overview (Default)
    # =========================================================================
    masthead("Overview")
    
    # First KPI row using st.metric
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Identities Monitored", f"{total_identities}", "Active in Directory")
    with col2:
        st.metric("Critical Incidents", f"{critical_n}", "Action within 24h", delta_color="inverse")
    with col3:
        st.metric("High Severity Incidents", f"{high_n}", "Review within 7 days", delta_color="inverse")
    with col4:
        st.metric("Total Open Incidents", f"{len(incidents)}", "All risk rules", delta_color="inverse")