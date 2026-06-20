import sqlite3
import sys
import os
import logging

# Add project root to sys.path so imports work regardless of where script is run from
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.db_connection import connect_db

def clear_all_data():
    
    conn = connect_db()
    if conn is None:
        logging.error("Could not connect to database. Aborting clear operation.")
        return False

    try:
        cur = conn.cursor()
        
        cur.execute("PRAGMA foreign_keys = OFF;")
        tables = [
            "account_role_mapping",
            "security_incidents",
            "accounts",
            "role_definitions",
            "platforms",
            "human_identities"
        ]
        
        for table in tables:
            cur.execute(f"DELETE FROM {table};")
            logging.info(f"Cleared all rows from {table}")
        
        cur.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
        logging.info("All data cleared successfully.")
        return True
    except Exception as e:
        conn.rollback()
        logging.error(f"Failed to clear data: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = clear_all_data()
    if success:
        print("All data cleared from the database.")
    else:
        print("Failed to clear data. Check logs for details.")