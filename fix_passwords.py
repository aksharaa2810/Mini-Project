import pandas as pd
import hashlib
from utils.database import STUDENTS_CSV

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def fix_passwords():
    print("Fixing passwords...")
    
    # Target students (existing ones)
    targets = ['STU002', 'STU003', 'Abhishek'] 
    # Abhishek is Admin but let's check staff file too.
    
    # 1. Fix Students
    try:
        df = pd.read_csv(STUDENTS_CSV)
        new_pass_hash = hash_password('password123')
        
        # Update Jaishree (STU002) and Aksharaa (STU003)
        mask = df['user_id'].isin(['STU002', 'STU003'])
        if mask.any():
            df.loc[mask, 'password'] = new_pass_hash
            print("✅ Updated passwords for STU002 and STU003 to 'password123'")
            
        df.to_csv(STUDENTS_CSV, index=False)
        print("Student passwords updated.")
        
    except Exception as e:
        print(f"Error updating students: {e}")

    # 2. Fix Admin/Staff
    # Check STAFF_CSV
    from utils.database import STAFF_CSV
    try:
        df_staff = pd.read_csv(STAFF_CSV)
        # Check for Abhishek
        mask_staff = df_staff['email'].str.contains('abhishek', case=False)
        if mask_staff.any():
            df_staff.loc[mask_staff, 'password'] = new_pass_hash
            print("✅ Updated password for Abhishek (Admin) to 'password123'")
            
            # Print his User ID
            user_id = df_staff.loc[mask_staff, 'user_id'].values[0]
            print(f"👉 Admin User ID is: {user_id}")
            
        df_staff.to_csv(STAFF_CSV, index=False)
        print("Staff passwords updated.")
        
    except Exception as e:
        print(f"Error updating staff: {e}")

if __name__ == "__main__":
    fix_passwords()
