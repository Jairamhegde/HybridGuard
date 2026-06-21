import os
import random
import csv
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(BASE_DIR, "csvs")
os.makedirs(CSV_DIR, exist_ok=True)

USER_DETAILS_PATH = os.path.join(CSV_DIR, "user_details.csv")
AD_USERS_PATH = os.path.join(CSV_DIR, "ad_users.csv")
AWS_USERS_PATH = os.path.join(CSV_DIR, "aws_users.csv")
OKTA_USERS_PATH = os.path.join(CSV_DIR, "okta_users.csv")
AUDIT_EVENTS_PATH = os.path.join(CSV_DIR, "audit_events.csv")

random.seed(42)

first_names = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
    "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua",
    "Kenneth", "Kevin", "Brian", "George", "Edward", "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan",
    "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen",
    "Lisa", "Nancy", "Betty", "Sandra", "Margaret", "Ashley", "Kimberly", "Emily", "Donna", "Michelle"
]
last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"
]

names_set = set()
while len(names_set) < 250:
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    names_set.add(name)
names_list = sorted(list(names_set))

import re
from difflib import SequenceMatcher

def get_clean_alpha(s):
    return "".join(c for c in s if c.isalpha()).lower()

def clean_username(text):
    return re.sub(r'[^a-z]', '', str(text).lower())

def generate_namepattern(name):
    parts = str(name).lower().strip().split()
    if len(parts) < 2:
        return [clean_username(name)]
    first, last = parts[0], parts[-1]
    return [first+last, last+first, first[0]+last, last+first[0], first+last[0], last[0]+first, first, last]

def get_identity(messy_username, official_patterns):
    cleaned = clean_username(messy_username)
    best, highest = None, 0.0
    for name, patterns in official_patterns.items():
        for pat in patterns:
            score = SequenceMatcher(None, cleaned, pat).ratio()
            if score > highest:
                highest, best = score, name
    return best if highest >= 0.80 else None

official_patterns = {name: generate_namepattern(name) for name in names_list}

def make_messy_username(full_name, platform, user_id, official_patterns):
    parts = full_name.split(" ")
    first, last = get_clean_alpha(parts[0]), get_clean_alpha(parts[-1])

    base_patterns = [
        f"{first}{last}",
        f"{last}{first}",
        f"{first[0]}{last}",
        f"{last}{first[0]}",
        f"{first}{last[0]}",
        f"{last[0]}{first}"
    ]

    base = None
    for bp in base_patterns:
        if get_identity(bp, official_patterns) == full_name:
            base = bp
            break

    if not base:
        base = f"{first}{last}"

    fmt = random.choice([
        lambda b: b.upper(),
        lambda b: f"{b[:len(b)//2]}.{b[len(b)//2:]}",
        lambda b: f"{b}_{random.randint(1, 99)}",
        lambda b: f"{b}.{random.randint(10, 99)}",
        lambda b: f"{b}-{random.randint(1, 9)}",
        lambda b: f"{b.upper()}_{random.randint(1, 9)}"
    ])

    return fmt(base)

identities = []
ad_users = []
aws_users = []
okta_users = []
audit_events = []

event_id_counter = 1

for i, name in enumerate(names_list):
    user_id = i + 1
    first, last = name.split(" ", 1)
    email = f"{get_clean_alpha(first)}.{get_clean_alpha(last)}{user_id}@company.com"

    ad_uname = make_messy_username(name, "AD", user_id, official_patterns)
    aws_uname = make_messy_username(name, "AWS", user_id, official_patterns)
    okta_uname = make_messy_username(name, "Okta", user_id, official_patterns)

    hr_status = "ACTIVE"
    hr_role = "User"
    ad_status = "ACTIVE"
    ad_group = "Domain Users"
    aws_status = "ACTIVE"
    aws_role = "S3ReadOnly"
    okta_status = "ACTIVE"
    okta_role = "User"

    # Determine dormancy profile
    if user_id in [40, 41, 42, 43]:
        dormant_days = random.randint(90, 120)
    elif user_id in [90, 91, 92, 93]:
        dormant_days = random.randint(90, 120)
    elif random.random() < 0.15:
        # 15% other users are dormant (30 to 89 days ago)
        dormant_days = random.randint(30, 89)
    else:
        # active users (2 to 20 days ago)
        dormant_days = random.randint(2, 20)

    last_login_dt = datetime(2026, 6, 21) - timedelta(days=dormant_days)
    last_login = last_login_dt.strftime("%Y-%m-%d %H:%M:%S")
    created_date = (last_login_dt - timedelta(days=random.randint(180, 500))).strftime("%Y-%m-%d")
    rotated_date = (last_login_dt - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")

    if user_id <= 30:
        hr_status = "DISABLED"
        hr_role = "User"
        ad_status = "ACTIVE"
        aws_status = "ACTIVE"
        okta_status = "ACTIVE"

    elif user_id <= 55:
        hr_status = "ACTIVE"
        hr_role = "User" # Tier 2 HR role
        ad_group = "Domain Users"
        aws_role = "AdministratorAccess"
        okta_role = "SuperAdmin"

    elif user_id <= 70:
        hr_status = "ACTIVE"
        hr_role = "User"
        ad_group = "Domain Users"
        aws_role = "ReadOnlyAccess"
        okta_role = "User"

    elif user_id <= 80:
        hr_status = "ACTIVE"
        hr_role = "User"
        ad_group = "Domain Users"
        aws_role = "ReadOnlyAccess"
        okta_role = "User"
        rotated_date = ""

    elif user_id <= 125:
        hr_status = "ACTIVE"
        hr_role = random.choice(["Domain Admin", "Enterprise Admin", "Server Operator"])
        ad_group = "Domain Admins" if "Admin" in hr_role else "Server Operators"
        aws_role = "AdministratorAccess" if "Admin" in hr_role else "PowerUserAccess"
        okta_role = "SuperAdmin" if "Admin" in hr_role else "InternalToolsAdmin"

    else:
        hr_status = "ACTIVE"
        hr_role = random.choice(["User", "Backup Operator", "Account Operator"])
        ad_group = "Domain Users" if hr_role == "User" else ("Server Operators" if hr_role == "Server Operator" else "Account Operators")
        aws_role = random.choice(["S3ReadOnly", "ReadOnlyAccess"])
        okta_role = "User"

    identities.append({
        'user_id': user_id,
        'name': name,
        'email': email,
        'status': hr_status,
        'role': hr_role
    })

    ad_users.append({
        'employee_id': user_id,
        'sAMAccountName': ad_uname,
        'userPrincipalName': email,
        'ad_status': ad_status,
        'ad_group': ad_group
    })

    aws_users.append({
        'userid': 10000 + user_id,
        'username': aws_uname,
        'email': email,
        'status': aws_status,
        'role': aws_role,
        'tokenusage': random.randint(10, 2000),
        'createdat': created_date,
        'rotatedat': rotated_date
    })

    okta_users.append({
        'userid': 20000 + user_id,
        'username': okta_uname,
        'email': email,
        'status': okta_status,
        'role': okta_role,
        'tokenusage': random.randint(10, 2000),
        'createdat': created_date,
        'rotatedat': rotated_date,
        'last login date': last_login
    })

    platforms_list = ["AD", "AWS", "OKTA"]
    resources = {
        "AD": ["AD:GroupPolicy", "VPN:Gateway", "CRM:Records"],
        "AWS": ["S3:customer-data", "AWS:IAM", "CRM:Records"],
        "OKTA": ["CRM:Records", "VPN:Gateway", "Okta:AdminConsole"]
    }
    ips = [f"{random.randint(50, 180)}.{random.randint(10, 250)}.{random.randint(1, 254)}.{random.randint(1, 254)}" for _ in range(50)]

    for platform in platforms_list:
        uname_map = {"AD": ad_uname, "AWS": aws_uname, "OKTA": okta_uname}
        uid_map = {"AD": user_id, "AWS": 10000 + user_id, "OKTA": 20000 + user_id}

        audit_events.append({
            'event_id': event_id_counter,
            'user_id': uid_map[platform],
            'username': uname_map[platform],
            'platform': platform,
            'event_type': "LOGIN",
            'timestamp': (last_login_dt - timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))).strftime("%Y-%m-%dT%H:%M:%S"),
            'source_ip': random.choice(ips),
            'resource_accessed': random.choice(resources[platform]),
            'previlage change': ""
        })
        event_id_counter += 1

    if 55 < user_id <= 70:
        platform = random.choice(["AWS", "OKTA"])
        uname_map = {"AD": ad_uname, "AWS": aws_uname, "OKTA": okta_uname}
        uid_map = {"AD": user_id, "AWS": 10000 + user_id, "OKTA": 20000 + user_id}

        audit_events.append({
            'event_id': event_id_counter,
            'user_id': uid_map[platform],
            'username': uname_map[platform],
            'platform': platform,
            'event_type': "PRIVILEGE_CHANGE",
            'timestamp': (datetime(2026, 6, 19, 10, 0, 0)).strftime("%Y-%m-%dT%H:%M:%S"),
            'source_ip': random.choice(ips),
            'resource_accessed': "Okta:AdminConsole" if platform == "OKTA" else "AWS:IAM",
            'previlage change': "SuperAdmin" if platform == "OKTA" else "AdministratorAccess"
        })
        event_id_counter += 1

    if 70 < user_id <= 80:
        platform = random.choice(["AWS", "OKTA"])
        uname_map = {"AD": ad_uname, "AWS": aws_uname, "OKTA": okta_uname}
        uid_map = {"AD": user_id, "AWS": 10000 + user_id, "OKTA": 20000 + user_id}

        suspicious_ip = f"198.51.100.{random.randint(10, 250)}"
        audit_events.append({
            'event_id': event_id_counter,
            'user_id': uid_map[platform],
            'username': uname_map[platform],
            'platform': platform,
            'event_type': "TOKEN_USED",
            'timestamp': (datetime(2026, 6, 20, 2, 30, 0)).strftime("%Y-%m-%dT%H:%M:%S"),
            'source_ip': suspicious_ip,
            'resource_accessed': "S3:customer-data" if platform == "AWS" else "Okta:AdminConsole",
            'previlage change': ""
        })
        event_id_counter += 1

def write_csv(filepath, data, fieldnames):
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Successfully generated {filepath} with {len(data)} rows.")

write_csv(USER_DETAILS_PATH, identities, ['user_id', 'name', 'email', 'status', 'role'])
write_csv(AD_USERS_PATH, ad_users, ['employee_id', 'sAMAccountName', 'userPrincipalName', 'ad_status', 'ad_group'])
write_csv(AWS_USERS_PATH, aws_users, ['userid', 'username', 'email', 'status', 'role', 'tokenusage', 'createdat', 'rotatedat'])
write_csv(OKTA_USERS_PATH, okta_users, ['userid', 'username', 'email', 'status', 'role', 'tokenusage', 'createdat', 'rotatedat', 'last login date'])
write_csv(AUDIT_EVENTS_PATH, audit_events, ['event_id', 'user_id', 'username', 'platform', 'event_type', 'timestamp', 'source_ip', 'resource_accessed', 'previlage change'])

# Write ground truth labels for self-evaluation
labels_path = os.path.join(BASE_DIR, "identity_risk_labels.csv")
labels_data = []
for i, name in enumerate(names_list):
    user_id = i + 1
    is_risky = 0
    anomaly_type = "NORMAL"
    if user_id <= 30:
        is_risky = 1
        anomaly_type = "ORPHANED_CROSS_PLATFORM"
    elif user_id <= 55:
        is_risky = 1
        anomaly_type = "PRIVILEGE_CREEP"
    elif user_id <= 70:
        is_risky = 1
        anomaly_type = "PRIVILEGE_ESCALATION"
    elif user_id <= 80:
        is_risky = 1
        anomaly_type = "SUSPICIOUS_TOKEN_USE"
        
    labels_data.append({
        'identity_id': user_id,
        'email': f"{get_clean_alpha(name.split(' ')[0])}.{get_clean_alpha(name.split(' ')[-1])}{user_id}@company.com",
        'is_risky': is_risky,
        'anomaly_type': anomaly_type
    })
write_csv(labels_path, labels_data, ['identity_id', 'email', 'is_risky', 'anomaly_type'])

print("All CSV datasets successfully generated.")