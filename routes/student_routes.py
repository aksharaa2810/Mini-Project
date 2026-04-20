from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from utils.database import get_attendance, submit_od_request, generate_bus_pass, get_hostel_pass, generate_hostel_qr, get_user_by_id, get_od_requests
from utils.validators import validate_od_form
from datetime import datetime
from datetime import datetime
import os
import socket

def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        print(f"DEBUG: Detected LAN IP: {ip}")
        return ip
    except:
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except:
            return '127.0.0.1'

bp = Blueprint('student', __name__, url_prefix='/student')

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'student':
            flash('Please login first!', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    name = session.get('name')
    
    # Get attendance summary
    attendance_data = get_attendance(user_id)
    
    # Process notifications from OD requests and Hostel passes
    notifications = []
    
    # Check OD requests
    try:
        all_ods = get_od_requests()
        for od in all_ods:
            if od.get('student_id') == user_id:
                status = od.get('status')
                if status == 'approved':
                    notifications.append({
                        'type': 'success',
                        'title': 'OD Request Approved',
                        'message': f"Your OD request for {od.get('date', '')} ({od.get('start_time', '')} - {od.get('end_time', '')}) has been approved.",
                        'time': od.get('approved_at', '')
                    })
                elif status == 'rejected':
                    notifications.append({
                        'type': 'error',
                        'title': 'OD Request Rejected',
                        'message': f"Your OD request for {od.get('date', '')} has been rejected. Remarks: {od.get('remarks', 'None')}",
                        'time': od.get('approved_at', '')
                    })
                elif status == 'pending':
                    notifications.append({
                        'type': 'warning',
                        'title': 'OD Request Pending',
                        'message': f"Your OD request for {od.get('date', '')} is awaiting approval.",
                        'time': od.get('submitted_at', '')
                    })
    except Exception as e:
        print(f"Error loading OD notifications: {e}")

    # Check Hostel passes
    try:
        all_passes = get_hostel_pass()
        for hp in all_passes:
            if hp.get('student_id') == user_id:
                status = hp.get('status')
                if status == 'approved':
                    notifications.append({
                        'type': 'success',
                        'title': 'Hostel Pass Approved',
                        'message': f"Your hostel pass for {hp.get('out_date', '')} to {hp.get('in_date', '')} has been approved.",
                        'time': hp.get('approved_at', '')
                    })
                elif status == 'rejected':
                    notifications.append({
                        'type': 'error',
                        'title': 'Hostel Pass Rejected',
                        'message': f"Your hostel pass for {hp.get('out_date', '')} has been rejected. Remarks: {hp.get('remarks', 'None')}",
                        'time': hp.get('approved_at', '')
                    })
                elif status == 'pending':
                    notifications.append({
                        'type': 'warning',
                        'title': 'Hostel Pass Pending',
                        'message': f"Your hostel pass for {hp.get('out_date', '')} is awaiting approval.",
                        'time': hp.get('submitted_at', '')
                    })
    except Exception as e:
        print(f"Error loading Hostel pass notifications: {e}")

    # Sort notifications by time, descending (newest first)
    notifications.sort(key=lambda x: x.get('time', ''), reverse=True)

    # Generate today's schedule pseudo-randomly for display
    import random
    random.seed(user_id)
    
    current_hour = datetime.now().hour
    subjects_pool = ['Theory of Computation', 'Data Structures', 'Operating Systems', 'Database Management', 'Computer Networks']
    
    schedule = []
    periods = [
        {'period': '1', 'start': '09:00', 'end': '10:00', 'hour': 9},
        {'period': '2', 'start': '10:00', 'end': '11:00', 'hour': 10},
        {'period': '3', 'start': '11:15', 'end': '12:15', 'hour': 11},
        {'period': 'LUNCH', 'start': '12:15', 'end': '13:00', 'hour': 12, 'break': True},
        {'period': '4', 'start': '13:00', 'end': '14:00', 'hour': 13},
        {'period': '5', 'start': '14:00', 'end': '15:00', 'hour': 14},
        {'period': '6', 'start': '15:15', 'end': '16:15', 'hour': 15}
    ]
    
    for p in periods:
        if p.get('break'):
            schedule.append({
                'period': p['period'],
                'start': p['start'],
                'end': p['end'],
                'subject': 'Lunch Break',
                'attended': False,
                'is_current': current_hour == p['hour']
            })
            continue
            
        p_hour = p['hour']
        is_current = current_hour == p_hour
        attended = current_hour > p_hour
        
        schedule.append({
            'period': p['period'],
            'start': p['start'],
            'end': p['end'],
            'subject': random.choice(subjects_pool),
            'attended': attended,
            'is_current': is_current
        })

    return render_template('student/dashboard.html', 
                         name=name, 
                         attendance=attendance_data,
                         notifications=notifications,
                         schedule=schedule)

@bp.route('/attendance')
@login_required
def attendance():
    user_id = session.get('user_id')
    attendance_records = get_attendance(user_id, detailed=True)
    
    return render_template('student/attendance.html', 
                         records=attendance_records)

@bp.route('/apply-od', methods=['GET', 'POST'])
@login_required
def apply_od():
    if request.method == 'POST':
        user_id = session.get('user_id')
        
        od_data = {
            'student_id': user_id,
            'date': request.form.get('date'),
            'start_time': request.form.get('start_time'),
            'end_time': request.form.get('end_time'),
            'reason': request.form.get('reason'),
            'od_type': request.form.get('od_type'),
            'venue': request.form.get('venue'),
            'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'pending'
        }
        
        # Validate form
        if validate_od_form(od_data):
            # Handle file upload
            if 'proof' in request.files:
                file = request.files['proof']
                if file.filename:
                    filename = f"{user_id}_{datetime.now().timestamp()}.pdf"
                    filepath = os.path.join('static/uploads/od_proofs', filename)
                    file.save(filepath)
                    od_data['proof_file'] = filename
            
            # Submit OD request
            if submit_od_request(od_data):
                flash('OD request submitted successfully!', 'success')
                return redirect(url_for('student.dashboard'))
            else:
                flash('Failed to submit OD request!', 'error')
        else:
            flash('Invalid form data!', 'error')
    
    return render_template('student/apply_od.html')

@bp.route('/hostel-pass', methods=['GET', 'POST'])
@login_required
def hostel_pass():
    if request.method == 'POST':
        user_id = session.get('user_id')
        
        pass_data = {
            'student_id': user_id,
            'out_date': request.form.get('out_date'),
            'out_time': request.form.get('out_time'),
            'in_date': request.form.get('in_date'),
            'in_time': request.form.get('in_time'),
            'reason': request.form.get('reason'),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'pending'
        }
        
        # Submit hostel pass request
        from utils.database import submit_hostel_pass
        if submit_hostel_pass(pass_data):
            flash('Hostel pass request submitted!', 'success')
        else:
            flash('Failed to submit hostel pass!', 'error')
    
    # Get existing passes
    passes = get_hostel_pass(session.get('user_id'))
    
    # Identify active pass (Approved and not expired)
    active_pass = None
    current_time = datetime.now()
    
    for p in passes:
        if p['status'] == 'approved':
            # Check if within valid timeframe
            try:
                in_dt = datetime.strptime(f"{p['in_date']} {p['in_time']}", '%Y-%m-%d %H:%M')
                if in_dt > current_time:
                    # Generate URL for verification using LAN IP
                    lan_ip = get_lan_ip()
                    verify_url = f"http://{lan_ip}:5000{url_for('student.verify_hostel_pass', pass_id=p['pass_id'])}"
                    p['qr_code'] = generate_hostel_qr(verify_url)
                    active_pass = p
                    break 
            except:
                pass

    return render_template('student/hostel_pass.html', passes=passes, active_pass=active_pass)

@bp.route('/get-hostel-qr/<pass_id>')
@login_required
def get_hostel_qr_route(pass_id):
    passes = get_hostel_pass(session.get('user_id'))
    target_pass = next((p for p in passes if p['pass_id'] == pass_id), None)
    
    if target_pass and target_pass['status'] == 'approved':
        # Generate URL for evaluation using LAN IP
        lan_ip = get_lan_ip()
        verify_url = f"http://{lan_ip}:5000{url_for('student.verify_hostel_pass', pass_id=pass_id)}"
        qr_code = generate_hostel_qr(verify_url)
        return jsonify({'success': True, 'qr_code': qr_code})
    
    return jsonify({'success': False, 'message': 'Pass not found or not approved'})


@bp.route('/verify-hostel-pass/<pass_id>')
def verify_hostel_pass(pass_id):
    """Public verification route for hostel passes"""
    # Note: In production, you might want to require staff login or use a signed token
    # For now, we'll fetch the pass directly
    
    all_passes = get_hostel_pass() # This fetches all (we need to filter in memory as get_hostel_pass by default might need ID)
    # Wait, get_hostel_pass in database.py was updated to accept status/student_id. 
    # But we don't have a 'get_pass_by_id' optimized function. passing nothing might return all or restricted.
    # Let's assume we can fetch all or search efficiently.
    # Actually, get_hostel_pass with no args returns everything? Let's check.
    # Yes, lines 517+ of database.py: if student_id=None return all.
    
    # Better approach: Fetch all and find. (Not efficient for big Db but fine for mini project)
    # Or add get_hostel_pass_by_id in database.py? 
    # Let's filter here for now.
    
    target_pass = None
    student_name = "Unknown"
    is_expired = False
    
    try:
        # We need to find the pass. 
        # Since we don't have a direct lookup, let's look at the implementation plan again.
        # I'll fetch 'approved' passes first to narrow down.
        # Actually, let's just make get_hostel_pass support pass_id filtering or just fetch all.
        
        # Ideally we should assume safe access.
        from utils.database import HOSTEL_PASS_CSV 
        import pandas as pd
        
        if os.path.exists(HOSTEL_PASS_CSV):
            df = pd.read_csv(HOSTEL_PASS_CSV)
            match = df[df['pass_id'] == pass_id]
            if not match.empty:
                target_pass = match.iloc[0].to_dict()
                
                # Get student name
                student = get_user_by_id(target_pass['student_id'], 'student')
                if student:
                    student_name = student.get('name', 'Unknown')
                
                # Check expiration
                try:
                    in_dt = datetime.strptime(f"{target_pass['in_date']} {target_pass['in_time']}", '%Y-%m-%d %H:%M')
                    if datetime.now() > in_dt:
                        is_expired = True
                except:
                    is_expired = True
                    
    except Exception as e:
        print(f"Error validating pass: {e}")

    return render_template('student/verify_hostel_pass.html', 
                         pass_data=target_pass,
                         student_name=student_name,
                         is_expired=is_expired,
                         now=datetime.now().strftime('%Y-%m-%d %I:%M %p'))

@bp.route('/bus-pass')
@login_required
def bus_pass():
    user_id = session.get('user_id')
    
    # Generate URL for verification using LAN IP
    lan_ip = get_lan_ip()
    verify_url = f"http://{lan_ip}:5000{url_for('student.verify_bus_pass', student_id=user_id)}"
    
    # Generate QR code for bus pass
    qr_code = generate_bus_pass(verify_url)
    
    return render_template('student/bus_pass.html', qr_code=qr_code)

@bp.route('/verify-bus-pass/<student_id>')
def verify_bus_pass(student_id):
    """Public verification route for bus passes"""
    from utils.database import get_user_by_id
    
    student = get_user_by_id(student_id, 'student')
    
    return render_template('student/verify_bus_pass.html', 
                         student=student,
                         date=datetime.now().strftime('%Y-%m-%d'),
                         now=datetime.now().strftime('%Y-%m-%d %I:%M %p'))