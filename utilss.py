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

def load_table(name: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT * FROM {name}", conn)
    conn.close()
    return df

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

        /* ---------- Action button styling ---------- */
        .stButton > button {
            background-color: #151b3b;
            color: #cbd5e1;
            border: 1px solid #2a3158;
            border-radius: 8px;
            font-size: 0.80rem;
            font-family: 'Inter', sans-serif;
            padding: 0.25rem 0.8rem;
            transition: all 0.2s ease;
        }
        .stButton > button:hover {
            border-color: #ef4444;
            color: #ef4444;
            background-color: rgba(239,68,68,0.08);
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
    if not sev or pd.isna(sev):
        return f'<span class="pill" style="background:#4a5568">—</span>'
    sev_str = str(sev).upper()
    color = SEVERITY_COLORS.get(sev_str.title(), "#4a5568")
    return f'<span class="pill" style="background:{color}">{sev_str}</span>'

def tier_pill(tier: str) -> str:
    if not tier or pd.isna(tier):
        return f'<span class="pill" style="background:#4a5568">—</span>'
    tier_str = str(tier)
    key = tier_str.replace(" ", "")
    color = TIER_COLORS.get(key, "#4a5568")
    return f'<span class="pill" style="background:{color}">{tier_str}</span>'


def render_html_table(df: pd.DataFrame, pill_cols=None, max_rows=None, height: int = 400):
    """Render a DataFrame as a classic bordered HTML table styled for the premium dark mode.
    The table body scrolls vertically inside a fixed-height container; header stays pinned.
    """
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
    .table-scroll-wrapper {{
        height: {height}px;
        overflow-y: auto;
        overflow-x: auto;
        border-radius: 8px;
        border: 1px solid #1e2443;
    }}
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
        position: sticky;
        top: 0;
        z-index: 1;
    }}
    .classic-table td {{
        padding: 0.7rem 0.85rem;
        border-bottom: 1px solid #1e2443;
        color: #cbd5e1;
        white-space: nowrap;
    }}
    .classic-table tr:hover td {{
        background: #181d36;
    }}
    </style>
    <div class="table-scroll-wrapper">
    <table class="classic-table">
    <thead><tr>{headers}</tr></thead>
    <tbody>{rows_html}</tbody>
    </table>
    </div>
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

def inject_table_css():
    """Injects button styling for the data table action buttons."""
    st.markdown("""
    <style>
    /* Action button styling for data tables */
    div[data-testid="stHorizontalBlock"] .stButton > button {
        background-color: #151b3b;
        color: #cbd5e1;
        border: 1px solid #2a3158;
        border-radius: 8px;
        font-size: 0.80rem;
        padding: 0.25rem 0.8rem;
        width: 100%;
    }
    div[data-testid="stHorizontalBlock"] .stButton > button:hover {
        border-color: #ef4444;
        color: #ef4444;
        background-color: rgba(239,68,68,0.08);
    }
    </style>
    """, unsafe_allow_html=True)

def _styled_span(text, color="#cbd5e1", weight="500", size=None):
    size_css = f"font-size:{size};" if size else ""
    return f"<span style='color:{color}; font-weight:{weight}; {size_css}'>{text}</span>"

def _render_cell(row, col_def):
    key = col_def["key"]
    value = row[key]
    cell_type = col_def.get("type", "text")

    if cell_type == "text":
        color = col_def.get("color", "#cbd5e1")
        weight = col_def.get("weight", "500")
        prefix = col_def.get("prefix", "")
        display_val = "—" if (pd.isna(value) or value is None or value == "") else str(value)
        return f"{prefix}{_styled_span(display_val, color=color, weight=weight)}"

    if cell_type == "score":
        thresholds = col_def.get("thresholds", {})
        if pd.isna(value) or value is None:
            return _styled_span("—", color="#94a3b8", weight="500")
        try:
            val_num = float(value)
        except (ValueError, TypeError):
            val_num = 0.0
        if val_num >= thresholds.get("high", 70):
            color = "#ef4444"
        elif val_num >= thresholds.get("medium", 40):
            color = "#f59e0b"
        else:
            color = "#22c55e"
        return _styled_span(value, color=color, weight="700")

    if cell_type == "pill":
        pill_fn = col_def["pill_fn"]
        return pill_fn(value)

    if cell_type == "custom":
        return col_def["render_fn"](row)

    return _styled_span(value)


def render_data_table(df, columns, actions=None, key_prefix="dt", expandable=False, detail_fn=None, height=350):
    """Renders a styled data table with pagination and optional action buttons.

    Architecture (fixes infinite rerender loop):
    - Data cells → single HTML string per row  (eliminates per-cell st.columns / st.markdown calls)
    - Action buttons → native st.button        (required for on_click callbacks)
    - Container → st.container(border=True) WITHOUT height  (eliminates scroll-JS rerender trigger)
    """
    actions = actions or []

    if df.empty:
        st.markdown(
            "<p style='color:#94a3b8;font-family:Inter,sans-serif;padding:0.5rem 0;'>"
            "No records found.</p>",
            unsafe_allow_html=True,
        )
        return

    # ── Pagination ─────────────────────────────────────────────────────────
    limit = 10
    total_rows = len(df)
    if total_rows > limit:
        num_pages = (total_rows - 1) // limit + 1
        pc1, pc2 = st.columns([4, 1])
        with pc2:
            page_num = st.selectbox(
                "Page",
                options=list(range(1, num_pages + 1)),
                key=f"_pg_{key_prefix}",
                label_visibility="collapsed",
            )
        with pc1:
            s = (page_num - 1) * limit + 1
            e = min(total_rows, page_num * limit)
            st.markdown(
                f"<p style='color:#94a3b8;font-size:0.82rem;margin:6px 0;"
                f"font-family:Inter,sans-serif;'>Showing "
                f"<b style='color:#cbd5e1'>{s}–{e}</b> of "
                f"<b style='color:#cbd5e1'>{total_rows}</b>"
                f"&nbsp;·&nbsp;Page {page_num}/{num_pages}</p>",
                unsafe_allow_html=True,
            )
        df_page = df.iloc[(page_num - 1) * limit : page_num * limit]
    else:
        df_page = df

    # ── Column proportional widths ──────────────────────────────────────────
    total_data_w = sum(c["width"] for c in columns)
    fracs = [c["width"] / total_data_w for c in columns]

    has_actions = bool(actions)
    if has_actions:
        layout_widths = [total_data_w] + [a["width"] for a in actions]

    # ── Table container – border only, NO height (eliminates scroll-JS loop) ─
    try:
        outer = st.container(border=True)
    except TypeError:
        outer = st.container()

    with outer:
        # ── Header (1 HTML call, zero layout widgets) ────────────────────────
        header_cells = "".join(
            f'<span style="flex:{frac:.4f};min-width:0;padding:6px 10px;'
            f'color:#94a3b8;font-size:0.74rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:0.04em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
            f'{c["label"]}</span>'
            for c, frac in zip(columns, fracs)
        )
        header_html = f'<div style="display:flex;border-bottom:2px solid #1e2443;padding:2px 0;background:transparent;">{header_cells}</div>'
        if has_actions:
            h_cols = st.columns(layout_widths)
            h_cols[0].markdown(header_html, unsafe_allow_html=True)
            for h_col in h_cols[1:]:
                h_col.markdown(
                    f'<div style="border-bottom:2px solid #1e2443;height:28px;"></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(header_html, unsafe_allow_html=True)

        # ── Data rows ────────────────────────────────────────────────────────
        for idx, row in df_page.iterrows():
            # All data cells → one HTML string (NO per-cell Streamlit widget calls)
            cells_html = "".join(
                f'<span style="flex:{frac:.4f};min-width:0;padding:8px 10px;'
                f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'
                f'{_render_cell(row, c)}</span>'
                for c, frac in zip(columns, fracs)
            )
            row_div = (
                f'<div style="display:flex;align-items:center;'
                f'min-height:42px;border-bottom:1px solid #1e2443;">'
                f'{cells_html}</div>'
            )

            if has_actions:
                # 1 st.columns call per row: [HTML data block | action button(s)]
                cols = st.columns(layout_widths)
                cols[0].markdown(row_div, unsafe_allow_html=True)
                for action, col in zip(actions, cols[1:]):
                    lbl = action["label"](row) if callable(action["label"]) else action["label"]
                    col.button(
                        lbl,
                        key=f"{key_prefix}_{action['key_suffix']}_{idx}",
                        on_click=action["on_click"],
                        args=(row,),
                    )
            else:
                st.markdown(row_div, unsafe_allow_html=True)