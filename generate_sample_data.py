import csv
import random
import hashlib
from datetime import datetime
import os

# Configuration
DEPARTMENTS = {
    'Computer Science': ['CSE-A', 'CSE-B', 'AI&DS-A'],
    'Electronics Engineering': ['ECE-A', 'ECE-B'],
    'Mechanical Engineering': ['MECH-A', 'MECH-B'],
    'Civil Engineering': ['CIVIL-A'],
    'Information Technology': ['IT-A']
}

STAFF_count_PER_DEPT = 4
STUDENTS_PER_CLASS = 10

STUDENTS_CSV = 'data/students.csv'
STAFF_CSV = 'data/staff.csv'

# Data Pools
FIRST_NAMES = ['Aarav', 'Vihaan', 'Aditya', 'Arjun', 'Sai', 'Reyansh', 'Ayan', 'Krishna', 'Ishaan', 'Shaurya',
               'Diya', 'Saanvi', 'Ananya', 'Aadhya', 'Pari', 'Anika', 'Myra', 'Prisha', 'Ria', 'Anya']
LAST_NAMES = ['Sharma', 'Verma', 'Gupta', 'Malhotra', 'Bhatia', 'Saxena', 'Mehta', 'Jain', 'Singh', 'Kumar',
              'Reddy', 'Nair', 'Patel', 'Shah', 'Rao', 'Iyer', 'Menon', 'Pillai', 'Das', 'Chatterjee']
DESIGNATIONS = ['Professor', 'Associate Professor', 'Assistant Professor', 'Lecturer']

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_next_id(file_path, prefix):
    max_id = 0
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                uid = row.get('user_id', '')
                if uid.startswith(prefix):
                    try:
                        num = int(uid.replace(prefix, ''))
                        if num > max_id:
                            max_id = num
                    except ValueError:
                        pass
    return max_id + 1

def generate_students():
    current_id_num = get_next_id(STUDENTS_CSV, 'STU')
    students = []
    
    for dept, classes in DEPARTMENTS.items():
        for class_name in classes:
            for i in range(1, STUDENTS_PER_CLASS + 1):
                fname = random.choice(FIRST_NAMES)
                lname = random.choice(LAST_NAMES)
                name = f"{fname} {lname}"
                roll_no = f"{class_name.split('-')[0]}{100+i}" # e.g., CSE101
                
                student = {
                    'user_id': f"STU{current_id_num:03d}",
                    'name': name,
                    'email': f"{fname.lower()}.{lname.lower()}{current_id_num}@srec.ac.in",
                    'parent_email': f"parent.{fname.lower()}{current_id_num}@gmail.com",
                    'password': hash_password('password123'),
                    'class': class_name,
                    'roll_no': roll_no,
                    'department': dept,
                    'semester': random.choice(['1', '3', '5', '7']),
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'phone': f"9{''.join([str(random.randint(0,9)) for _ in range(9)])}",
                    'face_registered': 'False'
                }
                students.append(student)
                current_id_num += 1
                
    # Append to CSV
    file_exists = os.path.exists(STUDENTS_CSV)
    with open(STUDENTS_CSV, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['user_id','name','email','parent_email','password','class','roll_no','department','semester','created_at','phone','face_registered']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for s in students:
            writer.writerow(s)
            
    print(f"✅ Added {len(students)} students.")

def generate_staff():
    current_id_num = get_next_id(STAFF_CSV, 'STAFF')
    staff_list = []
    
    for dept in DEPARTMENTS.keys():
        for i in range(STAFF_count_PER_DEPT):
            fname = random.choice(FIRST_NAMES)
            lname = random.choice(LAST_NAMES)
            name = f"Dr. {fname} {lname}" if i == 0 else f"{fname} {lname}"
            
            staff = {
                'user_id': f"STAFF{current_id_num:03d}",
                'name': name,
                'email': f"{fname.lower()}.{lname.lower()}{current_id_num}@srec.ac.in",
                'password': hash_password('password123'),
                'department': dept,
                'designation': random.choice(DESIGNATIONS),
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'phone': f"9{''.join([str(random.randint(0,9)) for _ in range(9)])}"
            }
            staff_list.append(staff)
            current_id_num += 1
            
    # Append to CSV
    file_exists = os.path.exists(STAFF_CSV)
    with open(STAFF_CSV, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['user_id','name','email','password','department','designation','created_at','phone']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for s in staff_list:
            writer.writerow(s)

    print(f"✅ Added {len(staff_list)} staff members.")

if __name__ == "__main__":
    print("Generating sample data...")
    generate_students()
    generate_staff()
    print("Done!")
