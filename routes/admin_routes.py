"""
Admin Routes - Complete admin_routes.py
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from datetime import datetime, date
from functools import wraps
from utils.database import get_od_requests

# Create Blueprint
bp = Blueprint('admin', __name__)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Please login as admin to access this page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/dashboard')
@login_required
def dashboard():
    """Admin Dashboard"""
    
    # Get admin info
    name = session.get('name', 'Admin')
    current_date = datetime.now().strftime('%B %d, %Y')
    current_time = datetime.now().strftime('%I:%M %p')
    
    # Main Statistics
    # TODO: Replace with actual database queries
    total_students = 150
    total_staff = 25
    today_attendance = 88
    # Get real pending OD requests count
    try:
        pending_od_requests = len(get_od_requests(status='pending'))
    except Exception:
        pending_od_requests = 0
    total_classes = 12
    total_subjects = 8
    bus_users = 45
    hostel_passes = 12
    
    # Chart Data - Weekly Attendance
    weekly_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    weekly_data = [85, 88, 92, 87, 90, 86]
    
    # Chart Data - Department-wise Attendance
    department_labels = ['CSE', 'ECE', 'MECH', 'CIVIL', 'EEE']
    department_data = [90, 85, 88, 82, 87]
    
    # Recent Users
    recent_users = []
    # TODO: Fetch from database
    # recent_users = db.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT 5")
    
    # Example data
    recent_users = [
        {
            'user_id': 'STU001',
            'name': 'John Doe',
            'role': 'student',
            'email': 'john@example.com',
            'created_at': '2025-01-05'
        }
    ]
    
    # System Status
    last_backup = datetime.now().strftime('%Y-%m-%d %I:%M %p')
    avg_response_time = 45
    
    # Alerts
    alerts = []
    # Example alert
    # alerts = [
    #     {
    #         'type': 'warning',
    #         'title': 'Low Attendance Alert',
    #         'message': '5 students below 75% attendance',
    #         'time': '10 minutes ago'
    #     }
    # ]
    
    return render_template('admin/dashboard.html',
                         name=name,
                         current_date=current_date,
                         current_time=current_time,
                         total_students=total_students,
                         total_staff=total_staff,
                         today_attendance=today_attendance,
                         pending_od_requests=pending_od_requests,
                         total_classes=total_classes,
                         total_subjects=total_subjects,
                         bus_users=bus_users,
                         hostel_passes=hostel_passes,
                         weekly_labels=weekly_labels,
                         weekly_data=weekly_data,
                         department_labels=department_labels,
                         department_data=department_data,
                         recent_users=recent_users,
                         last_backup=last_backup,
                         avg_response_time=avg_response_time,
                         alerts=alerts)


@bp.route('/manage-users')
@login_required
def manage_users():
    """Manage Users Page"""
    
    role = request.args.get('role', 'student')
    
    # Get user counts
    student_count = 150  # TODO: Get from database
    staff_count = 25
    admin_count = 3
    
    # Get users based on role filter
    users = []
    # TODO: Fetch from database
    # users = db.execute("SELECT * FROM users WHERE role = ?", role)
    
    # Example data
    users = [
        {
            'user_id': 'STU001',
            'name': 'John Doe',
            'email': 'john@example.com',
            'class': 'CSE-A',
            'roll_no': '101',
            'created_at': '2025-01-01'
        }
    ]
    
    return render_template('admin/manage_users.html',
                         role=role,
                         student_count=student_count,
                         staff_count=staff_count,
                         admin_count=admin_count,
                         users=users)


@bp.route('/system-logs')
@login_required
def system_logs():
    """System Logs Page"""
    
    # Get log statistics
    log_stats = {
        'info': 150,
        'success': 89,
        'warning': 12,
        'error': 3,
        'debug': 45
    }
    
    # Get logs
    logs = []
    # TODO: Fetch from database
    # logs = db.execute("SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT 100")
    
    # Example logs
    logs = [
        {
            'id': 1,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'level': 'info',
            'message': 'User STU001 logged in successfully'
        },
        {
            'id': 2,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'level': 'success',
            'message': 'Attendance marked for CSE-A Period 1'
        }
    ]
    
    # Critical logs
    critical_logs = []
    # TODO: Fetch critical logs
    
    # Activity stats
    activity_stats = {
        'logins': 45,
        'logouts': 42,
        'failed_logins': 2,
        'attendance_marked': 120,
        'attendance_modified': 5,
        'od_approved': 8,
        'db_queries': 1250,
        'api_calls': 89,
        'errors': 3
    }
    
    # Chart data for activity
    chart_labels = ['12 AM', '4 AM', '8 AM', '12 PM', '4 PM', '8 PM']
    chart_data = {
        'info': [10, 5, 45, 60, 25, 5],
        'warning': [2, 1, 3, 4, 2, 0],
        'error': [0, 0, 1, 1, 1, 0]
    }
    
    return render_template('admin/system_logs.html',
                         log_stats=log_stats,
                         logs=logs,
                         critical_logs=critical_logs,
                         activity_stats=activity_stats,
                         chart_labels=chart_labels,
                         chart_data=chart_data)


@bp.route('/add-user', methods=['POST'])
@login_required
def add_user():
    """Add New User"""
    try:
        user_id = request.form.get('user_id')
        name = request.form.get('name')
        email = request.form.get('email')
        role = request.form.get('role')
        password = request.form.get('password')
        
        # TODO: Add validation and save to database
        # db.execute("INSERT INTO users (...) VALUES (...)")
        
        flash(f'User {user_id} added successfully!', 'success')
        return redirect(url_for('admin.manage_users'))
        
    except Exception as e:
        flash(f'Error adding user: {str(e)}', 'error')
        return redirect(url_for('admin.manage_users'))


@bp.route('/get-user/<user_id>')
@login_required
def get_user(user_id):
    """Get User Details (AJAX)"""
    try:
        # TODO: Fetch from database
        # user = db.execute("SELECT * FROM users WHERE user_id = ?", user_id)
        
        # Example data
        user = {
            'user_id': user_id,
            'name': 'John Doe',
            'email': 'john@example.com',
            'role': 'student'
        }
        
        return jsonify(user)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/edit-user/<user_id>', methods=['POST'])
@login_required
def edit_user(user_id):
    """Edit User"""
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        
        # TODO: Update in database
        # db.execute("UPDATE users SET name = ?, email = ? WHERE user_id = ?", 
        #           name, email, user_id)
        
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.manage_users'))
        
    except Exception as e:
        flash(f'Error updating user: {str(e)}', 'error')
        return redirect(url_for('admin.manage_users'))


@bp.route('/delete-user/<user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete User"""
    try:
        # TODO: Delete from database
        # db.execute("DELETE FROM users WHERE user_id = ?", user_id)
        
        return jsonify({'success': True, 'message': 'User deleted'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/backup-database', methods=['POST'])
@login_required
def backup_database():
    """Create Database Backup"""
    try:
        # TODO: Implement database backup logic
        # import shutil
        # shutil.copy('database.db', f'backups/backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        
        return jsonify({'success': True, 'message': 'Backup created successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/get-logs')
@login_required
def get_logs():
    """Get System Logs (AJAX)"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        # TODO: Fetch logs from database based on time range
        logs = [
            {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'level': 'info',
                'message': 'Sample log message'
            }
        ]
        
        return jsonify({'success': True, 'logs': logs})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/export-logs')
@login_required
def export_logs():
    """Export System Logs"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        # TODO: Generate and return log file
        # You can use CSV or text file format
        
        flash('Logs exported successfully!', 'success')
        return redirect(url_for('admin.system_logs'))
        
    except Exception as e:
        flash(f'Error exporting logs: {str(e)}', 'error')
        return redirect(url_for('admin.system_logs'))


@bp.route('/clear-logs', methods=['POST'])
@login_required
def clear_logs():
    """Clear Old Logs"""
    try:
        # TODO: Delete old logs from database
        # db.execute("DELETE FROM system_logs WHERE timestamp < datetime('now', '-30 days')")
        
        deleted = 150  # Number of logs deleted
        
        return jsonify({'success': True, 'deleted': deleted})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/log-details/<log_id>')
@login_required
def log_details(log_id):
    """Get Log Details (AJAX)"""
    try:
        # TODO: Fetch log details from database
        log = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'level': 'info',
            'event_type': 'User Login',
            'user': 'STU001',
            'ip_address': '192.168.1.1',
            'description': 'User logged in successfully',
            'stack_trace': None
        }
        
        return jsonify(log)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500