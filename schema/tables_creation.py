import sqlite3
from backend.db_connection import connect_db

conn = connect_db()
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

huma_identity_table ="""
CREATE TABLE IF NOT EXISTS human_identities (
    identity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    hr_status TEXT NOT NULL
);"""

platforms ="""
CREATE TABLE IF NOT EXISTS platforms (
    platform_id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_name TEXT UNIQUE NOT NULL
);"""

accounts_table ='''
CREATE TABLE IF NOT EXISTS accounts (
        account_id TEXT PRIMARY KEY, 
        identity_id INTEGER,
        platform_id INTEGER,
        platform_username TEXT NOT NULL,
        account_status TEXT NOT NULL,
        token_usage INTEGER,
        token_created_date DATE,
        token_rotated_date DATE,
        FOREIGN KEY (identity_id) REFERENCES human_identities(identity_id) ON DELETE CASCADE,
        FOREIGN KEY (platform_id) REFERENCES platforms(platform_id) ON DELETE RESTRICT
    );'''

role_defination_table ='''
CREATE TABLE IF NOT EXISTS role_definitions (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_id INTEGER,
    raw_role_name TEXT NOT NULL,
    normalized_tier TEXT NOT NULL,
    FOREIGN KEY (platform_id) REFERENCES platforms(platform_id) ON DELETE CASCADE,
    UNIQUE(platform_id, raw_role_name) -- Prevents duplicate roles on the same platform
);'''

account_role_mapping = """
    CREATE TABLE IF NOT EXISTS account_role_mapping (
    mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id TEXT,
    role_id INTEGER,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES role_definitions(role_id) ON DELETE CASCADE,
    UNIQUE(account_id, role_id) -- Prevents assigning the exact same role to the same account twice
);"""

security_incidents = """

    CREATE TABLE IF NOT EXISTS security_incidents (
        incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
        identity_id INTEGER,
        incident_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT DEFAULT 'OPEN',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (identity_id) REFERENCES human_identities(identity_id) ON DELETE CASCADE
    );
    """

cur.execute(huma_identity_table)
cur.execute(platforms)
cur.execute(accounts_table)
cur.execute(role_defination_table)
cur.execute(account_role_mapping)
cur.execute(security_incidents)
conn.commit()
conn.close()