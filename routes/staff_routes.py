from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from utils.database import get_class_attendance, get_od_requests, approve_od_request, reject_od_request, get_hostel_pass, approve_hostel_pass, reject_hostel_pass
from datetime import datetime
import pandas as pd
import os
from utils.email_service import send_attendance_report
from utils.database import get_attendance, get_user_by_id

bp = Blueprint('staff', __name__, url_prefix='/staff')

def staff_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'staff':
            flash('Access denied!', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/send-parent-reports', methods=['POST'])
@staff_required
def send_parent_reports():
    """Send attendance reports to all parents via email"""
    try:
        from utils.email_service import send_attendance_report
        import pandas as pd
        
        # Read data files
        students_df = pd.read_csv('data/students.csv')
        attendance_df = pd.read_csv('data/attendance.csv')
        
        sent = 0
        failed = 0
        
        # Loop through each student
        for _, student in students_df.iterrows():
            parent_email = str(student.get('parent_email', '')).strip()
            student_id = student['user_id']
            student_name = student['name']
            
            # Validate email
            if not parent_email or '@' not in parent_email:
                print(f"⚠️ Skipping invalid email for {student_name}: {parent_email}")
                failed += 1
                continue
            
            # Calculate attendance stats for this student
            stu_att = attendance_df[attendance_df['student_id'] == student_id]
            total = len(stu_att)
            present = len(stu_att[stu_att['status'] == 'Present'])
            absent = len(stu_att[stu_att['status'] == 'Absent'])
            percentage = round((present / total) * 100, 2) if total > 0 else 0
            
            # Prepare data for email
            data = {
                'total': total,
                'present': present,
                'absent': absent,
                'percentage': percentage
            }
            
            # Send email
            print(f"📧 Sending report to {parent_email} for {student_name}")
            ok = send_attendance_report(parent_email, student_name, data)
            
            if ok:
                sent += 1
                print(f"✅ Email sent successfully to {parent_email}")
            else:
                failed += 1
                print(f"❌ Failed to send email to {parent_email}")
        
        return jsonify({
            'status': 'success',
            'sent': sent,
            'failed': failed
        })
        
    except FileNotFoundError as e:
        print(f"❌ ERROR: Data file not found - {e}")
        return jsonify({
            'status': 'error',
            'message': 'Data files not found'
        }), 500
        
    except Exception as e:
        print("❌ ERROR sending parent reports:", e)
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/dashboard')
@staff_required
def dashboard():
    staff_id = session.get('user_id')
    name = session.get('name')
    
    # Get today's date
    today = datetime.now()
    current_date = today.strftime('%A, %B %d, %Y')
    
    # Get statistics
    try:
        # Count total students
        students_csv = 'data/students.csv'
        if os.path.exists(students_csv):
            df = pd.read_csv(students_csv)
            total_students = len(df)
        else:
            total_students = 0
        
        # Get pending OD requests
        pending_ods = len(get_od_requests(status='pending'))
        
        # Calculate today's attendance (placeholder - implement based on your database)
        today_attendance = 85  # Default value
        
        # Classes today (placeholder)
        classes_today = 4
        
        # Get today's schedule (placeholder data)
        schedule = [
            {
                'period': '1',
                'start': '09:00',
                'end': '10:00',
                'class_name': 'CSE-A',
                'subject': 'Data Structures',
                'room': 'CS-101',
                'completed': True,
                'is_current': False
            },
            {
                'period': '2',
                'start': '10:00',
                'end': '11:00',
                'class_name': 'CSE-A',
                'subject': 'Algorithms',
                'room': 'CS-101',
                'completed': False,
                'is_current': True
            },
            {
                'period': '3',
                'start': '11:15',
                'end': '12:15',
                'class_name': 'CSE-B',
                'subject': 'Database Systems',
                'room': 'CS-102',
                'completed': False,
                'is_current': False
            }
        ]
        
        # Get pending OD list (first 5)
        pending_od_list = get_od_requests(status='pending')[:5] if get_od_requests(status='pending') else []
        
        # Recent activity (placeholder)
        recent_activity = [
            {
                'time': datetime.now().strftime('%I:%M %p'),
                'message': 'Attendance marked for CSE-A Period 1'
            },
            {
                'time': (datetime.now().replace(hour=datetime.now().hour-1)).strftime('%I:%M %p'),
                'message': 'OD request approved for student ST001'
            }
        ]
        
    except Exception as e:
        print(f"Error loading dashboard data: {e}")
        total_students = 0
        pending_ods = 0
        today_attendance = 0
        classes_today = 0
        schedule = []
        pending_od_list = []
        recent_activity = []
    
    return render_template('staff/dashboard.html', 
                         name=name,
                         current_date=current_date,
                         total_students=total_students,
                         pending_ods=pending_ods,
                         today_attendance=today_attendance,
                         classes_today=classes_today,
                         schedule=schedule,
                         pending_od_list=pending_od_list,
                         recent_activity=recent_activity)

@bp.route('/view-attendance')
@staff_required
def view_attendance():
    class_name = request.args.get('class', '')
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    period = request.args.get('period', '')
    
    try:
        # Get attendance data
        attendance_data = get_class_attendance(class_name, date)
        
        # Calculate summary
        total = len(attendance_data) if attendance_data else 0
        present = sum(1 for a in attendance_data if a.get('status') == 'present') if attendance_data else 0
        absent = sum(1 for a in attendance_data if a.get('status') == 'absent') if attendance_data else 0
        percentage = round((present / total * 100) if total > 0 else 0, 2)
        
        attendance_summary = {
            'total': total,
            'present': present,
            'absent': absent,
            'percentage': percentage
        }
        
        # Get defaulters (students below 75%)
        defaulters = []  # Implement based on your database
        
    except Exception as e:
        print(f"Error loading attendance: {e}")
        attendance_data = []
        attendance_summary = {'total': 0, 'present': 0, 'absent': 0, 'percentage': 0}
        defaulters = []
    
    return render_template('staff/view_attendance.html', 
                         attendance=attendance_data,
                         selected_class=class_name,
                         selected_date=date,
                         attendance_summary=attendance_summary,
                         defaulters=defaulters)

@bp.route('/od-details/<request_id>')
@staff_required
def od_details(request_id):
    """Get OD request details for modal"""
    try:
        # Get OD details from database
        od_requests = get_od_requests()
        
        # Debug: Print to check data
        print(f"🔍 Looking for request_id: {request_id}")
        print(f"📋 Available requests: {[req.get('request_id') for req in od_requests]}")
        
        # Try to find the request - handle both string and different ID formats
        od_request = None
        for req in od_requests:
            if str(req.get('request_id')) == str(request_id):
                od_request = req
                break
        
        if od_request:
            print(f"✅ Found OD request: {od_request}")
            
            # Extra cleaning for JSON serialization
            cleaned_request = {}
            for key, value in od_request.items():
                if value is None or value == '' or str(value).lower() == 'nan':
                    cleaned_request[key] = ''
                else:
                    cleaned_request[key] = str(value)
            
            return jsonify(cleaned_request)
        else:
            print(f"❌ Request not found: {request_id}")
            return jsonify({'error': 'Request not found'}), 404
            
    except Exception as e:
        print(f"❌ Error in od_details: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/od-approval')
@staff_required
def od_approval():
    status = request.args.get('status', 'pending')
    
    try:
        od_requests = get_od_requests(status=status)
        pending_count = len(get_od_requests(status='pending'))
    except Exception as e:
        print(f"Error loading OD requests: {e}")
        od_requests = []
        pending_count = 0
    
    return render_template('staff/od_approval.html', 
                         requests=od_requests,
                         status=status,
                         pending_count=pending_count)

@bp.route('/od-approve/<request_id>', methods=['POST'])
@staff_required
def od_approve(request_id):
    staff_id = session.get('user_id')
    remarks = request.form.get('remarks', '')
    
    try:
        if approve_od_request(request_id, staff_id, remarks):
            flash('OD request approved!', 'success')
            return jsonify({'success': True})
        else:
            flash('Failed to approve OD request!', 'error')
            return jsonify({'success': False}), 500
    except Exception as e:
        print(f"Error approving OD: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/od-reject/<request_id>', methods=['POST'])
@staff_required
def od_reject(request_id):
    staff_id = session.get('user_id')
    remarks = request.form.get('remarks', '')
    
    try:
        if reject_od_request(request_id, staff_id, remarks):
            flash('OD request rejected!', 'success')
            return jsonify({'success': True})
        else:
            flash('Failed to reject OD request!', 'error')
            return jsonify({'success': False}), 500
    except Exception as e:
        print(f"Error rejecting OD: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/hostel-approval')
@staff_required
def hostel_approval():
    status = request.args.get('status', 'pending')
    
    try:
        hostel_passes = get_hostel_pass(status=status)
        pending_count = len(get_hostel_pass(status='pending'))
    except Exception as e:
        print(f"Error loading hostel passes: {e}")
        hostel_passes = []
        pending_count = 0
    
    return render_template('staff/hostel_approval.html', 
                         passes=hostel_passes,
                         status=status,
                         pending_count=pending_count)


@bp.route('/hostel-approve/<pass_id>', methods=['POST'])
@staff_required
def hostel_approve(pass_id):
    staff_id = session.get('user_id')
    remarks = request.form.get('remarks', '')
    
    try:
        if approve_hostel_pass(pass_id, staff_id, remarks):
            flash('Hostel pass approved!', 'success')
            return jsonify({'success': True})
        else:
            flash('Failed to approve hostel pass!', 'error')
            return jsonify({'success': False}), 500
    except Exception as e:
        print(f"Error approving hostel pass: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/hostel-reject/<pass_id>', methods=['POST'])
@staff_required
def hostel_reject(pass_id):
    staff_id = session.get('user_id')
    remarks = request.form.get('remarks', '')
    
    try:
        if reject_hostel_pass(pass_id, staff_id, remarks):
            flash('Hostel pass rejected!', 'success')
            return jsonify({'success': True})
        else:
            flash('Failed to reject hostel pass!', 'error')
            return jsonify({'success': False}), 500
    except Exception as e:
        print(f"Error rejecting hostel pass: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/reports')
@staff_required
def reports():
    # Placeholder statistics
    today_stats = {'percentage': 85, 'present': 42, 'total': 50}
    week_stats = {'percentage': 82}
    month_stats = {'percentage': 84}
    recent_reports = []
    
    return render_template('staff/reports.html',
                         today_stats=today_stats,
                         week_stats=week_stats,
                         month_stats=month_stats,
                         recent_reports=recent_reports)

@bp.route('/generate-report', methods=['POST'])
@staff_required
def generate_report():
    """Generate report file"""
    # Implement report generation
    return jsonify({'message': 'Report generation not implemented yet'}), 501

@bp.route('/preview-report', methods=['POST'])
@staff_required
def preview_report():
    """Preview report data"""
    # Placeholder data
    data = {
        'summary': {
            'total': 50,
            'present': 42,
            'absent': 8,
            'od': 3,
            'percentage': 84
        },
        'students': [],
        'trend': {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
            'values': [85, 82, 88, 84, 86]
        }
    }
    return jsonify(data)

@bp.route('/send-report-email', methods=['POST'])
@staff_required
def send_report_email():
    """Send attendance report to parent via email"""
    try:
        data = request.get_json()
        
        parent_email = data.get('parent_email')
        student_name = data.get('student_name')
        attendance_data = data.get('attendance_data', {})
        
        # Validate inputs
        if not parent_email or not student_name:
            return jsonify({
                'success': False, 
                'message': 'Missing required fields'
            }), 400
        
        # Import email service
        from utils.email_service import send_attendance_report
        
        # Send email with timeout
        print(f"📧 Sending report to {parent_email} for {student_name}")
        result = send_attendance_report(parent_email, student_name, attendance_data)
        
        if result:
            return jsonify({
                'success': True, 
                'message': 'Email sent successfully'
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Failed to send email. Please check email configuration.'
            }), 500
            
    except Exception as e:
        print(f"❌ Error in send_report_email: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'message': f'Server error: {str(e)}'
        }), 500

@bp.route('/edit-attendance', methods=['POST'])
@staff_required
def edit_attendance():
    """Edit attendance record"""
    # Implement attendance editing
    return jsonify({'success': True})

@bp.route('/notify-student', methods=['POST'])
@staff_required
def notify_student():
    """Send notification to student"""
    # Implement notification
    return jsonify({'success': True})

@bp.route('/test-mail')
def test_mail():
    """Test email configuration"""
    from utils.email_service import send_email
    
    ok = send_email(
        "bloghosting34@gmail.com",  # Replace with your test email
        "Test Mail",
        "Mail working",
        "<b>Mail Working</b>"
    )
    
    return "Sent ✅" if ok else "Failed ❌"