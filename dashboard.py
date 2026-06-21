import sqlite3
from streamlit import expander
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from backend.db_connection import connect_db
from utilss import inject_table_css, render_data_table

from backend.security_insidents import generate_security_incidents, damage_score, dormancy_threat,calculate_risk_score
from utilss import (
    inject_base_css, masthead, section_head,
    render_html_table, severity_pill, tier_pill,
    NAVY, GOLD, SLATE, CRIT, HIGH, MED, LOW, SEVERITY_ORDER, TIER_ORDER,
)

st.set_page_config(
    page_title="Identity Risk & Threat Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_base_css()

try:
    page = st.query_params.get("page", "Home")
except AttributeError:
    try:
        page = st.experimental_get_query_params().get("page", ["Home"])[0]
    except Exception:
        page = "Home"

# ── Data Loading ──────────────────────────────────────────────────────────
incidents_raw, prevelage_df, ghost_acc, stale_token = generate_security_incidents()
damage = damage_score()
dormancy = dormancy_threat()
risk_df = calculate_risk_score(damage, dormancy)

no_of_incidents = len(incidents_raw)
incidents = incidents_raw.rename(columns={"incident_type": "rule_type"}).copy()
incidents["severity"] = incidents["severity"].str.title()


total_identities = dormancy["identity_name"].nunique()
critical_n = (incidents["severity"] == "Critical").sum()
high_n = (incidents["severity"] == "High").sum()
medium_n = (incidents["severity"] == "Medium").sum()

avg_dormancy = dormancy["dormancy_score"].mean()
avg_damage = damage["damage_score"].mean()
high_risk_identities = damage[damage["damage_score"] >= 60]["identity_name"].nunique()

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("#  HybridGuard Console")
    st.markdown("---")
    nav_html = f"""
        <div class="sidebar-nav">
            <p class="nav-title">NAVIGATION</p>
            <a href="?page=Home" target="_self" class="nav-item {"active" if page == 'Home' else ""}">Overall Threat Posture</a>
            <a href="?page=Dormancy" target="_self" class="nav-item {"active" if page == 'Dormancy' else ""}">Dormancy Analysis</a>
            <a href="?page=Damage" target="_self" class="nav-item {"active" if page == 'Damage' else ""}">Damage Score</a>
            <a href="?page=Remediation" target="_self" class="nav-item {"active" if page == 'Remediation' else ""}">Remediation Backlog</a>
            <a href="?page=Identities" target="_self" class="nav-item {"active" if page == 'Identities' else ""}">Identities</a>
        </div>
    """
    st.markdown(nav_html, unsafe_allow_html=True)
    st.markdown("---")
    if st.button("↻ Refresh data cache", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── Page Router ───────────────────────────────────────────────────────────

if page == "Dormancy":

    masthead("Dormancy Analysis")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Identities Monitored", f"{total_identities}", "AD, AWS & Okta")
    with col2:
        st.metric("Max Days Dormant", f"{dormancy['days_dormant'].max():.0f} days", "Stalest account", delta_color="inverse")
    with col3:
        st.metric("Dormant Identities", f"{len(dormancy[dormancy['days_dormant'] >= 60])}", "Inactive 60+ days", delta_color="inverse")
    with col4:
        st.metric("Avg. Dormancy Score", f"{avg_dormancy:.1f}", "higher = staler")

    section_head("Dormancy Distribution", "Overview of identity inactivity times across all integrated platforms")
    fig_dormancy_hist = px.histogram(
        dormancy, x="days_dormant", nbins=20,
        color_discrete_sequence=["#38bdf8"],
        labels={"days_dormant": "Days Inactive", "count": "Identity Count"}
    )
    fig_dormancy_hist.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#cbd5e1", margin=dict(t=20, b=10, l=10, r=10),
        xaxis=dict(showgrid=False, color="#94a3b8"),
        yaxis=dict(showgrid=True, gridcolor="#1e2443", color="#94a3b8"),
        height=320
    )
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.plotly_chart(fig_dormancy_hist, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    section_head("Dormancy Heatmap", "Average days inactive mapped by Privilege Tier and HR Status")
    heatmap_data = dormancy.pivot_table(
        index="highiest_privilage", columns="hr_status",
        values="days_dormant", aggfunc="mean"
    ).fillna(0)
    fig_heatmap = px.imshow(
        heatmap_data,
        labels=dict(x="HR Status", y="Privilege Tier", color="Avg Days Dormant"),
        x=heatmap_data.columns, y=heatmap_data.index,
        text_auto=".1f", aspect="auto",
        color_continuous_scale=[
            (0.00, "#1e293b"), (0.50, "#eab308"), (1.00, "#ef4444"),
        ]
    )
    fig_heatmap.update_layout(
        height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#cbd5e1", margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(showgrid=False, color="#94a3b8", title="HR Status"),
        yaxis=dict(showgrid=False, color="#94a3b8", title="Highest Privilege"),
    )
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    section_head("Identity Dormancy Ledger", "All monitored identities ranked by inactivity duration")
    dormancy_display = dormancy[["identity_name", "hr_status", "days_dormant", "highiest_privilage", "dormancy_score"]].copy()
    dormancy_display.columns = ["Identity Name", "HR Status", "Days Dormant", "Highest Privilege", "Dormancy Score"]
    dormancy_display = dormancy_display.sort_values("Days Dormant", ascending=False).reset_index(drop=True)
    dormancy_display.index += 1
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    render_html_table(dormancy_display, pill_cols={"Highest Privilege": tier_pill})
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("View Dormant table raw", expanded=False):
        st.dataframe(dormancy, use_container_width=True)

elif page == "Damage":
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
        tier_counts, x="tier", y="count", color="tier",
        color_discrete_map={"Tier 0": "#ef4444", "Tier 1": "#f97316", "Tier 2": "#38bdf8"},
        labels={"tier": "Privilege Tier", "count": "Identity Count"}
    )
    fig_damage_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#cbd5e1", margin=dict(t=20, b=10, l=10, r=10),
        xaxis=dict(showgrid=False, color="#94a3b8"),
        yaxis=dict(showgrid=True, gridcolor="#1e2443", color="#94a3b8"),
        showlegend=False, height=320
    )
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.plotly_chart(fig_damage_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    section_head("Blast Radius Registry", "All monitored identities ranked by privilege damage score")
    top_damage = damage.sort_values("damage_score", ascending=False)
    
    def disable_status(row):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE human_identities
            SET hr_status = 'DISABLED'
            WHERE identity_id = ?
        """, (int(row['identity_id']),))
        conn.commit()
        conn.close()
        st.toast(f"Status disabled for identity: {row['identity_name']} (ID: {row['identity_id']})")
        st.rerun()

    if top_damage.empty:
        st.markdown("<p style='color:#94a3b8; font-family: Inter, sans-serif; padding: 1rem;'>✅ No high-risk accounts found in the registry.</p>", unsafe_allow_html=True)
    else:
        inject_table_css()
        render_data_table(
            df=top_damage,
            columns=[
                {"label": "Identity ID",   "width": 1.0, "key": "identity_id", "type": "text"},
                {"label": "Identity",      "width": 2.2, "key": "identity_name", "type": "text", "color": "#ffffff", "weight": "600", "prefix": "👤 "},
                {"label": "HR Status",     "width": 1.2, "key": "hr_status", "type": "text"},
                {"label": "Highest Tier",  "width": 1.5, "key": "highest_tier_held", "type": "pill", "pill_fn": tier_pill},
                {"label": "Days Dormant",  "width": 1.2, "key": "days_dormant", "type": "text"},
                {"label": "Damage Score",  "width": 1.3, "key": "damage_score", "type": "score", "thresholds": {"high": 70, "medium": 40}},
            ],
            actions=[
                {"label": "DISABLE STATUS", "key_suffix": "dmg_inv", "width": 1.5, "on_click": disable_status},
            ],
            key_prefix="damage_registry",
        )

elif page == "Remediation":

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

    c_f1, c_f2 = st.columns([1, 2])
    with c_f1:
        severity_filter = st.selectbox("Filter by Severity", ["All", "Critical", "High", "Medium"])
    with c_f2:
        search_query = st.text_input("Search Violations ", "")

    filtered = incidents.copy()
    if severity_filter != "All":
        filtered = filtered[filtered["severity"] == severity_filter]
  

    def revoke_acces(row):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE accounts 
            SET account_status = 'DISABLED' 
            WHERE identity_id = ?
            AND platform_id = (SELECT platform_id FROM platforms WHERE platform_name = ?)
        """, (row['identity_id'], row['platform'])) # Notice lowercase keys based on your config

        cursor.execute("""
            DELETE FROM security_incidents 
            WHERE incident_type = ? AND platform = ? AND identity_id = ?
        """, (row['rule_type'], row['platform'], row['identity_id']))
        conn.commit()
        conn.close()

        st.toast(f"User status disabled {row['rule_type']} for ID: {row['identity_id']} in {row['platform']}.")
        st.rerun()


    def rotate_tockens(row):
        conn = connect_db()
        cur = conn.cursor()
        query = '''
        update accounts
        set token_rotated_date = datetime("now")
        where identity_id = ? AND platform_id = (SELECT platform_id FROM platforms WHERE platform_name = ?)
        '''
        cur.execute(query,(row['identity_id'], row['platform']))
        conn.commit()
        conn.close()
        st.toast(f"Token rotated for user: {row['identity_id']}")
        st.rerun()

    def revoke_tier(row):
        conn = connect_db()
        cur = conn.cursor()
        query = """
            DELETE FROM account_role_mapping
            WHERE account_id = (
                SELECT account_id FROM accounts 
                WHERE identity_id = ? AND platform_id = (SELECT platform_id FROM platforms WHERE platform_name = ?)
            )
            AND role_id IN (
                SELECT role_id FROM role_definitions WHERE normalized_tier = ?
            )
        """
        cur.execute(query,(row["identity_id"], row["platform"], row["elevated_tier"]))
        conn.commit()
        conn.close()
        st.toast(f"Revoked all the tier :{row['elevated_tier']} for user: {row['identity_id']}")
        st.rerun()

    

    inject_table_css()
    if search_query:
        query = search_query.lower()
        filtered = filtered[
            filtered["rule_type"].str.lower().str.contains(query) |
            filtered["description"].str.lower().str.contains(query)
        ]

    def handle_remediation(row):
        severity = row['severity'].upper()
        if severity == "CRITICAL":
            revoke_acces(row)    
        elif severity == "HIGH":
            revoke_tier(row)     
        elif severity == "MEDIUM":
            rotate_tockens(row)
   
    if filtered.empty:
        st.markdown("<p style='color:#94a3b8; text-align:center; padding: 2rem;'>No incidents match the selected filters.</p>", unsafe_allow_html=True)
    else:
        button_name = {
            "CRITICAL": "Disable User",
            "HIGH": "Revoke Access",
            "MEDIUM": "Rotate Token"
        }
        
        section_head("AWS", "Track and remediate active security policy violations")
        render_data_table(
            df=filtered[filtered['platform'] == "AWS"],
            columns=[
                {"label": "Rule Type",         "width": 1.5, "key": "rule_type",   "type": "text", "color": "#ffffff", "weight": "600"},
                {"label": "Identity id",          "width": 1.0, "key": "identity_id",    "type": "text", "color": "#94a3b8"},
                {"label": "Severity",          "width": 1.0, "key": "severity",    "type": "pill", "pill_fn": severity_pill},
                {"label": "Violation Details", "width": 3.5, "key": "description", "type": "text", "color": "#94a3b8"},
                {"label": "Platform",          "width": 1.0, "key": "platform",    "type": "text", "color": "#94a3b8"},   

            ],
            actions=[
                {"label":lambda row: button_name.get(row['severity'].upper(), "Remove"), "key_suffix": "remove", "width": 1.0, "on_click":handle_remediation},
            ],
            key_prefix="violations_aws",
        )
        section_head("Okta", "Track and remediate active security policy violations")
        render_data_table(
            df=filtered[filtered['platform'] == "Okta"],
            columns=[
                {"label": "Rule Type",         "width": 1.5, "key": "rule_type",   "type": "text", "color": "#ffffff", "weight": "600"},
                {"label": "Identity id",          "width": 1.0, "key": "identity_id",    "type": "text", "color": "#94a3b8"},
                {"label": "Severity",          "width": 1.0, "key": "severity",    "type": "pill", "pill_fn": severity_pill},
                {"label": "Violation Details", "width": 3.5, "key": "description", "type": "text", "color": "#94a3b8"},
                {"label": "Platform",          "width": 1.0, "key": "platform",    "type": "text", "color": "#94a3b8"},
            ],
            actions=[
                {"label": lambda row: button_name.get(row['severity'].upper(), "Remove"), "key_suffix": "remove", "width": 1.0, "on_click": revoke_acces},
            ],
            key_prefix="violations_okta",
        )

        section_head("AD", "Track and remediate active security policy violations")
        render_data_table(
            df=filtered[filtered['platform'] == "AD"],
            columns=[
                {"label": "Rule Type",         "width": 1.5, "key": "rule_type",   "type": "text", "color": "#ffffff", "weight": "600"},
                {"label": "Identity id",          "width": 1.0, "key": "identity_id",    "type": "text", "color": "#94a3b8"},
                {"label": "Severity",          "width": 1.0, "key": "severity",    "type": "pill", "pill_fn": severity_pill},
                {"label": "Violation Details", "width": 3.5, "key": "description", "type": "text", "color": "#94a3b8"},
                {"label": "Platform",          "width": 1.0, "key": "platform",    "type": "text", "color": "#94a3b8"},
            ],
            actions=[
                {"label":lambda row: button_name.get(row['severity'].upper(), "Remove"), "key_suffix": "remove", "width": 1.0, "on_click": revoke_acces},
            ],
            key_prefix="violations_ad",
        )
        
elif page == "Identities":
    masthead("All Identities")
    search_term = st.text_input("Search Identities by Name", "")
    filtered_risk_df = risk_df.copy()
    if search_term:
        filtered_risk_df = filtered_risk_df[filtered_risk_df['identity_name'].str.lower().str.contains(search_term.lower())]
    
    inject_table_css()
    render_data_table(
        df=filtered_risk_df,
        columns=[
            {"label": "Identity ID",   "width": 0.8, "key": "identity_id",        "type": "text"},
            {"label": "Identity",      "width": 2.2, "key": "identity_name",      "type": "text", "color": "#ffffff", "weight": "600", "prefix": " "},
            {"label": "HR Status",     "width": 1.0, "key": "hr_status",          "type": "text"},
            {"label": "Highest Tier",  "width": 1.2, "key": "highest_tier_held",  "type": "pill", "pill_fn": tier_pill},
            {"label": "Days Dormant",  "width": 1.2, "key": "days_dormant",       "type": "text"},
            {"label": "Risk Score",    "width": 1.0, "key": "risk_score",         "type": "score", "thresholds": {"high": 70, "medium": 40}},
            {"label": "Damage Score",  "width": 1.0, "key": "damage_score",       "type": "score", "thresholds": {"high": 70, "medium": 40}},
            {"label": "Dormancy Score","width": 1.0, "key": "dormancy_score",     "type": "text"},
            {"label": "Risk Factors",  "width": 2.0, "key": "risk_factors",       "type": "text", "color": "#94a3b8"},
        ],
        key_prefix="risk_all",
        height=550,
    )

else:
    def generate_risk_report(risk_df, damage_df, dormancy_df, incidents_df, prevelage_df, ghost_acc_df, stale_token_df):
        today = datetime.now().strftime("%Y-%m-%d")
        total_identities = len(risk_df)
        high_risk_count = len(risk_df[risk_df["risk_score"] >= 60])
        high_risk_pct = (high_risk_count / total_identities) * 100 if total_identities else 0.0
        
        avg_risk = risk_df["risk_score"].mean()
        avg_damage = damage_df["damage_score"].mean()
        avg_dormancy = dormancy_df["dormancy_score"].mean()
        
        # Dormancy top user
        dormant_count = len(dormancy_df[dormancy_df["days_dormant"] >= 60])
        if not dormancy_df.empty:
            top_dormant_row = dormancy_df.sort_values("days_dormant", ascending=False).iloc[0]
            top_dormant_user = top_dormant_row["identity_name"]
            top_dormant_days = top_dormant_row["days_dormant"]
            top_dormant_priv = top_dormant_row["highiest_privilage"]
        else:
            top_dormant_user, top_dormant_days, top_dormant_priv = "N/A", 0, "N/A"
            
        # Remediation backlog top user/violation
        total_incidents = len(incidents_df)
        if not incidents_df.empty:
            top_violation_row = incidents_df.iloc[0]
            top_violation_desc = top_violation_row["description"]
            top_violation_user = top_violation_row.get("full_name", "N/A")
        else:
            top_violation_desc, top_violation_user = "N/A", "N/A"
            
        report = []
        report.append(f"IDENTITY RISK SUMMARY — {today}")
        report.append("" * 36)
        report.append(f"Total Identities Assessed: {total_identities}")
        report.append(f"High-Risk Identities: {high_risk_count} ({high_risk_pct:.1f}%)")
        report.append(f"Orphaned/Ghost Accounts: {len(ghost_acc_df)}")
        report.append(f"Over-Privileged Roles: {len(prevelage_df)}")
        report.append(f"Stale Security Tokens: {len(stale_token_df)}")
        report.append(f"Alerts Clustered: {total_incidents} violations")
        report.append("")
        report.append("RISK METRICS OVERVIEW")
        report.append("-" * 21)
        report.append(f"Average Unified Risk Score: {avg_risk:.1f}/100")
        report.append(f"Average Privilege Damage Score: {avg_damage:.1f}/100")
        report.append(f"Average Inactivity Dormancy Score: {avg_dormancy:.1f}/100")
        report.append("")
        report.append("PLATFORM SECTION SUMMARY")
        report.append("-" * 24)
        report.append(f"- Dormancy: {dormant_count} identities are inactive for 60+ days. The top dormant user is {top_dormant_user} (dormant for {top_dormant_days} days, holding {top_dormant_priv}).")
        report.append(f"- Remediation Backlog: {total_incidents} active violations found. The top platform violation belongs to {top_violation_user}: {top_violation_desc}.")
        report.append("")
        report.append("CRITICAL FINDINGS (TOP 3 HIGHEST RISK)")
        report.append("-" * 38)
        
        top_3 = risk_df.head(3)
        for idx, (_, row) in enumerate(top_3.iterrows(), 1):
            name = row["identity_name"]
            score = row["risk_score"]
            tier = row["highest_tier_held"]
            days = row["days_dormant"]
            factors = row["risk_factors"]
            hr_status = row["hr_status"]
            
            report.append(f"{idx}. {name} (HR Status: {hr_status})")
            report.append(f"   Risk Score: {score:.1f}/100")
            
            issue_parts = []
            if tier:
                issue_parts.append(f"holds {tier} privileges")
            if pd.notna(days):
                issue_parts.append(f"inactive for {days} days")
            if factors:
                issue_parts.append(f"flagged factors: {factors}")
            
            issue_str = "; ".join(issue_parts)
            report.append(f"   Issue: {issue_str}")
            
            if "ghost_account" in factors:
                action = "Immediately disable all platform credentials and audit cross-platform access logs."
            elif "high_privilege" in factors and "dormant_account" in factors:
                action = "Disable/deprivilege inactive admin accounts, rotate credentials, and suspend access."
            elif "high_privilege" in factors:
                action = "Review role assignment justifications and enforce least privilege."
            elif "dormant_account" in factors:
                action = "Temporarily suspend inactive account or enforce credential rotation."
            else:
                action = "Audit platform login patterns and enforce key rotation policies."
                
            report.append(f"   Action: {action}")
            report.append("")
            
        return "\n".join(report)

    high_damage_score_acc = len(damage[damage['damage_score'] >= 60])
    Dorminant_acc = len(dormancy[dormancy['days_dormant'] >= 60])
    masthead("Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Open Incidents", f"{len(incidents)}", "All risk rules", delta_color="inverse")
    with col2:
        st.metric("High Risk accounts", f"{high_damage_score_acc}", "Action within 24h", delta_color="inverse")
    with col3:
        st.metric("Dorminant Identities", f"{Dorminant_acc}", "Inactive for 60 days", delta_color="inverse")
    with col4:
        st.metric("Identities Monitored", f"{total_identities}", "Active in Directory")

    # Executive Report Generator Button
    st.markdown("---")
    r_col1, r_col2 = st.columns([1.2, 3.8])
    with r_col1:
        if st.button(" GENERATE RISK REPORT", key="btn_gen_report", use_container_width=True):
            st.session_state["show_risk_report"] = True
        if st.session_state.get("show_risk_report", False):
            if st.button(" CLOSE REPORT", key="btn_close_report", use_container_width=True):
                st.session_state["show_risk_report"] = False
                st.rerun()
                
    if st.session_state.get("show_risk_report", False):
        report_text = generate_risk_report(risk_df, damage, dormancy, incidents, prevelage_df, ghost_acc, stale_token)
        st.text_area("Precise Executive Risk Summary", value=report_text, height=350)
        st.download_button(
            label="DOWNLOAD REPORT AS TEXTFILE",
            data=report_text,
            file_name=f"identity_risk_summary_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    
    # masthead("Overview")
    section_head("Top 10 Risk Identities", "Ranked by unified risk score (privilege dormancy)")
    
    top_risk = risk_df[:10].copy()
    
    def disable_status(row):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE human_identities
            SET hr_status = 'DISABLED'
            WHERE identity_id = ?
        """, (int(row['identity_id']),))
        conn.commit()
        conn.close()
        st.toast(f"Status disabled for identity: {row['identity_name']} (ID: {row['identity_id']})")
        st.rerun()

    inject_table_css()
    def risk_detail_html(row):
        return f"""
        <div style="font-family:'Inter',sans-serif; color:#cbd5e1; font-size:0.85rem; line-height:1.6;">
            <b style="color:#fff;">Full Risk Breakdown</b><br>
            Highest Tier Held: {row.get('highest_tier_held','—')}<br>
            Risk Factors: {row['risk_factors']}<br>
            Damage Score: <span style="color:#ef4444; font-weight:700;">{row['damage_score']}</span> &nbsp;|&nbsp;
            Dormancy Score: <span style="color:#f59e0b; font-weight:700;">{row['dormancy_score']}</span>
        </div>
        """
    render_data_table(
        df=top_risk,
        columns=[
            {"label": "Identity",  "width": 2.5, "key": "identity_name", "type": "text", "color": "#ffffff", "weight": "600", "prefix": " "},
            {"label": "HR Status", "width": 1.3, "key": "hr_status",     "type": "text"},
            {"label": "Risk",      "width": 1.0, "key": "risk_score",    "type": "score", "thresholds": {"high": 70, "medium": 40}},
            {"label": "Damage",    "width": 1.0, "key": "damage_score",  "type": "score", "thresholds": {"high": 70, "medium": 40}},
            {"label": "Dormancy",  "width": 1.0, "key": "dormancy_score","type": "text"},
            {"label": "Factors",   "width": 2.0, "key": "risk_factors",  "type": "text", "color": "#94a3b8"},
        ],
        actions=[
            {"label": "DISABLE STATUS", "key_suffix": "inv", "width": 1.4, "on_click": disable_status},
        ],
        key_prefix="risk_top10",
    )

    with st.expander("View Full Incident Table", expanded=False):
        st.markdown("### Privilege Creep")
        st.dataframe(prevelage_df)
        st.markdown("### Ghost Account")
        st.dataframe(ghost_acc)
        st.markdown("### Stale Token")
        st.dataframe(stale_token)