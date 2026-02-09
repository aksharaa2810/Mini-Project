"""
Initialize database with demo users
Run this script once to create default users
"""

import os
import csv
import hashlib
from datetime import datetime

# CSV file paths
STUDENTS_CSV = 'data/students.csv'
STAFF_CSV = 'data/staff.csv'

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_csv_files():
    """Create CSV files with headers if they don't exist"""
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Students CSV structure
    if not os.path.exists(STUDENTS_CSV):
        with open(STUDENTS_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'name', 'email', 'parent_email', 'password', 'class', 'roll_no', 'department', 'semester', 'created_at', 'phone', 'face_registered', 'profile_image'])
        print(f"✓ Created {STUDENTS_CSV}")
    
    # Staff CSV structure
    if not os.path.exists(STAFF_CSV):
        with open(STAFF_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'name', 'email', 'password', 'department', 'designation', 'created_at', 'phone', 'profile_image'])
        print(f"✓ Created {STAFF_CSV}")

def add_demo_students():
    """Add demo student users"""
    
    demo_students = [
        {
            'user_id': 'STU001',
            'name': 'John Doe',
            'email': 'john@student.com',
            'password': 'password123',
            'class': 'CSE-A',
            'roll_no': '101'
        },
        {
            'user_id': 'STU002',
            'name': 'Jane Smith',
            'email': 'jane@student.com',
            'password': 'password123',
            'class': 'CSE-A',
            'roll_no': '102'
        },
        {
            'user_id': 'STU003',
            'name': 'Alice Johnson',
            'email': 'alice@student.com',
            'password': 'password123',
            'class': 'CSE-B',
            'roll_no': '103'
        },
        {
            'user_id': 'STU004',
            'name': 'Bob Wilson',
            'email': 'bob@student.com',
            'password': 'password123',
            'class': 'ECE-A',
            'roll_no': '104'
        },
        {
            'user_id': 'STU005',
            'name': 'Charlie Brown',
            'email': 'charlie@student.com',
            'password': 'password123',
            'class': 'MECH-A',
            'roll_no': '105'
        }
    ]
    
    with open(STUDENTS_CSV, 'a', newline='') as f:
        writer = csv.writer(f)
        for student in demo_students:
            writer.writerow([
                student['user_id'],
                student['name'],
                student['email'],
                hash_password(student['password']),
                student['class'],
                student['roll_no'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ])
    
    print(f"\n✓ Added {len(demo_students)} demo students")
    print("\nStudent Login Credentials:")
    print("-" * 50)
    for student in demo_students:
        print(f"User ID: {student['user_id']} | Password: {student['password']}")

def add_demo_staff():
    """Add demo staff and admin users"""
    
    demo_staff = [
        {
            'user_id': 'STAFF001',
            'name': 'Dr. Sarah Williams',
            'email': 'sarah@staff.com',
            'password': 'password123',
            'department': 'Computer Science',
            'designation': 'Professor'
        },
        {
            'user_id': 'STAFF002',
            'name': 'Prof. Michael Davis',
            'email': 'michael@staff.com',
            'password': 'password123',
            'department': 'Electronics',
            'designation': 'Associate Professor'
        },
        {
            'user_id': 'STAFF003',
            'name': 'Dr. Emily Clark',
            'email': 'emily@staff.com',
            'password': 'password123',
            'department': 'Mechanical',
            'designation': 'Assistant Professor'
        }
    ]
    
    demo_admin = [
        {
            'user_id': 'ADMIN001',
            'name': 'Admin User',
            'email': 'admin@system.com',
            'password': 'password123',
            'department': 'Administration',
            'designation': 'System Administrator'
        }
    ]
    
    all_users = demo_staff + demo_admin
    
    with open(STAFF_CSV, 'a', newline='') as f:
        writer = csv.writer(f)
        for user in all_users:
            writer.writerow([
                user['user_id'],
                user['name'],
                user['email'],
                hash_password(user['password']),
                user['department'],
                user['designation'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ])
    
    print(f"\n✓ Added {len(demo_staff)} demo staff members")
    print(f"✓ Added {len(demo_admin)} admin user")
    
    print("\nStaff Login Credentials:")
    print("-" * 50)
    for user in demo_staff:
        print(f"User ID: {user['user_id']} | Password: {user['password']}")
    
    print("\nAdmin Login Credentials:")
    print("-" * 50)
    for user in demo_admin:
        print(f"User ID: {user['user_id']} | Password: {user['password']}")

def create_other_csv_files():
    """Create other required CSV files"""
    
    csv_files = {
        'data/attendance.csv': ['student_id', 'date', 'time', 'status', 'subject', 'period', 'marked_by'],
        'data/od_requests.csv': ['request_id', 'student_id', 'date', 'start_time', 'end_time', 'reason', 
                                 'proof_file', 'status', 'submitted_at', 'approved_by', 'approved_at', 'remarks'],
        'data/hostel_pass.csv': ['pass_id', 'student_id', 'out_date', 'out_time', 'in_date', 'in_time', 
                                 'reason', 'status', 'created_at', 'approved_by'],
        'data/bus_attendance.csv': ['student_id', 'date', 'time', 'bus_number', 'route', 'status']
    }
    
    for filepath, headers in csv_files.items():
        if not os.path.exists(filepath):
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            print(f"✓ Created {filepath}")

def main():
    """Main initialization function"""
    
    print("=" * 60)
    print("DATABASE INITIALIZATION")
    print("=" * 60)
    
    # Step 1: Create CSV files with headers
    print("\n[1/4] Creating CSV files...")
    init_csv_files()
    
    # Step 2: Create other CSV files
    print("\n[2/4] Creating additional CSV files...")
    create_other_csv_files()
    
    # Step 3: Add demo students
    print("\n[3/4] Adding demo students...")
    add_demo_students()
    
    # Step 4: Add demo staff and admin
    print("\n[4/4] Adding demo staff and admin...")
    add_demo_staff()
    
    print("\n" + "=" * 60)
    print("✅ DATABASE INITIALIZATION COMPLETE!")
    print("=" * 60)
    
    print("\n📋 QUICK LOGIN GUIDE:")
    print("-" * 60)
    print("Student Login:")
    print("  User ID: STU001")
    print("  Password: password123")
    print("  Role: student")
    print()
    print("Staff Login:")
    print("  User ID: STAFF001")
    print("  Password: password123")
    print("  Role: staff")
    print()
    print("Admin Login:")
    print("  User ID: ADMIN001")
    print("  Password: password123")
    print("  Role: admin")
    print("-" * 60)
    
    print("\n🚀 You can now run the application:")
    print("   python app.py")
    print()

if __name__ == "__main__":
    main()