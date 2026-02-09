# utils/email_service.py
from flask_mail import Mail, Message
from flask import current_app, render_template_string
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import os

mail = Mail()

def init_mail(app):
    """Initialize Flask-Mail with app"""
    mail.init_app(app)
    return mail


def generate_reset_token(email):
    """Generate password reset token"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')


def verify_reset_token(token, expiration=3600):
    """Verify password reset token"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
        return email
    except (SignatureExpired, BadSignature):
        return None


def send_email(recipient, subject, body, html=None):
    """Send email with timeout handling"""
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            body=body,
            html=html
        )
        
        # Send with timeout
        import socket
        socket.setdefaulttimeout(10)  # 10 second timeout
        
        mail.send(msg)
        print(f"✅ Email sent to {recipient}")
        return True
        
    except socket.timeout:
        print(f"⌛ Email timeout for {recipient}")
        return False
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        import traceback
        traceback.print_exc()
        return False


def send_registration_email(student_email, student_name, student_id, password):
    """Send registration confirmation email to student"""
    subject = "Welcome to FaceWave - Registration Successful"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }}
            .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
            .content {{ padding: 30px 0; }}
            .credentials {{ background: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .credentials p {{ margin: 10px 0; font-size: 16px; }}
            .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #6b7280; font-size: 14px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎓 Welcome to FaceWave</h1>
            </div>
            
            <div class="content">
                <h2>Hello {student_name}! 👋</h2>
                <p>Your registration has been completed successfully. You can now access the FaceWave.</p>
                
                <div class="credentials">
                    <h3>Your Login Credentials:</h3>
                    <p><strong>Student ID:</strong> {student_id}</p>
                    <p><strong>Email:</strong> {student_email}</p>
                    <p><strong>Password:</strong> {password}</p>
                </div>
                
                <div class="warning">
                    <strong>⚠️ Important:</strong> Please change your password after first login for security.
                </div>
                
                <h3>Next Steps:</h3>
                <ol>
                    <li>Login using your credentials</li>
                    <li>Complete face registration (3 photos required)</li>
                    <li>Start marking attendance using face recognition</li>
                </ol>
                
                <p>If you have any questions, please contact your administrator.</p>
            </div>
            
            <div class="footer">
                <p>This is an automated email. Please do not reply.</p>
                <p>&copy; 2025 FaceWave</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    body = f"""
    Welcome to FaceWave!
    
    Hello {student_name},
    
    Your registration has been completed successfully.
    
    Login Credentials:
    Student ID: {student_id}
    Email: {student_email}
    Password: {password}
    
    Please change your password after first login.
    
    Next Steps:
    1. Login using your credentials
    2. Complete face registration (3 photos required)
    3. Start marking attendance using face recognition
    
    If you have any questions, please contact your administrator.
    
    Best regards,
    FaceWave Team
    """
    
    return send_email(student_email, subject, body, html)


def send_parent_notification(parent_email, student_name, student_id):
    """Send notification to parent about student registration"""
    subject = f"Student Registration Notification - {student_name}"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }}
            .header {{ background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
            .content {{ padding: 30px 0; }}
            .info-box {{ background: #f0fdf4; border: 2px solid #10b981; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📧 Student Registration Notification</h1>
            </div>
            
            <div class="content">
                <h2>Dear Parent/Guardian,</h2>
                <p>This is to inform you that your ward has been successfully registered in the FaceWave.</p>
                
                <div class="info-box">
                    <h3>Student Details:</h3>
                    <p><strong>Name:</strong> {student_name}</p>
                    <p><strong>Student ID:</strong> {student_id}</p>
                </div>
                
                <p>You will receive attendance reports via email at the end of each month.</p>
                
                <h3>Features:</h3>
                <ul>
                    <li>✅ AI-powered face recognition attendance</li>
                    <li>📊 Monthly attendance reports</li>
                    <li>📱 Real-time notifications</li>
                    <li>🔒 Secure and reliable</li>
                </ul>
                
                <p>For any queries, please contact the institution.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    body = f"""
    Dear Parent/Guardian,
    
    This is to inform you that your ward has been successfully registered in the FaceWave.
    
    Student Details:
    Name: {student_name}
    Student ID: {student_id}
    
    You will receive attendance reports via email at the end of each month.
    
    For any queries, please contact the institution.
    
    Best regards,
    FaceWave
    """
    
    return send_email(parent_email, subject, body, html)


def send_attendance_report(parent_email, student_name, attendance_data):
    """Send monthly attendance report to parent"""
    
    # Validate email
    if not parent_email or '@' not in parent_email:
        print(f"❌ Invalid email address: {parent_email}")
        return False
    
    subject = f"Monthly Attendance Report - {student_name}"
    
    # Calculate statistics with safe defaults
    total = attendance_data.get('total', 0)
    present = attendance_data.get('present', 0)
    absent = attendance_data.get('absent', 0)
    percentage = attendance_data.get('percentage', 0)
    
    try:
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }}
                .header {{ background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
                .stats {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 20px 0; }}
                .stat-box {{ background: #f9fafb; padding: 20px; border-radius: 8px; text-align: center; }}
                .stat-value {{ font-size: 32px; font-weight: bold; color: #667eea; }}
                .stat-label {{ color: #6b7280; margin-top: 5px; }}
                .percentage {{ font-size: 48px; font-weight: bold; margin: 20px 0; }}
                .good {{ color: #10b981; }}
                .warning {{ color: #f59e0b; }}
                .danger {{ color: #ef4444; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Monthly Attendance Report</h1>
                </div>
                
                <div class="content">
                    <h2>Student: {student_name}</h2>
                    
                    <div class="percentage {'good' if percentage >= 75 else 'warning' if percentage >= 60 else 'danger'}">
                        {percentage}%
                    </div>
                    
                    <div class="stats">
                        <div class="stat-box">
                            <div class="stat-value">{total}</div>
                            <div class="stat-label">Total Classes</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">{present}</div>
                            <div class="stat-label">Present</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">{absent}</div>
                            <div class="stat-label">Absent</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">{percentage}%</div>
                            <div class="stat-label">Percentage</div>
                        </div>
                    </div>
                    
                    <p>{'✅ Attendance is satisfactory.' if percentage >= 75 else '⚠️ Attendance is below 75%. Please ensure regular attendance.' if percentage >= 60 else '❌ Critical: Attendance is below 60%.'}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        body = f"""
        Monthly Attendance Report
        
        Student: {student_name}
        
        Statistics:
        Total Classes: {total}
        Present: {present}
        Absent: {absent}
        Percentage: {percentage}%
        
        Status: {'Satisfactory' if percentage >= 75 else 'Below Average' if percentage >= 60 else 'Critical'}
        """
        
        return send_email(parent_email, subject, body, html)
        
    except Exception as e:
        print(f"❌ Error creating email content: {e}")
        import traceback
        traceback.print_exc()
        return False


def send_password_reset_email(email, reset_url, name):
    """Send password reset email"""
    subject = "Password Reset Request - FaceWave"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }}
            .header {{ background: linear-gradient(135deg, #ef4444, #dc2626); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
            .btn {{ display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 20px 0; }}
            .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔑 Password Reset Request</h1>
            </div>
            
            <div class="content">
                <h2>Hello {name},</h2>
                <p>We received a request to reset your password for FaceWave.</p>
                
                <p>Click the button below to reset your password:</p>
                
                <a href="{reset_url}" class="btn">Reset Password</a>
                
                <div class="warning">
                    <strong>⚠️ Security Notice:</strong><br>
                    • This link will expire in 1 hour<br>
                    • If you didn't request this, please ignore this email<br>
                    • Never share this link with anyone
                </div>
                
                <p>Or copy this link to your browser:</p>
                <p style="word-break: break-all; color: #667eea;">{reset_url}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    body = f"""
    Hello {name},
    
    We received a request to reset your password for FaceWave.
    
    Click the link below to reset your password:
    {reset_url}
    
    This link will expire in 1 hour.
    
    If you didn't request this, please ignore this email.
    
    Best regards,
    FaceWave Team
    """
    
    return send_email(email, subject, body, html)


def send_password_changed_notification(email, name):
    """Send notification after password is successfully changed"""
    subject = "Password Changed Successfully - FaceWave"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }}
            .header {{ background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✅ Password Changed Successfully</h1>
            </div>
            
            <div class="content">
                <h2>Hello {name},</h2>
                <p>Your password has been successfully changed.</p>
                
                <p>If you didn't make this change, please contact your administrator immediately.</p>
                
                <p>You can now login with your new password.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    body = f"""
    Hello {name},
    
    Your password has been successfully changed.
    
    If you didn't make this change, please contact your administrator immediately.
    
    You can now login with your new password.
    
    Best regards,
    FaceWave Team
    """
    
    return send_email(email, subject, body, html)