import pandas as pd
from utils.path import USER_DETAILS
def generate_ad_csv():
    print("Reading user_details.csv...")
    try:
        # Load the HR Source of Truth
        hr_df = pd.read_csv(USER_DETAILS)
    except FileNotFoundError:
        print("Error: Could not find 'user_details.csv'. Please make sure it's in the same folder.")
        return

    ad_records = []
    
    for _, row in hr_df.iterrows():
        # 1. Create the sAMAccountName (First Initial + Last Name)
        name_parts = str(row['name']).lower().strip().split()
        if len(name_parts) >= 2:
            sam_account_name = name_parts[0][0] + name_parts[-1] # e.g., 'Allison Hill' -> 'ahill'
        elif len(name_parts) == 1:
            sam_account_name = name_parts[0]
        else:
            sam_account_name = "unknown"
            
        # 2. Map the HR Role to a realistic Active Directory Group
        hr_role = str(row['role']).strip()
        if hr_role in ['Domain Admin', 'Enterprise Admin']:
            ad_group = 'Domain Admins'
        elif hr_role in ['Server Operator', 'Backup Operator']:
            ad_group = 'Server Operators'
        elif hr_role == 'Account Operator':
            ad_group = 'Account Operators'
        else:
            ad_group = 'Domain Users' # The baseline group for standard employees

        # 3. Build the AD Record
        ad_records.append({
            'employee_id': row['user_id'],          # Links back to HR Identity
            'sAMAccountName': sam_account_name,     # The AD Username
            'userPrincipalName': row['email'],      # The Email (UPN)
            'ad_status': row['status'],             # ACTIVE or DISABLED
            'ad_group': ad_group                    # The Privilege Baseline
        })
        
    ad_df = pd.DataFrame(ad_records)
    
    # Save the file
    output_filename = "ad_users.csv"
    ad_df.to_csv(output_filename, index=False)
    
    print(f"✅ Successfully generated {output_filename} with {len(ad_df)} Active Directory records!")

if __name__ == "__main__":
    generate_ad_csv()