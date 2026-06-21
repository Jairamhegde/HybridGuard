import pandas as pd
import re
from difflib import SequenceMatcher
from utils.path import USER_DETAILS, AWS_DATA, OKTA, AUDIT_EVENTS, AD_USERS
from backend.db_connection import connect_db

# ___________________________HELPER_FUNCTIONS__________________________________
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
    if role in ['admin', 'domain admins', 'enterprise admin', 'iamfullaccess', 'administratoraccess']: 
        return "Tier 0"
    elif role in ['applicationadmin', 'helpdeskadmin', 'server operators', 'ec2fullaccess', 'internaltoolsadmin']: 
        return "Tier 1"
    elif role in ['user', 'domain users', 'backup operator', 'account operators', 'readonlyaccess', 's3readonly', 's3fullaccess']: 
        return "Tier 2"
    return "Unknown Role"

def get_identity(messy_username, official_patterns):
    cleaned = clean_username(messy_username)
    best, highest = None, 0.0
    for name, patterns in official_patterns.items():
        for pat in patterns:
            score = SequenceMatcher(None, cleaned, pat).ratio()
            if score > highest: 
                highest, best = score, name
    return best if highest >= 0.80 else None

# ___________________________EXTRACT__MATCH__________________________________
def load_and_match_data():
    print("1. Extracting data from CSVs...")
    hr_df = pd.read_csv(USER_DETAILS)
    aws_df = pd.read_csv(AWS_DATA)
    okta_df = pd.read_csv(OKTA)
    ad_df = pd.read_csv(AD_USERS)        
    audit_df = pd.read_csv(AUDIT_EVENTS)  

    official_patterns = {name: generate_namepattern(name) for name in hr_df['name']}

    print("2. Matching messy usernames to official HR identities...")
    aws_df['matched_human'] = aws_df['username'].apply(lambda x:get_identity(x,official_patterns))
    okta_df['matched_human'] = okta_df['username'].apply(lambda x:get_identity(x,official_patterns))
    ad_df['matched_human'] = ad_df['sAMAccountName'].apply(lambda x:get_identity(x,official_patterns))
    audit_df['matched_human'] = audit_df['username'].apply(lambda x:get_identity(x,official_patterns))
    
    return hr_df, aws_df, okta_df, ad_df, audit_df

# ___________________________TRANSFORM__________________________________________


def process_platform(df, platform_id, prefix, id_col, role_col, user_col, status_col, name_to_id, unique_roles, accounts_list, role_mappings_list, last_login_dict, human_col='name'):
    for _, row in df.iterrows():
        identity_id = name_to_id.get(row.get(human_col))
        
        if identity_id:
            # Fetch last login date
            account_last_login = last_login_dict.get((identity_id, prefix.upper()), None)
            
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
                'token_rotated_date': row.get('rotatedat', None),
                'last_login_date': account_last_login 
            })

            # Build Role Definition
            raw_role = row[role_col]
            role_key = f"{platform_id}_{raw_role}"
            
            if role_key not in unique_roles:
                unique_roles[role_key] = {
                    'role_id': len(unique_roles) + 1, 
                    'platform_id': platform_id,
                    'raw_role_name': raw_role,
                    'normalized_tier': normalize_role(raw_role)
                }
            
            # Build Account-to-Role Mapping
            role_mappings_list.append({
                'account_id': acc_id,
                'role_id': unique_roles[role_key]['role_id']
            })

def transform_to_3nf(hr_df, aws_df, okta_df, ad_df, audit_df):
    print("3. Transforming flat data into 3NF relational tables...")
    
    platforms_df = pd.DataFrame([
        {'platform_id': 1, 'platform_name': 'AD'},
        {'platform_id': 2, 'platform_name': 'AWS'},
        {'platform_id': 3, 'platform_name': 'Okta'}
    ])

    # Table 2: Human Identities
    identities_df = hr_df[['name', 'email', 'status']].copy()
    identities_df.rename(columns={'name': 'full_name', 'status': 'hr_status'}, inplace=True)
    identities_df['identity_id'] = identities_df.index + 1 
    
    name_to_id = dict(zip(identities_df['full_name'], identities_df['identity_id']))

    # Calculate Last Login Dates from Audit Logs
    last_login_dict = {}
    if not audit_df.empty:
        for _, row in audit_df.iterrows():
            human_name = row.get('matched_human')
            identity_id = name_to_id.get(human_name)
            if identity_id:
                key = (identity_id, str(row['platform']).upper())
                event_time = row['timestamp'] 
                
                # Save the absolute newest date we find
                if key not in last_login_dict or event_time > last_login_dict[key]:
                    last_login_dict[key] = event_time

    # Setup for Tables 3, 4, and 5
    accounts_list = []
    role_mappings_list = []
    unique_roles = {} 

    # Run the processor for each platform
    process_platform(ad_df, 1, "AD", 'employee_id', 'ad_group', 'sAMAccountName', 'ad_status', name_to_id, unique_roles, accounts_list, role_mappings_list, last_login_dict, 'matched_human')
    process_platform(aws_df, 2, "AWS", 'userid', 'role', 'username', 'status', name_to_id, unique_roles, accounts_list, role_mappings_list, last_login_dict, 'matched_human')
    process_platform(okta_df, 3, "OKTA", 'userid', 'role', 'username', 'status', name_to_id, unique_roles, accounts_list, role_mappings_list, last_login_dict, 'matched_human')
    
    accounts_df = pd.DataFrame(accounts_list)
    role_definitions_df = pd.DataFrame(list(unique_roles.values()))
    mapping_df = pd.DataFrame(role_mappings_list)

    if not audit_df.empty:
        audit_df['identity_id'] = audit_df['matched_human'].map(name_to_id)
        audit_df.rename(columns={
            'event id': 'event_id',
            'time stamp': 'timestamp',
            'previlatge changed': 'event_type' 
        }, inplace=True)

    return {
        'platforms': platforms_df,
        'human_identities': identities_df,
        'accounts': accounts_df,
        'role_definitions': role_definitions_df,
        'account_role_mapping': mapping_df,
        'audit_events': audit_df  
    }
# _____________________________LOAD_______________________________________________________
def load_to_database(tables_dict):
    print("4. Loading data into the SQLite database...")
    conn = connect_db()
    for table_name, dataframe in tables_dict.items():
        dataframe.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"   -> Loaded {len(dataframe)} rows into {table_name}")
    conn.close()
   
def main():
    hr_df, aws_df, okta_df, ad_df, audit_df = load_and_match_data()
    relational_tables = transform_to_3nf(hr_df, aws_df, okta_df, ad_df, audit_df)
    load_to_database(relational_tables)

main()
