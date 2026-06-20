import pandas as pd
import sqlite3
import re
from difflib import SequenceMatcher
from utils.path import USER_DETAILS, AWS_DATA, OKTA 
from backend.db_connection import connect_db

def clean_username(text):
    return re.sub(r'[^a-z]', '', str(text).lower())

def generate_namepattern(name):
    parts = str(name).lower().strip().split()
    if len(parts) < 2: 
        return [clean_username(name)]
    first, last = parts[0], parts[-1]
    return [first+last, last+first, first[0]+last, last+first[0], first+last[0], last[0]+first, first, last]

def normalize_role(raw_role):
    role = str(raw_role).lower().strip()
    if role in ['admin', 'domain admin', 'enterprise admin', 'iamfullaccess', 'administratoraccess']: 
        return "Tier 0"
    elif role in ['applicationadmin', 'helpdeskadmin', 'server operator', 'ec2fullaccess', 'internaltoolsadmin']: 
        return "Tier 1"
    elif role in ['user', 'backup operator', 'account operator', 'readonlyaccess', 's3readonly', 's3fullaccess']: 
        return "Tier 2"
    return "Unknown Role"

# ==========================================
# 2. EXTRACT & MATCH STAGE
# ==========================================

def load_and_match_data():
    """Loads CSVs and applies the fuzzy matcher to find out who is who."""
    print("1. Extracting data from CSVs...")
    hr_df = pd.read_csv(USER_DETAILS)
    aws_df = pd.read_csv(AWS_DATA)
    okta_df = pd.read_csv(OKTA)

    print("2. Matching messy usernames to official HR identities...")
    official_patterns = {name: generate_namepattern(name) for name in hr_df['name']}

    def get_identity(messy_username):
        cleaned = clean_username(messy_username)
        best, highest = None, 0.0
        for name, patterns in official_patterns.items():
            for pat in patterns:
                score = SequenceMatcher(None, cleaned, pat).ratio()
                if score > highest: 
                    highest, best = score, name
        return best if highest >= 0.80 else None

    # Apply matching to the platform dataframes
    aws_df['matched_human'] = aws_df['username'].apply(get_identity)
    okta_df['matched_human'] = okta_df['username'].apply(get_identity)

    return hr_df, aws_df, okta_df



def transform_to_3nf(hr_df, aws_df, okta_df):
    print("3. Transforming flat data into 3NF relational tables...")

    # Table 1: Platforms
    platforms_df = pd.DataFrame([
        {'platform_id': 1, 'platform_name': 'HR_System'},
        {'platform_id': 2, 'platform_name': 'AWS'},
        {'platform_id': 3, 'platform_name': 'Okta'}
    ])

    # Table 2: Human Identities
    identities_df = hr_df[['user_id', 'name', 'email', 'status']].copy()
    identities_df.rename(columns={'name': 'full_name', 'status': 'hr_status'}, inplace=True)
    identities_df['identity_id'] = identities_df.index + 1 
    identities_df['user_id'] = identities_df['user_id'].apply(lambda x: f"EMP{int(x):04d}")
    
    name_to_id = dict(zip(identities_df['full_name'], identities_df['identity_id']))

    # Setup for Tables 3, 4, and 5
    accounts_list = []
    role_mappings_list = []
    unique_roles = {} 
    role_id_counter = 1

    def process_platform(df, platform_id, prefix, id_col, role_col, user_col, status_col, human_col='name'):
        nonlocal role_id_counter
        for _, row in df.iterrows():
            identity_id = name_to_id.get(row.get(human_col))
            
            if identity_id:
                # Build Account
                acc_id = f"{prefix}-{row[id_col]}"
                accounts_list.append({
                    'account_id': acc_id,
                    'identity_id': identity_id,
                    'platform_id': platform_id,
                    'platform_username': row[user_col],
                    'account_status': row[status_col],
                    'token_usage': row.get('tokenusage', None),
                    'token_created_date': row.get('createdat', None),
                    'token_rotated_date': row.get('rotatedat', None)
                })

                # Build Role Definition
                raw_role = row[role_col]
                role_key = f"{platform_id}_{raw_role}"
                
                if role_key not in unique_roles:
                    unique_roles[role_key] = {
                        'role_id': role_id_counter,
                        'platform_id': platform_id,
                        'raw_role_name': raw_role,
                        'normalized_tier': normalize_role(raw_role)
                    }
                    role_id_counter += 1
                
                # Build Account-to-Role Mapping
                role_mappings_list.append({
                    'account_id': acc_id,
                    'role_id': unique_roles[role_key]['role_id']
                })

    # Run the processor for each platform
    process_platform(hr_df, 1, "HR", 'user_id', 'role', 'email', 'status', 'name')
    process_platform(aws_df, 2, "AWS", 'userid', 'role', 'username', 'status', 'matched_human')
    process_platform(okta_df, 3, "OKTA", 'userid', 'role', 'username', 'status', 'matched_human')

    accounts_df = pd.DataFrame(accounts_list)
    role_definitions_df = pd.DataFrame(list(unique_roles.values()))
    mapping_df = pd.DataFrame(role_mappings_list)

    # Return a dictionary of all the tables we built
    return {
        'platforms': platforms_df,
        'human_identities': identities_df,
        'accounts': accounts_df,
        'role_definitions': role_definitions_df,
        'account_role_mapping': mapping_df
    }

def load_to_database(tables_dict):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF;")
    for table_name in tables_dict.keys():
        cursor.execute(f"DELETE FROM {table_name};")
    cursor.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    for table_name, dataframe in tables_dict.items():
        dataframe.to_sql(table_name, conn, if_exists='append', index=False)
    conn.close()
    


def main():
    hr_df, aws_df, okta_df = load_and_match_data()
    
    relational_tables = transform_to_3nf(hr_df, aws_df, okta_df)

    load_to_database(relational_tables)
    

if __name__ == "__main__":
    main()