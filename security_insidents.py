from backend.db_connection import connect_db
import pandas as pd
def generate_security_incidents():
    conn = connect_db()
    cursor = conn.cursor()

    # 1. Create the Incidents Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS security_incidents (
        incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
        identity_id INTEGER,
        incident_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT DEFAULT 'OPEN',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (identity_id) REFERENCES human_identities(identity_id)
    );
    """)
    # Clear out old incidents so we don't duplicate them if we run the script twice
    cursor.execute("DELETE FROM security_incidents;") 

    ghost_account_query = """
    INSERT INTO security_incidents (identity_id, incident_type, severity, description)
    SELECT 
        h.identity_id,
        'Ghost Account' AS incident_type,
        'CRITICAL' AS severity,
        'User ' || h.full_name || ' is marked DISABLED in HR, but still has an ACTIVE ' || p.platform_name || ' account.' AS description
    FROM human_identities h
    JOIN accounts a ON h.identity_id = a.identity_id
    JOIN platforms p ON a.platform_id = p.platform_id
    WHERE h.hr_status = 'DISABLED' AND a.account_status = 'ACTIVE';
    """
    cursor.execute(ghost_account_query)
    print(f"Detected {cursor.rowcount} Ghost Account violations.")

    # ---------------------------------------------------------
    # THREAT 2: PRIVILEGE CREEP (HIGH)
    # Employee is a standard 'Tier 2' User, but holds 'Tier 0' or 'Tier 1' IT access
    # ---------------------------------------------------------
    privilege_creep_query = """
    INSERT INTO security_incidents (identity_id, incident_type, severity, description)
    SELECT DISTINCT
        h.identity_id,
        'Privilege Creep' AS incident_type,
        'HIGH' AS severity,
        'User ' || h.full_name || ' is a standard Tier 2 employee, but holds elevated ' || sys_role.normalized_tier || ' access (' || sys_role.raw_role_name || ') in ' || p.platform_name || '.' AS description
    FROM human_identities h
    JOIN accounts hr_acc ON h.identity_id = hr_acc.identity_id AND hr_acc.platform_id = 1
    JOIN account_role_mapping hr_map ON hr_acc.account_id = hr_map.account_id
    JOIN role_definitions hr_role ON hr_map.role_id = hr_role.role_id
    JOIN accounts sys_acc ON h.identity_id = sys_acc.identity_id AND sys_acc.platform_id != 1
    JOIN account_role_mapping sys_map ON sys_acc.account_id = sys_map.account_id
    JOIN role_definitions sys_role ON sys_map.role_id = sys_role.role_id
    JOIN platforms p ON sys_acc.platform_id = p.platform_id
    WHERE hr_role.normalized_tier = 'Tier 2' 
    AND sys_role.normalized_tier IN ('Tier 0', 'Tier 1');
    """
    cursor.execute(privilege_creep_query)

    # ---------------------------------------------------------
    # THREAT 3: MISSING MFA / STALE TOKENS (MEDIUM)
    # Account is active, but the token hasn't been rotated (is empty)
    # ---------------------------------------------------------
    stale_token_query = """
    INSERT INTO security_incidents (identity_id, incident_type, severity, description)
    SELECT 
        h.identity_id,
        'Stale Security Token' AS incident_type,
        'MEDIUM' AS severity,
        'Active ' || p.platform_name || ' account for ' || h.full_name || ' has no record of token rotation.' AS description
    FROM accounts a
    JOIN human_identities h ON a.identity_id = h.identity_id
    JOIN platforms p ON a.platform_id = p.platform_id
    WHERE a.account_status = 'ACTIVE' 
    AND (a.token_rotated_date IS NULL OR a.token_rotated_date = '');
    """
    cursor.execute(stale_token_query)

    conn.commit()
   

    incidents_df = pd.read_sql_query("SELECT incident_type, severity, description FROM security_incidents ORDER BY severity ASC", conn)
    # incidents_df.to_csv("reposr.csv",index=False)
    # print(incidents_df.head(10)) # Shows the first 10 incidents

    conn.close()
    

print(generate_security_incidents())