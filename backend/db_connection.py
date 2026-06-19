import sqlite3
from utils.path import HYBRIDDB
import logging



def connect_db():
    try :
        conn = sqlite3.connect(HYBRIDDB)
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to the database :{e}")



con = connect_db()
print("Connection succesfull") if con else print("failed to connect")