from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

HYBRIDDB = BASE_DIR/"hybridguard.db"

# ___________________csv files path ____________________________________________

AWS_DATA =  BASE_DIR/"csvs"/"aws_users.csv"
OKTA =      BASE_DIR/"csvs"/"okta_users.csv"
USER_DETAILS = BASE_DIR/"csvs"/"user_details.csv"
