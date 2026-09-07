from backend.db_connection import connect_db
import pandas as pd


def generate_security_incidents():
    conn = connect_db()
    cursor = conn.cursor()

    # Ensure platform and elevated_tier columns exist in security_incidents table
    try:
        cursor.execute("PRAGMA table_info(security_incidents);")
        existing_columns = [col[1] for col in cursor.fetchall()]
        if "platform" not in existing_columns:
            cursor.execute("ALTER TABLE security_incidents ADD COLUMN platform TEXT;")
        if "elevated_tier" not in existing_columns:
            cursor.execute("ALTER TABLE security_incidents ADD COLUMN elevated_tier TEXT;")
        conn.commit()
    except Exception as e:
        print(f"Error ensuring security_incidents columns: {e}")

    cursor.execute("DELETE FROM security_incidents;")

    ghost_account_insert = """
    INSERT INTO security_incidents (identity_id, incident_type, severity,platform, description)
    SELECT 
        h.identity_id,
        'Ghost Account' AS incident_type,
        'CRITICAL' AS severity,
        p.platform_name,
        'User ' || h.full_name || ' is marked DISABLED in HR, but still has an ACTIVE ' || p.platform_name || ' account.' AS description
    FROM human_identities h
    JOIN accounts a ON h.identity_id = a.identity_id
    JOIN platforms p ON a.platform_id = p.platform_id
    WHERE h.hr_status = 'DISABLED' AND a.account_status = 'ACTIVE';
    """

    

    privilege_creep_insert = """
    INSERT INTO security_incidents (identity_id, incident_type, severity, platform, description, elevated_tier)
        SELECT DISTINCT
            h.identity_id,
            'Privilege Creep' AS incident_type,
            'HIGH' AS severity,
            p.platform_name,
            'User ' || h.full_name || ' is a standard ' || hr_role.normalized_tier || ' employee, but holds elevated ' || sys_role.normalized_tier || ' access (' || sys_role.raw_role_name || ') in ' || p.platform_name || '.' AS description,
            sys_role.normalized_tier AS elevated_tier
        FROM human_identities h
        JOIN accounts hr_acc ON h.identity_id = hr_acc.identity_id AND hr_acc.platform_id = 1
        JOIN account_role_mapping hr_map ON hr_acc.account_id = hr_map.account_id
        JOIN role_definitions hr_role ON hr_map.role_id = hr_role.role_id
        JOIN accounts sys_acc ON h.identity_id = sys_acc.identity_id AND sys_acc.platform_id != 1
        JOIN account_role_mapping sys_map ON sys_acc.account_id = sys_map.account_id
        JOIN role_definitions sys_role ON sys_map.role_id = sys_role.role_id
        JOIN platforms p ON sys_acc.platform_id = p.platform_id

        WHERE hr_acc.account_status = 'ACTIVE' 
        AND sys_acc.account_status = 'ACTIVE' 

        AND (
            (hr_role.normalized_tier = 'Tier 2' AND sys_role.normalized_tier IN ('Tier 0', 'Tier 1'))
        OR (hr_role.normalized_tier = 'Tier 1' AND sys_role.normalized_tier = 'Tier 0')
        );
    """

    stale_token_insert = """
    INSERT INTO security_incidents (identity_id, incident_type, severity, platform, description)
    SELECT 
        h.identity_id,
        'Stale Security Token' AS incident_type,
        'MEDIUM' AS severity,
        p.platform_name,
        'Active ' || p.platform_name || ' account for ' || h.full_name || ' has no record of token rotation.' AS description
    FROM accounts a
    JOIN human_identities h ON a.identity_id = h.identity_id
    JOIN platforms p ON a.platform_id = p.platform_id
    WHERE a.account_status = 'ACTIVE' 
    AND (a.token_rotated_date IS NULL OR a.token_rotated_date = '')
    AND p.platform_name != 'AD';
    """

    privilege_creep_select = """
    SELECT DISTINCT
        h.identity_id,
        'Privilege Creep' AS incident_type,
        'HIGH' AS severity,
        h.full_name,
        hr_role.normalized_tier AS "Normalized Tier",
        sys_role.raw_role_name AS "Elevated Role",
        p.platform_name AS "On Platform"
    FROM human_identities h
    JOIN accounts hr_acc ON h.identity_id = hr_acc.identity_id AND hr_acc.platform_id = 1
    JOIN account_role_mapping hr_map ON hr_acc.account_id = hr_map.account_id
    JOIN role_definitions hr_role ON hr_map.role_id = hr_role.role_id
    JOIN accounts sys_acc ON h.identity_id = sys_acc.identity_id AND sys_acc.platform_id != 1
    JOIN account_role_mapping sys_map ON sys_acc.account_id = sys_map.account_id
    JOIN role_definitions sys_role ON sys_map.role_id = sys_role.role_id
    JOIN platforms p ON sys_acc.platform_id = p.platform_id
    WHERE (hr_role.normalized_tier = 'Tier 2' AND sys_role.normalized_tier IN ('Tier 0', 'Tier 1'))
       OR (hr_role.normalized_tier = 'Tier 1' AND sys_role.normalized_tier = 'Tier 0');
    """

    ghost_account_select = """
    SELECT DISTINCT
        h.identity_id,
        'Ghost Account' AS incident_type,
        'CRITICAL' AS severity,
        h.full_name,
        h.hr_status AS "HR Status",
        a.account_status AS "Account Status",
        p.platform_name AS "On Platform"
    FROM human_identities h
    JOIN accounts a ON h.identity_id = a.identity_id
    JOIN platforms p ON a.platform_id = p.platform_id
    WHERE h.hr_status = 'DISABLED' AND a.account_status = 'ACTIVE';
    """

    stale_token_select = """
    SELECT DISTINCT
        h.identity_id,
        'Stale Security Token' AS incident_type,
        'MEDIUM' AS severity,
        h.full_name,
        p.platform_name AS "On Platform",
        COALESCE(a.token_rotated_date, a.token_created_date) AS "Last Token Date",
        CASE 
            WHEN COALESCE(a.token_rotated_date, a.token_created_date) IS NULL THEN NULL
            ELSE CAST(julianday('now') - julianday(COALESCE(a.token_rotated_date, a.token_created_date)) AS INTEGER)
        END AS "Days Since Rotation",
        CASE 
            WHEN COALESCE(a.token_rotated_date, a.token_created_date) IS NULL THEN 'Expired'
            WHEN CAST(julianday('now') - julianday(COALESCE(a.token_rotated_date, a.token_created_date)) AS INTEGER) > 30 
            THEN 'Expired' 
            ELSE 'Valid' 
        END AS "Token Status"
    FROM accounts a
    JOIN human_identities h ON a.identity_id = h.identity_id
    JOIN platforms p ON a.platform_id = p.platform_id
    WHERE a.account_status = 'ACTIVE' 
    AND (a.token_rotated_date IS NULL OR a.token_rotated_date = '')
    AND p.platform_name != 'AD';
    """

    cursor.execute(ghost_account_insert)
    print(f"Detected {cursor.rowcount} Ghost Account violations.")
    cursor.execute(privilege_creep_insert)
    cursor.execute(stale_token_insert)
    conn.commit()

    prevelage_df = pd.read_sql_query(privilege_creep_select, conn)
    ghost_acc = pd.read_sql_query(ghost_account_select, conn)
    stale_token = pd.read_sql_query(stale_token_select, conn)
    incidents_df = pd.concat([prevelage_df, ghost_acc, stale_token], ignore_index=True)
    incidents_df = pd.read_sql_query(
        "SELECT identity_id, incident_type, severity, platform, description, elevated_tier FROM security_incidents ORDER BY severity ASC", conn
    )

    conn.close()
    return incidents_df, prevelage_df, ghost_acc, stale_token


def damage_score():
    conn = connect_db()
    damage_query = """
    SELECT 
        identity_id,
        identity_name,
        hr_status,
        days_dormant,
        highest_tier_held,
        CASE 
            WHEN hr_status = 'DISABLED' THEN 0
            WHEN highest_tier_held = 'Tier 0' THEN 100
            WHEN highest_tier_held = 'Tier 1' THEN 50
            WHEN highest_tier_held = 'Tier 2' THEN 10
            ELSE 0 
        END AS damage_score
    FROM live_privileged_watchlist
    ORDER BY damage_score DESC, days_dormant DESC;
    """
    df = pd.read_sql_query(damage_query, conn)
    print(f"Detected {len(df)} Damage Threat violations.")
    conn.commit()
    conn.close()
    return df


def dormancy_threat():
    conn = connect_db()
    dormancy_query = """
    SELECT 
        identity_id,
        identity_name,
        hr_status,
        days_dormant,
        highest_tier_held AS highiest_privilage,
        last_login_date,
        CASE 
            WHEN days_dormant IS NULL THEN 100
            WHEN days_dormant >= 90 THEN 100
            WHEN days_dormant >= 60 THEN 50
            WHEN days_dormant >= 30 THEN 10
            ELSE 0 
        END AS dormancy_score
    FROM live_privileged_watchlist
    ORDER BY dormancy_score DESC, days_dormant DESC;
    """
    df = pd.read_sql_query(dormancy_query, conn)
    print(f"Detected {len(df)} Dormancy Threat violations.")
    conn.commit()
    conn.close()
    return df


def calculate_risk_score(damage_df, dormancy_df):

    merged = damage_df.merge(
        dormancy_df[["identity_id", "dormancy_score", "last_login_date"]],
        on="identity_id",
        how="left"
    )
    
    merged["risk_score"] = (
        merged["damage_score"] * 0.4 +
        merged["dormancy_score"] * 0.3 +
        merged["hr_status"].apply(lambda status: 100.0 if status == "DISABLED" else 0.0) * 0.3
    )
    
    merged["risk_factors"] = merged.apply(lambda row: ", ".join([
        f for f in [
            "high_privilege" if row["damage_score"] >= 50 else "",
            "dormant_account" if row["dormancy_score"] >= 50 else "",
            "ghost_account" if row["hr_status"] == "DISABLED" else ""
        ] if f
    ]), axis=1)
    
    merged = merged.sort_values("risk_score", ascending=False)
    return merged


def get_all_details(identity_id):
    conn = connect_db()
    account_status = """
    SELECT
        h.identity_id,
        h.full_name,
        h.hr_status,
        p.platform_name,
        a.account_status,
    FROM human_identities h
    JOIN accounts a ON h.identity_id = a.identity_id
    JOIN platforms p ON a.platform_id = p.platform_id
    where h.identity_id = identity_id;
    """
 



    df = pd.read_sql_query(account_status, conn)
    print(f"Detected {len(df)} All Identities.")
    conn.commit()
    conn.close()
    return df


def disable_hr_status(identity_id: int):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE human_identities
        SET hr_status = 'DISABLED'
        WHERE identity_id = ?
    """, (identity_id,))
    conn.commit()
    conn.close()

def revoke_account_access(identity_id: int, platform_name: str, incident_type: str = None):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE accounts 
        SET account_status = 'DISABLED' 
        WHERE identity_id = ?
        AND platform_id = (SELECT platform_id FROM platforms WHERE platform_name = ?)
    """, (identity_id, platform_name))
    if incident_type:
        cursor.execute("""
            DELETE FROM security_incidents 
            WHERE incident_type = ? AND platform = ? AND identity_id = ?
        """, (incident_type, platform_name, identity_id))
    conn.commit()
    conn.close()

def rotate_account_token(identity_id: int, platform_name: str):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE accounts
        SET token_rotated_date = datetime("now")
        WHERE identity_id = ? AND platform_id = (SELECT platform_id FROM platforms WHERE platform_name = ?)
    """, (identity_id, platform_name))
    conn.commit()
    conn.close()

def revoke_account_tier(identity_id: int, platform_name: str, elevated_tier: str):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM account_role_mapping
        WHERE account_id = (
            SELECT account_id FROM accounts 
            WHERE identity_id = ? AND platform_id = (SELECT platform_id FROM platforms WHERE platform_name = ?)
        )
        AND role_id IN (
            SELECT role_id FROM role_definitions WHERE normalized_tier = ?
        )
    """, (identity_id, platform_name, elevated_tier))
    conn.commit()
    conn.close()

def generate_executive_report():
    from datetime import datetime
    incidents_df, prevelage_df, ghost_acc_df, stale_token_df = generate_security_incidents()
    damage_df = damage_score()
    dormancy_df = dormancy_threat()
    risk_df = calculate_risk_score(damage_df, dormancy_df)

    today = datetime.now().strftime("%Y-%m-%d")
    total_identities = len(risk_df)
    high_risk_count = len(risk_df[risk_df["risk_score"] >= 60])
    high_risk_pct = (high_risk_count / total_identities) * 100 if total_identities else 0.0
    
    avg_risk = risk_df["risk_score"].mean()
    avg_damage = damage_df["damage_score"].mean()
    avg_dormancy = dormancy_df["dormancy_score"].mean()
    
    dormant_count = len(dormancy_df[dormancy_df["days_dormant"] >= 60])
    if not dormancy_df.empty:
        top_dormant_row = dormancy_df.sort_values("days_dormant", ascending=False).iloc[0]
        top_dormant_user = top_dormant_row["identity_name"]
        top_dormant_days = top_dormant_row["days_dormant"]
        top_dormant_priv = top_dormant_row["highiest_privilage"]
    else:
        top_dormant_user, top_dormant_days, top_dormant_priv = "N/A", 0, "N/A"
        
    total_incidents = len(incidents_df)
    if not incidents_df.empty:
        top_violation_row = incidents_df.iloc[0]
        top_violation_desc = top_violation_row["description"]
        top_violation_user = top_violation_row.get("full_name", "N/A")
    else:
        top_violation_desc, top_violation_user = "N/A", "N/A"
        
    report = []
    report.append(f"IDENTITY RISK SUMMARY — {today}")
    report.append("-" * 36)
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

def get_identity_lineage(identity_id: int):
    conn = connect_db()
    cursor = conn.cursor()

    # Master HR identity details
    cursor.execute("""
        SELECT identity_id, full_name, email, hr_status
        FROM human_identities
        WHERE identity_id = ?
    """, (identity_id,))
    identity_row = cursor.fetchone()

    if not identity_row:
        conn.close()
        return None

    identity_info = {
        "identity_id": identity_row[0],
        "full_name": identity_row[1],
        "email": identity_row[2],
        "hr_status": identity_row[3],
    }

    # Fetch risk scores from live_privileged_watchlist if available
    cursor.execute("""
        SELECT days_dormant, highest_tier_held
        FROM live_privileged_watchlist
        WHERE identity_id = ?
    """, (identity_id,))
    watchlist_row = cursor.fetchone()
    if watchlist_row:
        identity_info["days_dormant"] = watchlist_row[0]
        identity_info["highest_tier_held"] = watchlist_row[1]
    else:
        identity_info["days_dormant"] = 0
        identity_info["highest_tier_held"] = "Tier 2"

    # Compute risk score
    damage_df = damage_score()
    dormancy_df = dormancy_threat()
    risk_df = calculate_risk_score(damage_df, dormancy_df)
    match_risk = risk_df[risk_df["identity_id"] == identity_id]
    if not match_risk.empty:
        r = match_risk.iloc[0]
        identity_info["risk_score"] = float(r["risk_score"])
        identity_info["damage_score"] = float(r["damage_score"])
        identity_info["dormancy_score"] = float(r["dormancy_score"])
        identity_info["risk_factors"] = str(r["risk_factors"])
    else:
        identity_info["risk_score"] = 0.0
        identity_info["damage_score"] = 0.0
        identity_info["dormancy_score"] = 0.0
        identity_info["risk_factors"] = ""

    # Fetch platform accounts
    cursor.execute("""
        SELECT a.account_id, p.platform_name, a.platform_username, a.account_status,
               a.token_created_date, a.token_rotated_date, a.last_login_date
        FROM accounts a
        JOIN platforms p ON a.platform_id = p.platform_id
        WHERE a.identity_id = ?
    """, (identity_id,))
    accounts_rows = cursor.fetchall()

    accounts = []
    for acc in accounts_rows:
        acc_id, platform_name, username, status, created_date, rotated_date, last_login = acc
        
        # Roles for this account
        cursor.execute("""
            SELECT r.raw_role_name, r.normalized_tier
            FROM account_role_mapping arm
            JOIN role_definitions r ON arm.role_id = r.role_id
            WHERE arm.account_id = ?
        """, (acc_id,))
        roles_rows = cursor.fetchall()
        roles = [{"raw_role_name": r[0], "normalized_tier": r[1]} for r in roles_rows]

        accounts.append({
            "account_id": acc_id,
            "platform_name": platform_name,
            "username": username,
            "account_status": status,
            "token_created_date": created_date,
            "token_rotated_date": rotated_date,
            "last_login_date": last_login,
            "roles": roles
        })

    # Fetch security incidents for this identity
    cursor.execute("""
        SELECT incident_type, severity, platform, description, elevated_tier
        FROM security_incidents
        WHERE identity_id = ?
    """, (identity_id,))
    incident_rows = cursor.fetchall()
    incidents = [{
        "incident_type": inc[0],
        "severity": inc[1],
        "platform": inc[2],
        "description": inc[3],
        "elevated_tier": inc[4]
    } for inc in incident_rows]

    conn.close()
    return {
        "identity": identity_info,
        "accounts": accounts,
        "incidents": incidents
    }


def get_graph_data(limit: int = 15):
    damage_df = damage_score()
    dormancy_df = dormancy_threat()
    risk_df = calculate_risk_score(damage_df, dormancy_df)
    top_identities = risk_df.head(limit)

    conn = connect_db()
    cursor = conn.cursor()

    nodes = []
    links = []
    added_nodes = set()

    for _, id_row in top_identities.iterrows():
        identity_id = int(id_row["identity_id"])
        user_node_id = f"user_{identity_id}"
        
        if user_node_id not in added_nodes:
            added_nodes.add(user_node_id)
            nodes.append({
                "id": user_node_id,
                "label": id_row["identity_name"],
                "type": "identity",
                "identity_id": identity_id,
                "status": id_row["hr_status"],
                "risk_score": float(id_row["risk_score"]),
                "tier": id_row["highest_tier_held"]
            })

        # Fetch accounts for this identity
        cursor.execute("""
            SELECT a.account_id, p.platform_name, a.platform_username, a.account_status
            FROM accounts a
            JOIN platforms p ON a.platform_id = p.platform_id
            WHERE a.identity_id = ?
        """, (identity_id,))
        acc_rows = cursor.fetchall()

        for acc in acc_rows:
            acc_id, p_name, username, acc_status = acc
            plat_node_id = f"acc_{acc_id}"

            if plat_node_id not in added_nodes:
                added_nodes.add(plat_node_id)
                nodes.append({
                    "id": plat_node_id,
                    "label": f"{p_name}: {username}",
                    "type": "account",
                    "platform": p_name,
                    "status": acc_status
                })

            links.append({
                "source": user_node_id,
                "target": plat_node_id,
                "label": "owns"
            })

            # Fetch roles for account
            cursor.execute("""
                SELECT r.role_id, r.raw_role_name, r.normalized_tier
                FROM account_role_mapping arm
                JOIN role_definitions r ON arm.role_id = r.role_id
                WHERE arm.account_id = ?
            """, (acc_id,))
            role_rows = cursor.fetchall()

            for r_row in role_rows:
                r_id, raw_role, tier = r_row
                role_node_id = f"role_{p_name}_{r_id}"

                if role_node_id not in added_nodes:
                    added_nodes.add(role_node_id)
                    nodes.append({
                        "id": role_node_id,
                        "label": f"{raw_role} ({tier})",
                        "type": "role",
                        "platform": p_name,
                        "tier": tier
                    })

                links.append({
                    "source": plat_node_id,
                    "target": role_node_id,
                    "label": "assigned"
                })

    conn.close()
    return {"nodes": nodes, "links": links}

generate_security_incidents()
