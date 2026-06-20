from backend.db_connection import connect_db
import pandas as pd
from datetime import datetime

def generate_security_incidents():
    conn = connect_db()
    cursor = conn.cursor()

    # 1. Create the Incidents Table with the correct schema
    cursor.execute("DROP TABLE IF EXISTS security_incidents;")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS security_incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        full_name TEXT NOT NULL,
        incident_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        platform TEXT NOT NULL,
        description TEXT NOT NULL,
        detected_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()

    # Load data from relational tables
    df_identities = pd.read_sql_query("SELECT * FROM human_identities", conn)
    df_accounts = pd.read_sql_query("SELECT * FROM accounts", conn)
    df_platforms = pd.read_sql_query("SELECT * FROM platforms", conn)
    df_roles = pd.read_sql_query("SELECT * FROM role_definitions", conn)
    df_mappings = pd.read_sql_query("SELECT * FROM account_role_mapping", conn)

    # Dictionary to collect and group incidents by employee & incident type
    # Key: (user_id, incident_type) -> { ... }
    incidents_map = {}

    def add_incident(user_id, full_name, incident_type, severity, platform_name, description):
        key = (user_id, incident_type)
        if key not in incidents_map:
            incidents_map[key] = {
                'user_id': user_id,
                'full_name': full_name,
                'incident_type': incident_type,
                'severity': severity,
                'platforms': set(),
                'descriptions': []
            }
        incidents_map[key]['platforms'].add(platform_name)
        incidents_map[key]['descriptions'].append(description)

    # ---------------------------------------------------------
    # THREAT 1: GHOST ACCOUNT (CRITICAL)
    # Terminated employee (DISABLED in HR) has ACTIVE platform account
    # ---------------------------------------------------------
    df_acc_ind = df_accounts.merge(df_identities, on='identity_id')
    df_acc_ind = df_acc_ind.merge(df_platforms, on='platform_id')

    ghosts = df_acc_ind[(df_acc_ind['hr_status'] == 'DISABLED') & (df_acc_ind['account_status'] == 'ACTIVE') & (df_acc_ind['platform_id'].isin([2, 3]))]
    for _, row in ghosts.iterrows():
        pname = row['platform_name']
        desc = f"Terminated employee still has active {pname} account."
        add_incident(row['user_id'], row['full_name'], "Ghost Account", "Critical", pname, desc)

    # ---------------------------------------------------------
    # THREAT 2: PRIVILEGE CREEP (HIGH)
    # Employee holds Tier 2 in HR, but Tier 0 or Tier 1 in AWS or Okta
    # ---------------------------------------------------------
    df_acc_roles = df_accounts.merge(df_mappings, on='account_id').merge(df_roles, on=['role_id', 'platform_id'])
    
    # Extract HR tiers per human identity
    df_hr_roles = df_acc_roles[df_acc_roles['platform_id'] == 1][['identity_id', 'normalized_tier']].rename(columns={'normalized_tier': 'hr_tier'})
    # Extract system tiers per human identity
    df_sys_roles = df_acc_roles[df_acc_roles['platform_id'].isin([2, 3])][['identity_id', 'platform_id', 'raw_role_name', 'normalized_tier']].rename(columns={'normalized_tier': 'sys_tier'})
    
    df_creep = df_sys_roles.merge(df_hr_roles, on='identity_id')
    df_creep = df_creep.merge(df_identities, on='identity_id')
    df_creep = df_creep.merge(df_platforms, on='platform_id')
    
    creep_violations = df_creep[(df_creep['hr_tier'] == 'Tier 2') & (df_creep['sys_tier'].isin(['Tier 0', 'Tier 1'])) & (df_creep['hr_status'] == 'ACTIVE')]
    for _, row in creep_violations.iterrows():
        pname = row['platform_name']
        desc = f"Standard Tier 2 employee holds elevated {row['sys_tier']} access ({row['raw_role_name']}) in {pname}."
        add_incident(row['user_id'], row['full_name'], "Privilege Creep", "High", pname, desc)

    # ---------------------------------------------------------
    # THREAT 3: STALE TOKENS (MEDIUM)
    # Token rotated date is missing or > 180 days relative to 2026-06-20 reference date
    # ---------------------------------------------------------
    ref_date = datetime(2026, 6, 20)
    df_active_sys = df_accounts[(df_accounts['platform_id'].isin([2, 3])) & (df_accounts['account_status'] == 'ACTIVE')].copy()
    df_active_sys = df_active_sys.merge(df_identities, on='identity_id')
    df_active_sys = df_active_sys.merge(df_platforms, on='platform_id')

    for _, row in df_active_sys.iterrows():
        rot = row['token_rotated_date']
        cre = row['token_created_date']
        eff_date_str = rot if (pd.notna(rot) and str(rot).strip() != '') else cre
        
        is_stale = False
        last_rot_text = "None"
        if pd.isna(eff_date_str) or str(eff_date_str).strip() == '':
            is_stale = True
        else:
            try:
                eff_date = datetime.strptime(str(eff_date_str).strip(), "%Y-%m-%d")
                age_days = (ref_date - eff_date).days
                last_rot_text = str(eff_date_str).strip()
                if age_days >= 180:
                    is_stale = True
            except Exception:
                is_stale = True
        
        if is_stale:
            pname = row['platform_name']
            desc = f"Active {pname} account has no record of token rotation in the last 180 days (last rotation: {last_rot_text})."
            add_incident(row['user_id'], row['full_name'], "Stale Token", "Medium", pname, desc)

    # ---------------------------------------------------------
    # CONSOLIDATE AND INSERT TO DB
    # ---------------------------------------------------------
    incidents_list = []
    for (user_id, incident_type), data in incidents_map.items():
        platform_str = ", ".join(sorted(data['platforms']))
        
        if len(data['descriptions']) == 1:
            desc_str = data['descriptions'][0]
        else:
            desc_str = f"Violations found on {platform_str}: " + "; ".join(data['descriptions'])
            
        cursor.execute("""
            INSERT INTO security_incidents (user_id, full_name, incident_type, severity, platform, description)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (user_id, data['full_name'], incident_type, data['severity'], platform_str, desc_str))
        
        incidents_list.append({
            'user_id': user_id,
            'full_name': data['full_name'],
            'incident_type': incident_type,
            'severity': data['severity'],
            'platform': platform_str,
            'description': desc_str
        })

    conn.commit()
    conn.close()
    
    # Return df for debug prints / backward compatibility
    return pd.DataFrame(incidents_list)

if __name__ == "__main__":
    df = generate_security_incidents()
    print(f"Detected and stored {len(df)} violations in SQLite database.")
    df.to_csv("reposr.csv", index=False)
