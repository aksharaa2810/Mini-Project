import csv
import pandas as pd
import os
import hashlib
from datetime import datetime
from utils.database import ensure_data_directory, STUDENTS_CSV, STAFF_CSV

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def import_users():
    ensure_data_directory()
    
    roles_file = 'ROLES.csv'
    if not os.path.exists(roles_file):
        print(f"❌ {roles_file} not found")
        return

    print(f"Reading {roles_file}...")
    
    # Read CSV manually to handle the weird structure
    users_to_add = []
    
    with open(roles_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader) # EMAIL,ROLE,,EMAIL,ROLE
        
        for row in reader:
            if not row: continue
            
            # Left side
            if len(row) >= 2 and row[0] and row[1]:
                users_to_add.append({'email': row[0].strip(), 'role': row[1].strip()})
            
            # Right side
            if len(row) >= 5 and row[3] and row[4]:
                users_to_add.append({'email': row[3].strip(), 'role': row[4].strip()})

    print(f"Found {len(users_to_add)} users to process.")

    # Process Students
    if os.path.exists(STUDENTS_CSV):
        students_df = pd.read_csv(STUDENTS_CSV)
    else:
        students_df = pd.DataFrame(columns=['user_id', 'name', 'email', 'parent_email', 'password', 'class', 'roll_no', 'department', 'semester', 'created_at'])

    # Process Staff
    if os.path.exists(STAFF_CSV):
        staff_df = pd.read_csv(STAFF_CSV)
    else:
        staff_df = pd.DataFrame(columns=['user_id', 'name', 'email', 'password', 'department', 'designation', 'created_at'])

    default_password = hash_password("password123")

    for user in users_to_add:
        email = user['email']
        role = user['role'].upper()
        
        # Extract name and ID from email (e.g., jaishree.2411025@srec.ac.in)
        try:
            local_part = email.split('@')[0]
            if '.' in local_part:
                name_part, id_part = local_part.rsplit('.', 1)
                name = name_part.replace('.', ' ').title()
                user_id = id_part
            else:
                name = local_part.title()
                user_id = local_part
                
        except Exception as e:
            print(f"Error parsing email {email}: {e}")
            continue

        if role == 'STUDENT':
            if email in students_df['email'].values:
                print(f"⚠️ Student already exists: {email}")
                continue
                
            new_student = {
                'user_id': user_id,
                'name': name,
                'email': email,
                'parent_email': '',
                'password': default_password,
                'class': 'Not Assigned',
                'roll_no': user_id[-3:] if len(user_id) >=3 else user_id,
                'department': 'Unknown',
                'semester': '3',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            # Append using concat
            students_df = pd.concat([students_df, pd.DataFrame([new_student])], ignore_index=True)
            print(f"✅ Added student: {name} ({user_id})")

        elif role in ['ADMIN', 'STAFF']:
            if email in staff_df['email'].values:
                print(f"⚠️ Staff already exists: {email}")
                continue
                
            new_staff = {
                'user_id': user_id,
                'name': name,
                'email': email,
                'password': default_password,
                'department': 'Administration' if role == 'ADMIN' else 'Unknown',
                'designation': 'Admin' if role == 'ADMIN' else 'Staff',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            # Append using concat
            staff_df = pd.concat([staff_df, pd.DataFrame([new_staff])], ignore_index=True)
            print(f"✅ Added staff/admin: {name} ({user_id})")

    # Save files
    students_df.to_csv(STUDENTS_CSV, index=False)
    staff_df.to_csv(STAFF_CSV, index=False)
    print("Saving complete.")

if __name__ == "__main__":
    import_users()
