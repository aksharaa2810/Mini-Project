"""
Clean initialization script - No demo data
Run this to set up clean CSV files with proper structure
"""

import pandas as pd
import os

def init_clean_system():
    """Initialize system with empty CSV files (no demo data)"""
    
    print("\n" + "="*60)
    print("INITIALIZING CLEAN ATTENDANCE SYSTEM")
    print("="*60)
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    print("\n✓ Created data directory")
    
    # Define CSV structures with ALL required columns
    csv_files = {
        'data/staff.csv': {
            'columns': ['user_id', 'name', 'email', 'password', 'department', 'designation', 'created_at'],
            'description': 'Staff accounts (passwords will be hashed)'
        },
        'data/students.csv': {
            # Complete structure matching database.py and face_registration.py
            'columns': ['user_id', 'name', 'email', 'parent_email', 'password', 'class', 'roll_no', 'department', 'semester', 'created_at'],
            'description': 'Student accounts with parent email support'
        },
        'data/attendance.csv': {
            # Complete structure matching database.py mark_attendance function
            'columns': ['student_id', 'date', 'time', 'status', 'subject', 'period', 'department', 'semester', 'marked_at'],
            'description': 'Daily attendance records'
        },
        'data/od_requests.csv': {
            'columns': ['request_id', 'student_id', 'student_name', 'class', 'date', 'start_time', 
                       'end_time', 'od_type', 'reason', 'venue', 'status', 'submitted_at', 
                       'approved_by', 'approved_at', 'remarks'],
            'description': 'On-duty requests'
        },
        'data/hostel_pass.csv': {
            'columns': ['pass_id', 'student_id', 'student_name', 'room_no', 'out_date', 'out_time', 
                       'in_date', 'in_time', 'reason', 'destination', 'status', 'approved_by'],
            'description': 'Hostel outpass records'
        },
        'data/bus_attendance.csv': {
            'columns': ['student_id', 'date', 'time', 'bus_number', 'route', 'status'],
            'description': 'Bus attendance tracking'
        },
        'data/password_resets.csv': {
            'columns': ['email', 'token', 'created_at', 'used'],
            'description': 'Password reset tokens'
        }
    }
    
    print("\nCreating CSV files:\n")
    
    for filepath, info in csv_files.items():
        # Create empty DataFrame with columns
        df = pd.DataFrame(columns=info['columns'])
        df.to_csv(filepath, index=False)
        print(f"✓ {filepath}")
        print(f"  └─ {info['description']}")
        print(f"  └─ Columns: {len(info['columns'])}")
        print()
    
    print("="*60)
    print("✅ SYSTEM INITIALIZED SUCCESSFULLY")
    print("="*60)
    
    print("\n📋 NEXT STEPS:")
    print("-" * 60)
    print("1. Start the Flask application:")
    print("   python app.py")
    print()
    print("2. Open browser and go to:")
    print("   http://127.0.0.1:5000")
    print()
    print("3. Register students with face:")
    print("   Go to Face Registration page")
    print("   Enter Student ID, Name, Email, Parent Email, Department")
    print("   Capture 3 face images")
    print()
    print("4. Mark attendance:")
    print("   Go to Face Attendance page")
    print("   Students can mark attendance during class periods")
    print("-" * 60)
    
    print("\n🔒 SECURITY NOTES:")
    print("-" * 60)
    print("✓ No demo accounts created")
    print("✓ All passwords will be hashed (SHA-256)")
    print("✓ Clean database ready for production")
    print("✓ Default password for new students: 'password'")
    print("✓ Parent email notifications supported")
    print("-" * 60)
    
    # Create static directories
    static_dirs = [
        'static/uploads',
        'static/uploads/student_faces',
        'static/uploads/od_proofs',
        'static/css',
        'static/js',
        'models/saved_models'
    ]
    
    print("\n\nCreating required directories:")
    for directory in static_dirs:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ {directory}")
    
    print("\n" + "="*60)
    print("🎉 ALL DONE! You can now start the application.")
    print("="*60)
    
    print("\n💡 TIPS:")
    print("-" * 60)
    print("• Configure email settings in config.py for notifications")
    print("• Update MAIL_USERNAME and MAIL_PASSWORD for Gmail")
    print("• Parent emails will receive attendance notifications")
    print("• Face recognition models will be created automatically")
    print("-" * 60 + "\n")

if __name__ == "__main__":
    init_clean_system()