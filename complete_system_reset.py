
import os
import shutil
import csv
from datetime import datetime

def complete_reset():
    """Complete system reset with proper structure"""
    
    print("\n" + "="*70)
    print("🔧 SMART ATTENDANCE SYSTEM - COMPLETE RESET")
    print("="*70)
    
    # Step 1: Backup existing data
    print("\n[1/5] Creating backup...")
    if os.path.exists('data'):
        backup_dir = f'data_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        try:
            shutil.copytree('data', backup_dir)
            print(f"✅ Backup created: {backup_dir}")
        except:
            print("⚠️ No backup needed")
    
    # Step 2: Clean everything
    print("\n[2/5] Cleaning old files...")
    if os.path.exists('data'):
        shutil.rmtree('data')
        print("✅ Removed old data directory")
    
    if os.path.exists('static/uploads/student_faces'):
        shutil.rmtree('static/uploads/student_faces')
        print("✅ Removed old face images")
    
    # Step 3: Create directories
    print("\n[3/5] Creating fresh directories...")
    directories = [
        'data',
        'static/uploads',
        'static/uploads/student_faces',
        'static/uploads/od_proofs',
        'models/saved_models'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}")
    
    # Step 4: Create CSV files with proper structure
    print("\n[4/5] Creating database files...")
    
    csv_files = {
        'data/students.csv': [
            'user_id', 'name', 'email', 'parent_email', 'password', 
            'class', 'roll_no', 'department', 'semester', 'created_at'
        ],
        'data/staff.csv': [
            'user_id', 'name', 'email', 'password', 'department', 
            'designation', 'created_at'
        ],
        'data/attendance.csv': [
            'student_id', 'date', 'time', 'status', 'subject', 
            'period', 'department', 'semester', 'marked_at'
        ],
        'data/od_requests.csv': [
            'request_id', 'student_id', 'date', 'start_time', 'end_time', 
            'reason', 'proof_file', 'status', 'submitted_at', 'approved_by', 
            'approved_at', 'remarks'
        ],
        'data/hostel_pass.csv': [
            'pass_id', 'student_id', 'out_date', 'out_time', 'in_date', 
            'in_time', 'reason', 'status', 'created_at', 'approved_by'
        ],
        'data/bus_attendance.csv': [
            'student_id', 'date', 'time', 'bus_number', 'route', 'status'
        ],
        'data/password_resets.csv': [
            'email', 'token', 'created_at', 'used'
        ]
    }
    
    for filepath, headers in csv_files.items():
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        print(f"✅ Created: {filepath} ({len(headers)} columns)")
    
    # Step 5: Test the system
    print("\n[5/5] Verifying system...")
    
    all_good = True
    for filepath in csv_files.keys():
        if not os.path.exists(filepath):
            print(f"❌ Missing: {filepath}")
            all_good = False
    
    if all_good:
        print("✅ All database files verified")
    
    print("\n" + "="*70)
    print("✅ SYSTEM RESET COMPLETE!")
    print("="*70)
    
    print("\n📋 NEXT STEPS:")
    print("-" * 70)
    print("1. Start the Flask application:")
    print("   python app.py")
    print()
    print("2. Open your browser:")
    print("   http://127.0.0.1:5000/face-registration/register")
    print()
    print("3. Register a new student:")
    print("   - Enter Student ID (e.g., CS2024001)")
    print("   - Enter Name")
    print("   - Enter Email")
    print("   - Enter Parent Email (optional)")
    print("   - Select Department")
    print("   - Capture 3 face photos")
    print("   - Complete registration")
    print()
    print("4. Mark attendance:")
    print("   http://127.0.0.1:5000/face-attendance/mark")
    print("-" * 70)
    
    print("\n💡 IMPORTANT NOTES:")
    print("-" * 70)
    print("✓ Database is now clean and properly structured")
    print("✓ Default password for new students: 'password'")
    print("✓ Face images will be stored in: static/uploads/student_faces/")
    print("✓ All CSV files use UTF-8 encoding")
    print("✓ Parent email field is now supported")
    print("-" * 70)
    
    print("\n🎉 Ready to use! Start with registration first.")
    print("="*70 + "\n")

if __name__ == "__main__":
    complete_reset()