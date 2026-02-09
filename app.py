from flask import Flask, render_template, redirect, session, url_for
from routes import auth, student_routes, staff_routes, admin_routes
from routes import face_attendance, face_registration, bus_pass
from utils.email_service import init_mail
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Mail
mail = init_mail(app)

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(student_routes.bp)
app.register_blueprint(staff_routes.bp)
app.register_blueprint(admin_routes.bp)
app.register_blueprint(face_attendance.bp)
app.register_blueprint(face_registration.bp)
app.register_blueprint(bus_pass.bp)

@app.route('/')
def index():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'student':
            return redirect(url_for('student.dashboard'))
        elif role == 'staff':
            return redirect(url_for('staff.dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin.dashboard'))
    return render_template('index.html')

if __name__ == '__main__':
    # Create required directories
    import os
    os.makedirs('static/uploads/student_faces', exist_ok=True)
    os.makedirs('static/uploads/od_proofs', exist_ok=True)
    os.makedirs('models/saved_models', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    print("\n" + "="*60)
    print("🚀 SMART ATTENDANCE SYSTEM")
    print("="*60)
    print("\n📧 Email Configuration:")
    print(f"   Server: {app.config['MAIL_SERVER']}")
    print(f"   Port: {app.config['MAIL_PORT']}")
    print(f"   Username: {app.config['MAIL_USERNAME']}")
    print(f"   Sender: {app.config['MAIL_DEFAULT_SENDER']}")
    print("\n⚠️  IMPORTANT: Configure MAIL_USERNAME and MAIL_PASSWORD in config.py")
    # Get local IP
    import socket
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"\n📱 To access on mobile/other devices, use: http://{local_ip}:5000")
    except:
        print("\n📱 Could not detect local IP. Try 'ipconfig' (Windows) or 'ifconfig' (Mac/Linux) to find it.")

    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')