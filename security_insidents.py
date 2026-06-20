from backend.db_connection import connect_db
import pandas as pd



def generate_security_incidents():
    conn = connect_db()
    cursor = conn.cursor()
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

    privilege_creep_query = \
    """
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

    cursor.execute(ghost_account_query)
    print(f"Detected {cursor.rowcount} Ghost Account violations.")
    cursor.execute(privilege_creep_query)
    cursor.execute(stale_token_query)
    conn.commit()

    incidents_df = pd.read_sql_query("SELECT incident_type, severity, description FROM security_incidents ORDER BY severity ASC", conn)

    conn.close()
    return incidents_df

def damage_score():
    conn = connect_db()
    cursor = conn.cursor()
    damage_threat = '''
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
    '''

    
    damage_score_df = pd.read_sql_query(damage_threat,conn)
    print(f"Detected {len(damage_score_df)} Damage Threat violations.")
    conn.commit()
    return  damage_score_df

def dormancy_threat():
    conn = connect_db()
    cursor = conn.cursor()
    dormancy = '''
        SELECT 
        identity_id,
        identity_name,
        hr_status,
        days_dormant,
        highest_tier_held as highiest_privilage,
        last_login_date,
        CASE 
            WHEN days_dormant is NULL THEN 100
            WHEN days_dormant >= 90 THEN 100
            WHEN days_dormant >= 60 THEN 50
            WHEN days_dormant >= 30 THEN 10
            ELSE 0 
        END AS dormancy_score
        FROM live_privileged_watchlist
        ORDER BY dormancy_score DESC, days_dormant DESC;
    '''

    dormancy_df = pd.read_sql_query(dormancy,conn)
    print(f"Detected {len(dormancy_df)} Dormancy Threat violations.")
    conn.commit()
    return dormancy_df




