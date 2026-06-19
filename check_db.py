import sqlite3

conn = sqlite3.connect('hybridguard.db')
cur = conn.cursor()

# Check what tables exist
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("Tables in database:", tables)

if tables:
    for table in tables:
        cur.execute(f"PRAGMA table_info({table[0]})")
        cols = cur.fetchall()
        print(f"\n--- {table[0]} ---")
        for col in cols:
            print(f"  {col[1]} ({col[2]})")

conn.close()