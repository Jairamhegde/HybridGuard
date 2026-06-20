"""
utils.py
--------
Shared helpers used across every page of the dashboard:
 - cached SQLite access
 - the classic / professional CSS theme
 - small reusable HTML components (KPI cards, severity pills, section headers)
"""

import os
import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = os.path.join(os.path.dirname(__file__), "identity_risk.db")

SEVERITY_COLORS = {
    "Critical": "#9b2226",
    "High": "#bb4d00",
    "Medium": "#8a6d00",
    "Low": "#2f5d3a",
}

TIER_COLORS = {
    "Tier0": "#9b2226",
    "Tier1": "#bb4d00",
    "Tier2": "#3a5a78",
}


@st.cache_data(ttl=300)
def load_table(name: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT * FROM {name}", conn)
    conn.close()
    return df


@st.cache_data(ttl=300)
def load_all():
    return {
        "dormancy": load_table("dormancy"),
        "damage": load_table("damage"),
        "incidents": load_table("incidents"),
    }


def inject_base_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
        }

        :root {
            --ink: #ffffff;
            --ink-soft: #94a3b8;
            --hairline: #1e2443;
            --panel: #111425;
            --bg: #080a11;
            --navy: #080a11;
            --navy-2: #5e5ce6;
            --gold: #38bdf8;
            --emerald: #30d158;
        }

        .stApp {
            background: var(--bg) !important;
            color: var(--ink) !important;
        }

        /* Hide default streamlit chrome for a cleaner, custom shell */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {background: transparent;}

        section[data-testid="stSidebar"] {
            background: #080a11 !important;
            border-right: 1px solid var(--hairline) !important;
        }
        section[data-testid="stSidebar"] * {
            color: #cbd5e1 !important;
        }
        section[data-testid="stSidebar"] hr {
            border-color: var(--hairline) !important;
        }

        .block-container {
            padding-top: 1.6rem;
            padding-bottom: 3rem;
            max-width: 1280px;
        }

        /* ---------- Sidebar Navigation (Screenshot style) ---------- */
        .sidebar-nav {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            padding: 0;
            margin-top: 1rem;
        }
        .nav-title {
            color: #4f5b7c !important;
            font-size: 0.72rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.12em !important;
            margin-bottom: 0.75rem !important;
            margin-top: 0.5rem !important;
        }
        .nav-item {
            display: block;
            background-color: #121526;
            color: #94a3b8 !important;
            border: 1px solid #1e2443;
            border-radius: 8px;
            padding: 0.7rem 1.1rem;
            text-decoration: none !important;
            font-size: 0.88rem;
            font-weight: 500;
            transition: all 0.2s ease-in-out;
            margin-bottom: 0.4rem;
        }
        .nav-item:hover {
            background-color: #161a35;
            color: #ffffff !important;
            border-color: #5e5ce6;
        }
        .nav-item.active {
            background-color: #161a35;
            color: #ffffff !important;
            border-color: #5e5ce6;
            box-shadow: 0 0 10px rgba(94, 92, 230, 0.15);
        }

        /* ---------- Masthead ---------- */
        .masthead {
            border-bottom: 1px solid var(--hairline);
            padding-bottom: 1rem;
            margin-bottom: 1.75rem;
            display: flex;
            justify-content: space-between;
            align-items: baseline;
        }
        .masthead-title {
            font-family: 'Inter', sans-serif;
            font-size: 1.85rem;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: 0.2px;
            margin: 0;
        }
        .masthead-sub {
            color: var(--ink-soft);
            font-size: 0.92rem;
            margin-top: 0.25rem;
        }
        .masthead-meta {
            text-align: right;
            color: #64748b;
            font-size: 0.82rem;
            line-height: 1.5;
        }

        /* ---------- Section headers ---------- */
        .section-head {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            margin: 2rem 0 1rem 0;
        }
        .section-head .bar {
            width: 4px;
            height: 1.25rem;
            background: var(--navy-2);
            display: inline-block;
            border-radius: 2px;
        }
        .section-head h3 {
            font-family: 'Inter', sans-serif;
            font-size: 1.25rem;
            font-weight: 700;
            color: #ffffff;
            margin: 0;
        }
        .section-note {
            color: var(--ink-soft);
            font-size: 0.88rem;
            margin: -0.4rem 0 1.2rem 0.65rem;
        }

        /* ---------- KPI cards ---------- */
        .kpi-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1rem;
            margin-bottom: 0.5rem;
        }
        .kpi-card {
            background: var(--panel);
            border: 1px solid var(--hairline);
            border-top: 3px solid var(--navy-2);
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .kpi-card.accent-critical { border-top-color: #ef4444; }
        .kpi-card.accent-high     { border-top-color: #f97316; }
        .kpi-card.accent-medium   { border-top-color: #eab308; }
        .kpi-card.accent-gold     { border-top-color: var(--gold); }
        .kpi-card.accent-green    { border-top-color: var(--emerald); }

        .kpi-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--ink-soft);
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        .kpi-value {
            font-family: 'Inter', sans-serif;
            font-size: 2.1rem;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.1;
        }
        .kpi-foot {
            margin-top: 0.6rem;
        }
        .kpi-foot-badge {
            display: inline-flex;
            align-items: center;
            background-color: rgba(48, 209, 88, 0.12);
            color: #30d158;
            border: 1px solid rgba(48, 209, 88, 0.22);
            border-radius: 6px;
            padding: 0.2rem 0.55rem;
            font-size: 0.72rem;
            font-weight: 600;
        }
        .kpi-foot-badge.down {
            background-color: rgba(239, 68, 68, 0.12);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.22);
        }

        /* ---------- Severity / tier pills ---------- */
        .pill {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            color: #ffffff;
        }

        /* ---------- Panel wrapper ---------- */
        .panel {
            background: var(--panel);
            border: 1px solid var(--hairline);
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .footnote {
            color: var(--ink-soft);
            font-size: 0.78rem;
            border-top: 1px solid var(--hairline);
            padding-top: 0.8rem;
            margin-top: 2.5rem;
        }

        /* Streamlit inputs and dropdowns dark theme tweaks */
        div[data-baseweb="select"] > div {
            background-color: #121526 !important;
            color: #ffffff !important;
            border-color: #1e2443 !important;
        }
        div[data-baseweb="select"] * {
            color: #ffffff !important;
        }
        input[data-testid="stTextInputBase"] {
            background-color: #121526 !important;
            color: #ffffff !important;
            border-color: #1e2443 !important;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--hairline);
            border-radius: 8px;
        }

        /* Metric widget tweak (native st.metric) */
        [data-testid="stMetric"] {
            background-color: #121526 !important;
            border: 1px solid #1e2443 !important;
            border-radius: 12px !important;
            padding: 1rem 1.25rem !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        }
        [data-testid="stMetricLabel"] > div {
            color: #94a3b8 !important;
            font-size: 0.72rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
            font-weight: 600 !important;
            margin-bottom: 0.25rem !important;
        }
        [data-testid="stMetricValue"] > div {
            color: #ffffff !important;
            font-size: 2.1rem !important;
            font-weight: 700 !important;
        }
        [data-testid="stMetricDelta"] > div {
            font-size: 0.72rem !important;
            font-weight: 600 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def masthead(page_label: str):
    st.markdown(
        f"""
        <div class="masthead">
            <div>
                <p class="masthead-title">Identity Risk &amp; Threat Analytics</p>
                <p class="masthead-sub">Cross-Platform Privilege, Dormancy &amp; Damage Intelligence &nbsp;·&nbsp; {page_label}</p>
            </div>
            <div class="masthead-meta">
                Platforms monitored: AD &middot; AWS IAM &middot; Okta<br>
                Snapshot date: 20 Jun 2026
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_head(title: str, note: str = ""):
    st.markdown(
        f"""
        <div class="section-head"><span class="bar"></span><h3>{title}</h3></div>
        {f'<p class="section-note">{note}</p>' if note else ''}
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label, value, foot="", accent="navy"):
    accent_class = f"accent-{accent}" if accent != "navy" else ""
    foot_html = ""
    if foot:
        # Decide badge class (red/down if negative/warning keyword, green/up otherwise)
        if any(w in foot.lower() for w in ["down", "critical", "high", "open", "stale"]):
            badge_class = "kpi-foot-badge down"
            arrow = "▼"
        else:
            badge_class = "kpi-foot-badge"
            arrow = "▲"
        foot_html = f'<div class="kpi-foot"><span class="{badge_class}">{arrow} {foot}</span></div>'

    return f'<div class="kpi-card {accent_class}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{foot_html}</div>'


def kpi_row(cards_html: list):
    st.markdown(f'<div class="kpi-row">{"".join(cards_html)}</div>', unsafe_allow_html=True)


def severity_pill(sev: str) -> str:
    color = SEVERITY_COLORS.get(sev, "#4a5568")
    return f'<span class="pill" style="background:{color}">{sev.upper()}</span>'


def tier_pill(tier: str) -> str:
    color = TIER_COLORS.get(tier, "#4a5568")
    return f'<span class="pill" style="background:{color}">{tier}</span>'


def render_html_table(df: pd.DataFrame, pill_cols=None, max_rows=None):
    """Render a DataFrame as a classic bordered HTML table styled for the premium dark mode."""
    pill_cols = pill_cols or {}
    d = df.copy()
    if max_rows:
        d = d.head(max_rows)

    headers = "".join(f"<th>{c.replace('_', ' ').title()}</th>" for c in d.columns)
    rows_html = ""
    for _, r in d.iterrows():
        cells = []
        for c in d.columns:
            val = r[c]
            if c in pill_cols:
                val = pill_cols[c](val)
            cells.append(f"<td>{val}</td>")
        rows_html += f"<tr>{''.join(cells)}</tr>"

    table_html = f"""
<style>
.classic-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.86rem;
    color: #cbd5e1;
}}
.classic-table th {{
    text-align: left;
    background: #121526;
    color: #94a3b8;
    font-weight: 700;
    font-size: 0.74rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: 0.75rem 0.85rem;
    border-bottom: 2px solid #1e2443;
}}
.classic-table td {{
    padding: 0.7rem 0.85rem;
    border-bottom: 1px solid #1e2443;
    color: #cbd5e1;
}}
.classic-table tr:hover td {{
    background: #181d36;
}}
</style>
<table class="classic-table">
<thead><tr>{headers}</tr></thead>
<tbody>{rows_html}</tbody>
</table>
"""
    st.markdown(table_html, unsafe_allow_html=True)


PLOTLY_TEMPLATE = "plotly_dark"
NAVY = "#5e5ce6"
GOLD = "#38bdf8"
SLATE = "#94a3b8"
CRIT = "#ef4444"
HIGH = "#f97316"
MED = "#eab308"
LOW = "#10b981"

SEVERITY_ORDER = ["Critical", "High", "Medium", "Low"]
TIER_ORDER = ["Tier0", "Tier1", "Tier2"]
