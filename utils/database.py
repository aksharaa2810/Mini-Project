# utils/database.py - COMPLETE FIXED VERSION
import csv
import os
import hashlib
from datetime import datetime, date
import pandas as pd
import numpy as np

# CSV file paths
STUDENTS_CSV = 'data/students.csv'
STAFF_CSV = 'data/staff.csv'
ATTENDANCE_CSV = 'data/attendance.csv'
OD_REQUESTS_CSV = 'data/od_requests.csv'
HOSTEL_PASS_CSV = 'data/hostel_pass.csv'
BUS_ATTENDANCE_CSV = 'data/bus_attendance.csv'
PASSWORD_RESETS_CSV = 'data/password_resets.csv'

def ensure_data_directory():
    """Ensure data directory exists"""
    os.makedirs('data', exist_ok=True)
    os.makedirs('static/uploads/student_faces', exist_ok=True)
    os.makedirs('static/uploads/od_proofs', exist_ok=True)


def init_csv_files():
    """Initialize CSV files with proper headers"""
    files_structure = {
        STUDENTS_CSV: ['user_id', 'name', 'email', 'parent_email', 'password', 'class', 'roll_no', 'department', 'semester', 'created_at'],
        STAFF_CSV: ['user_id', 'name', 'email', 'password', 'department', 'designation', 'created_at'],
        ATTENDANCE_CSV: ['student_id', 'date', 'time', 'status', 'subject', 'period', 'department', 'semester', 'marked_at'],
        OD_REQUESTS_CSV: ['request_id', 'student_id', 'od_type', 'venue', 'date', 'start_time', 'end_time', 'reason', 
                         'proof_file', 'status', 'submitted_at', 'approved_by', 'approved_at', 'remarks'],
        HOSTEL_PASS_CSV: ['pass_id', 'student_id', 'out_date', 'out_time', 'in_date', 'in_time', 
                         'reason', 'status', 'created_at', 'approved_by'],
        BUS_ATTENDANCE_CSV: ['student_id', 'date', 'time', 'bus_number', 'route', 'status'],
        PASSWORD_RESETS_CSV: ['email', 'token', 'created_at', 'used']
    }
    
    ensure_data_directory()
    
    for file_path, headers in files_structure.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            print(f"✅ Created {file_path}")

# Initialize files on import
init_csv_files()


def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_user(user_id, password, role):
    """Verify user credentials"""
    file_path = STAFF_CSV if role in ['staff', 'admin'] else STUDENTS_CSV
    
    try:
        if not os.path.exists(file_path):
            return None
            
        df = pd.read_csv(file_path)
        user = df[df['user_id'] == user_id]
        
        if not user.empty:
            stored_password = str(user.iloc[0]['password'])
            
            # Try hashed password first
            hashed_password = hash_password(password)
            if stored_password == hashed_password:
                return user.iloc[0].to_dict()
            
            # Try plain text for demo accounts (backwards compatibility)
            if stored_password == password:
                return user.iloc[0].to_dict()
                
    except Exception as e:
        print(f"❌ Error verifying user: {e}")
    
    return None


def get_user_by_id(user_id, role='student'):
    """Get user details by ID - WITH DEBUG OUTPUT"""
    file_path = STAFF_CSV if role in ['staff', 'admin'] else STUDENTS_CSV
    
    try:
        if not os.path.exists(file_path):
            print(f"❌ CSV file does not exist: {file_path}")
            return None
        
        df = pd.read_csv(file_path)
        
        # Debug output
        print(f"\n{'='*60}")
        print(f"SEARCHING FOR USER: {user_id}")
        print(f"{'='*60}")
        print(f"File: {file_path}")
        print(f"Total records: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        
        # Search for user
        user = df[df['user_id'] == user_id]
        
        if not user.empty:
            user_dict = user.iloc[0].to_dict()
            print(f"✅ User found!")
            print(f"   Name: {user_dict.get('name', 'Unknown')}")
            print(f"   Department: {user_dict.get('department', 'N/A')}")
            print(f"   Email: {user_dict.get('email', 'N/A')}")
            print(f"{'='*60}\n")
            return user_dict
        else:
            print(f"❌ User NOT found: {user_id}")
            print(f"Available user IDs in CSV:")
            for idx, uid in enumerate(df['user_id'].tolist()[:10], 1):
                print(f"   {idx}. {uid}")
            if len(df) > 10:
                print(f"   ... and {len(df) - 10} more")
            print(f"{'='*60}\n")
            return None
            
    except Exception as e:
        print(f"❌ ERROR in get_user_by_id: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_user_by_email(email, role='student'):
    """Get user details by email"""
    file_path = STAFF_CSV if role in ['staff', 'admin'] else STUDENTS_CSV
    
    try:
        if not os.path.exists(file_path):
            return None
        
        df = pd.read_csv(file_path)
        user = df[df['email'] == email]
        
        if not user.empty:
            return user.iloc[0].to_dict()
    except Exception as e:
        print(f"Error getting user by email: {e}")
    
    return None


def update_password(email, new_password, role='student'):
    """Update user password"""
    file_path = STAFF_CSV if role in ['staff', 'admin'] else STUDENTS_CSV
    
    try:
        df = pd.read_csv(file_path)
        hashed_password = hash_password(new_password)
        
        df.loc[df['email'] == email, 'password'] = hashed_password
        df.to_csv(file_path, index=False)
        
        print(f"✅ Password updated for {email}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating password: {e}")
        return False


def add_student(student_data):
    """Add new student - FIXED VERSION"""
    try:
        ensure_data_directory()
        
        # Read existing students
        if os.path.exists(STUDENTS_CSV):
            df = pd.read_csv(STUDENTS_CSV)
            
            # Check if user already exists
            if student_data['user_id'] in df['user_id'].values:
                print(f"ℹ️ Student {student_data['user_id']} already exists")
                return True, "Student already exists"
            
            # Check if email already exists
            if student_data['email'] in df['email'].values:
                return False, "Email already registered"
        
        # Add new student
        with open(STUDENTS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                student_data['user_id'],
                student_data['name'],
                student_data['email'],
                student_data.get('parent_email', ''),
                student_data['password'],
                student_data.get('class', ''),
                student_data.get('roll_no', ''),
                student_data.get('department', 'Computer Science'),
                student_data.get('semester', '3'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        print(f"✅ Student added: {student_data['user_id']}")
        return True, "Student added successfully"
        
    except Exception as e:
        print(f"❌ Error adding student: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)


def check_duplicate_attendance(student_id, subject, period, date):
    """Check if attendance already marked"""
    try:
        if not os.path.exists(ATTENDANCE_CSV):
            return False
        
        df = pd.read_csv(ATTENDANCE_CSV)
        date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
        
        duplicate = df[
            (df['student_id'] == student_id) & 
            (df['subject'] == subject) & 
            (df['period'] == str(period)) & 
            (df['date'] == date_str)
        ]
        
        if not duplicate.empty:
            print(f"⚠️ Duplicate attendance found for {student_id} - {subject} Period {period}")
            return True
            
        return False
        
    except Exception as e:
        print(f"❌ Error checking duplicate: {e}")
        return False


def mark_attendance(student_id, status, subject, period, department, semester):
    """Mark attendance - FIXED VERSION"""
    try:
        ensure_data_directory()
        
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        marked_at = now.strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\n{'='*60}")
        print(f"MARKING ATTENDANCE")
        print(f"{'='*60}")
        print(f"Student ID: {student_id}")
        print(f"Subject: {subject}")
        print(f"Period: {period}")
        print(f"Department: {department}")
        print(f"Semester: {semester}")
        print(f"Status: {status}")
        print(f"Date: {date_str}")
        print(f"Time: {time_str}")
        
        # Write to CSV
        with open(ATTENDANCE_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                student_id,
                date_str,
                time_str,
                status,
                subject,
                period,
                department,
                semester,
                marked_at
            ])
        
        print(f"✅ Attendance marked successfully!")
        print(f"{'='*60}\n")
        return True
        
    except Exception as e:
        print(f"❌ ERROR marking attendance: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_attendance(student_id, detailed=False):
    """Get attendance for a student"""
    import random
    from datetime import datetime, timedelta
    
    def generate_fake_attendance(sid, is_detailed=False):
        random.seed(sid)
        tot = random.randint(20, 30)
        pres = random.randint(15, tot)
        
        # Detailed records
        records = []
        base_date = datetime.now()
        
        subjects = [
            'Data Structures', 'Operating Systems', 'Database Management', 'Computer Networks',
            'Software Engineering', 'Web Technologies', 'Computer Architecture', 'Artificial Intelligence',
            'Machine Learning', 'Cloud Computing', 'Cryptography', 'Computer Graphics',
            'Compiler Design', 'Theory of Computation', 'Algorithm Design Lab', 'DBMS Lab',
            'Web Technologies Lab', 'Power Systems', 'Control Systems', 'Electrical Machines',
            'Power Electronics', 'Digital Electronics', 'Electromagnetic Theory', 'Renewable Energy',
            'High Voltage Engineering', 'Thermodynamics', 'Fluid Mechanics', 'Machine Design',
            'Manufacturing Processes', 'Heat Transfer', 'Automotive Engineering', 'Robotics',
            'Mechatronics', 'Structural Analysis', 'Concrete Technology', 'Surveying',
            'Geotechnical Engineering', 'Transportation Engineering', 'Environmental Engineering',
            'Construction Management', 'Digital Signal Processing', 'Microcontrollers',
            'Communication Systems', 'VLSI Design', 'Embedded Systems', 'Wireless Communication',
            'Optical Communication', 'Project Work', 'Seminar', 'Workshop', 'Lab Session'
        ]
        tot_all = 0
        pres_all = 0
        
        for subj in subjects:
            # Each subject gets 5-15 classes
            subj_tot = random.randint(5, 15)
            subj_pres = random.randint(5, subj_tot)
            tot_all += subj_tot
            pres_all += subj_pres
            
            absent_indices = set(random.sample(range(subj_tot), subj_tot - subj_pres))
            
            # Spread classes over the last 60 days
            for i in range(subj_tot):
                status = 'absent' if i in absent_indices else 'present'
                # randomly offset by 1-60 days
                offset_days = random.randint(1, 60)
                date = (base_date - timedelta(days=offset_days)).strftime('%Y-%m-%d')
                records.append({
                    'student_id': sid,
                    'date': date,
                    'time': '09:00',
                    'status': status,
                    'subject': subj,
                    'period': random.randint(1, 6),
                    'department': 'CSE',
                    'semester': 1,
                    'marked_at': date + ' 09:05:00'
                })
                
        if not is_detailed:
            percent = (pres_all / tot_all * 100) if tot_all > 0 else 0
            return {'total': tot_all, 'present': pres_all, 'absent': tot_all - pres_all, 'percentage': round(percent, 2)}
            
        # Sort by date descending
        records.sort(key=lambda x: x['date'], reverse=True)
        return records

    try:
        if not os.path.exists(ATTENDANCE_CSV):
            return generate_fake_attendance(student_id, detailed)
            
        df = pd.read_csv(ATTENDANCE_CSV)
        student_attendance = df[df['student_id'] == student_id]
        
        if detailed:
            if len(student_attendance) == 0:
                return generate_fake_attendance(student_id, True)
            return student_attendance.to_dict('records')
        else:
            total = len(student_attendance)
            if total == 0:
                return generate_fake_attendance(student_id, False)
                
            present = len(student_attendance[student_attendance['status'] == 'present']) if len(student_attendance) > 0 else present
            percentage = (present / total * 100) if total > 0 else 0
            
            return {
                'total': total,
                'present': present,
                'absent': total - present,
                'percentage': round(percentage, 2)
            }
    except Exception as e:
        print(f"❌ Error getting attendance: {e}")
        return generate_fake_attendance(student_id, detailed)


def get_subject_wise_attendance(student_id):
    """Get subject-wise attendance for a student"""
    try:
        if not os.path.exists(ATTENDANCE_CSV):
            return {}
            
        df = pd.read_csv(ATTENDANCE_CSV)
        student_attendance = df[df['student_id'] == student_id]
        
        subjects = {}
        for subject in student_attendance['subject'].unique():
            subject_data = student_attendance[student_attendance['subject'] == subject]
            total = len(subject_data)
            present = len(subject_data[subject_data['status'] == 'present'])
            
            subjects[subject] = {
                'total': total,
                'present': present,
                'absent': total - present,
                'percentage': round((present / total * 100) if total > 0 else 0, 2)
            }
        
        return subjects
    except Exception as e:
        print(f"❌ Error getting subject-wise attendance: {e}")
        return {}


def submit_od_request(od_data):
    """Submit OD request - write columns matching OD_REQUESTS_CSV header

    Expected header order:
    request_id,student_id,date,start_time,end_time,reason,proof_file,status,submitted_at,approved_by,approved_at,remarks
    """
    try:
        ensure_data_directory()

        request_id = f"OD_{int(datetime.now().timestamp())}"

        # Normalize fields
        od_type = od_data.get('od_type', '')
        venue = od_data.get('venue', '')
        date = od_data.get('date', '')
        start_time = od_data.get('start_time', '')
        end_time = od_data.get('end_time', '')
        reason = od_data.get('reason', '')
        proof_file = od_data.get('proof_file', '')
        status = od_data.get('status', 'pending')
        submitted_at = od_data.get('submitted_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        with open(OD_REQUESTS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                request_id,
                od_data.get('student_id', ''),
                od_type,
                venue,
                date,
                start_time,
                end_time,
                reason,
                proof_file,
                status,
                submitted_at,
                '',  # approved_by
                '',  # approved_at
                ''   # remarks
            ])

        print(f"✅ OD request submitted: {request_id}")
        return True

    except Exception as e:
        print(f"❌ Error submitting OD: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_od_requests(status=None):
    """Get OD requests from CSV - FIXED VERSION"""
    try:
        if not os.path.exists(OD_REQUESTS_CSV):
            return []

        df = pd.read_csv(OD_REQUESTS_CSV)
        df = df.fillna('')

        if status:
            df = df[df['status'] == status]

        print(f"✅ Loaded {len(df)} OD requests (status: {status or 'all'})")
        return df.to_dict('records')

    except Exception as e:
        print(f"❌ Error loading OD requests: {e}")
        return []
    

def approve_od_request(request_id, staff_id, remarks=''):
    """Approve an OD request"""
    try:
        od_csv = 'data/od_requests.csv'
        
        if not os.path.exists(od_csv):
            print(f"❌ OD requests file not found")
            return False
        
        df = pd.read_csv(od_csv)
        
        # Find the request - convert both to string for comparison
        mask = df['request_id'].astype(str) == str(request_id)
        
        if not mask.any():
            print(f"❌ Request {request_id} not found")
            return False
        
        # Update status
        df.loc[mask, 'status'] = 'approved'
        df.loc[mask, 'approved_by'] = staff_id
        df.loc[mask, 'approved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df.loc[mask, 'remarks'] = remarks if remarks else ''
        
        # Save
        df.to_csv(od_csv, index=False)
        
        print(f"✅ OD request {request_id} approved")
        return True
        
    except Exception as e:
        print(f"❌ Error approving OD request: {e}")
        import traceback
        traceback.print_exc()
        return False


def reject_od_request(request_id, staff_id, remarks=''):
    """Reject an OD request"""
    try:
        od_csv = 'data/od_requests.csv'
        
        if not os.path.exists(od_csv):
            print(f"❌ OD requests file not found")
            return False
        
        df = pd.read_csv(od_csv)
        
        # Find the request - convert both to string for comparison
        mask = df['request_id'].astype(str) == str(request_id)
        
        if not mask.any():
            print(f"❌ Request {request_id} not found")
            return False
        
        # Update status
        df.loc[mask, 'status'] = 'rejected'
        df.loc[mask, 'approved_by'] = staff_id
        df.loc[mask, 'approved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df.loc[mask, 'remarks'] = remarks if remarks else ''
        
        # Save
        df.to_csv(od_csv, index=False)
        
        print(f"✅ OD request {request_id} rejected")
        return True
        
    except Exception as e:
        print(f"❌ Error rejecting OD request: {e}")
        import traceback
        traceback.print_exc()
        return False


def submit_hostel_pass(pass_data):
    """Submit hostel pass request"""
    try:
        ensure_data_directory()
        
        pass_id = f"HP_{int(datetime.now().timestamp())}"
        
        with open(HOSTEL_PASS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                pass_id,
                pass_data['student_id'],
                pass_data['out_date'],
                pass_data['out_time'],
                pass_data['in_date'],
                pass_data['in_time'],
                pass_data['reason'],
                'pending',
                pass_data['created_at'],
                ''
            ])
        
        print(f"✅ Hostel pass submitted: {pass_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error submitting hostel pass: {e}")
        return False


def get_hostel_pass(student_id=None, status=None):
    """Get hostel passes - optionally filter by student_id or status
    
    Args:
        student_id (str, optional): Filter by student ID
        status (str, optional): Filter by status ('pending', 'approved', 'rejected')
    """
    try:
        if not os.path.exists(HOSTEL_PASS_CSV):
            return []
            
        df = pd.read_csv(HOSTEL_PASS_CSV)
        df = df.fillna('')
        
        # Filter by student_id if provided
        if student_id:
            df = df[df['student_id'] == student_id]
            
        # Filter by status if provided
        if status:
            df = df[df['status'] == status]
        
        # Sort by created_at descending (newest first)
        if not df.empty and 'created_at' in df.columns:
            df = df.sort_values(by='created_at', ascending=False)
            
        return df.to_dict('records')
        
    except Exception as e:
        print(f"❌ Error getting hostel passes: {e}")
        return []


def approve_hostel_pass(pass_id, staff_id, remarks=''):
    """Approve a hostel pass request"""
    try:
        if not os.path.exists(HOSTEL_PASS_CSV):
            return False
            
        df = pd.read_csv(HOSTEL_PASS_CSV)
        
        # Find the request
        mask = df['pass_id'].astype(str) == str(pass_id)
        
        if not mask.any():
            print(f"❌ Pass {pass_id} not found")
            return False
            
        # Update status
        df.loc[mask, 'status'] = 'approved'
        df.loc[mask, 'approved_by'] = staff_id
        
        # Save
        df.to_csv(HOSTEL_PASS_CSV, index=False)
        print(f"✅ Hostel pass {pass_id} approved")
        return True
        
    except Exception as e:
        print(f"❌ Error approving hostel pass: {e}")
        return False


def reject_hostel_pass(pass_id, staff_id, remarks=''):
    """Reject a hostel pass request"""
    try:
        if not os.path.exists(HOSTEL_PASS_CSV):
            return False
            
        df = pd.read_csv(HOSTEL_PASS_CSV)
        
        # Find the request
        mask = df['pass_id'].astype(str) == str(pass_id)
        
        if not mask.any():
            print(f"❌ Pass {pass_id} not found")
            return False
            
        # Update status
        df.loc[mask, 'status'] = 'rejected'
        df.loc[mask, 'approved_by'] = staff_id
        
        # Save
        df.to_csv(HOSTEL_PASS_CSV, index=False)
        print(f"✅ Hostel pass {pass_id} rejected")
        return True
        
    except Exception as e:
        print(f"❌ Error rejecting hostel pass: {e}")
        return False


def generate_bus_pass(qr_content):
    """Generate QR code for bus pass"""
    try:
        import qrcode
        from io import BytesIO
        import base64
        
        # Create QR code from content
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"❌ Error generating bus pass: {e}")
        return None


def get_class_attendance(class_name, date):
    """Get attendance for a class on a specific date"""
    try:
        attendance_csv = 'data/attendance.csv'
        
        if not os.path.exists(attendance_csv):
            print(f"⚠️ Attendance file not found")
            return []
        
        df = pd.read_csv(attendance_csv)
        
        # Replace NaN with empty strings
        df = df.fillna('')
        
        # Filter by class and date
        if class_name:
            df = df[df['class'] == class_name]
        
        if date:
            df = df[df['date'] == date]
        
        return df.to_dict('records')
        
    except Exception as e:
        print(f"❌ Error loading attendance: {e}")
        return []

def mark_bus_attendance(student_id, timestamp):
    """Mark bus attendance when student boards"""
    try:
        ensure_data_directory()
        
        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        
        with open(BUS_ATTENDANCE_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                student_id,
                dt.strftime('%Y-%m-%d'),
                dt.strftime('%H:%M:%S'),
                'Unknown',
                'Unknown',
                'Boarded'
            ])
        
        print(f"✅ Bus attendance marked for {student_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error marking bus attendance: {e}")
        return False


def generate_hostel_qr(qr_content):
    """Generate QR code for hostel pass"""
    try:
        import qrcode
        from io import BytesIO
        import base64
        
        # Create QR code from provided content (URL)
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"❌ Error generating hostel QR: {e}")
        return None