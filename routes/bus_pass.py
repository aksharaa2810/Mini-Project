# routes/bus_pass.py - Complete Bus Pass QR System with Mobile Scanning
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, Response
from datetime import datetime, timedelta
import hashlib
import json
import qrcode
from io import BytesIO
import base64

bp = Blueprint('bus_pass', __name__, url_prefix='/bus-pass')

# In-memory storage (use database in production)
bus_passes = {}

def generate_pass_token(student_id, timestamp):
    """Generate unique token for QR code"""
    data = f"{student_id}-{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]

def generate_qr_code(data):
    """Generate QR code image"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        print(f"Error generating QR: {e}")
        return None

@bp.route('/generate')
def generate_pass():
    """Student generates bus pass with QR code"""
    # Get student info from session
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    student_id = session.get('user_id')
    student_name = session.get('name', 'Student')
    
    # Import here to avoid circular imports
    from utils.database import get_user_by_id
    student = get_user_by_id(student_id, 'student')
    
    if not student:
        return "Student not found", 404
    
    # Generate pass data
    timestamp = datetime.now().isoformat()
    valid_until = (datetime.now() + timedelta(hours=24)).isoformat()
    token = generate_pass_token(student_id, timestamp)
    
    pass_data = {
        'type': 'BUS_PASS',
        'token': token,
        'student_id': student_id,
        'student_name': student_name,
        'class': student.get('class', 'N/A'),
        'roll_no': student.get('roll_no', 'N/A'),
        'department': student.get('department', 'N/A'),
        'semester': student.get('semester', 'N/A'),
        'generated_at': timestamp,
        'valid_until': valid_until
    }
    
    # Store pass in memory
    bus_passes[token] = pass_data
    
    # Generate QR code URL that points to verification page
    qr_url = f"{request.host_url}bus-pass/verify/{token}"
    qr_image = generate_qr_code(qr_url)
    
    # Return HTML page with QR code
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bus Pass - {student_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea, #764ba2);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 500px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
        }}
        h1 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2em;
        }}
        .badge {{
            display: inline-block;
            background: #10b981;
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
        .qr-container {{
            background: white;
            padding: 20px;
            border: 3px solid #667eea;
            border-radius: 15px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }}
        .qr-container img {{
            width: 250px;
            height: 250px;
            margin: 0 auto;
            display: block;
        }}
        .scan-instruction {{
            background: #f0f4ff;
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            font-size: 14px;
            color: #4338ca;
            border-left: 4px solid #667eea;
        }}
        .info-card {{
            background: #f9fafb;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: left;
        }}
        .info-row {{
            padding: 12px 0;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .info-row:last-child {{
            border-bottom: none;
        }}
        .info-label {{
            font-weight: 600;
            color: #6b7280;
            font-size: 14px;
        }}
        .info-value {{
            color: #111827;
            font-weight: 600;
            font-size: 16px;
        }}
        .btn {{
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin: 5px;
            text-decoration: none;
            display: inline-block;
            color: white;
            transition: all 0.3s ease;
        }}
        .btn-primary {{ background: linear-gradient(135deg, #667eea, #764ba2); }}
        .btn-success {{ background: linear-gradient(135deg, #10b981, #059669); }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }}
        .valid-badge {{
            background: #d1fae5;
            color: #065f46;
            padding: 10px 20px;
            border-radius: 8px;
            display: inline-block;
            margin: 10px 0;
            font-weight: 600;
            font-size: 14px;
        }}
        .timer {{
            font-size: 24px;
            color: #667eea;
            font-weight: bold;
            margin: 15px 0;
        }}
        @media print {{
            body {{ background: white; }}
            .btn {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚌 Bus Pass</h1>
        <div class="badge">ACTIVE</div>
        
        <div class="scan-instruction">
            📱 Scan this QR code at the bus entrance<br>
            Guard can verify your details instantly
        </div>
        
        <div class="qr-container">
            <img src="{qr_image}" alt="Bus Pass QR Code">
        </div>
        
        <div class="info-card">
            <div class="info-row">
                <span class="info-label">🆔 Student ID</span>
                <span class="info-value">{student_id}</span>
            </div>
            <div class="info-row">
                <span class="info-label">👤 Name</span>
                <span class="info-value">{student_name}</span>
            </div>
            <div class="info-row">
                <span class="info-label">📚 Class</span>
                <span class="info-value">{student.get('class', 'N/A')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">🔢 Roll No</span>
                <span class="info-value">{student.get('roll_no', 'N/A')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">🏢 Department</span>
                <span class="info-value">{student.get('department', 'N/A')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">📅 Semester</span>
                <span class="info-value">{student.get('semester', 'N/A')}</span>
            </div>
        </div>
        
        <div class="valid-badge">
            ✅ Valid for 24 hours
        </div>
        
        <div class="timer" id="timer">23:59:59</div>
        
        <div style="margin-top: 20px;">
            <button class="btn btn-success" onclick="window.print()">
                🖨️ Print Pass
            </button>
            <button class="btn btn-primary" onclick="downloadQR()">
                💾 Download QR
            </button>
        </div>
        
        <div style="margin-top: 20px;">
            <a href="/student/dashboard" class="btn btn-primary">
                ← Back to Dashboard
            </a>
        </div>
    </div>
    
    <script>
        // Countdown timer
        const validUntil = new Date('{valid_until}');
        
        function updateTimer() {{
            const now = new Date();
            const diff = validUntil - now;
            
            if (diff <= 0) {{
                document.getElementById('timer').textContent = 'EXPIRED';
                document.getElementById('timer').style.color = '#ef4444';
                return;
            }}
            
            const hours = Math.floor(diff / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((diff % (1000 * 60)) / 1000);
            
            document.getElementById('timer').textContent = 
                `${{hours.toString().padStart(2, '0')}}:${{minutes.toString().padStart(2, '0')}}:${{seconds.toString().padStart(2, '0')}}`;
        }}
        
        updateTimer();
        setInterval(updateTimer, 1000);
        
        function downloadQR() {{
            const link = document.createElement('a');
            link.download = 'bus_pass_{student_id}.png';
            link.href = '{qr_image}';
            link.click();
        }}
    </script>
</body>
</html>'''
    
    return html


@bp.route('/verify/<token>')
def verify_pass(token):
    """Verify and display bus pass details - THIS IS WHAT MOBILE SCAN SHOWS"""
    
    # Get pass data from storage
    pass_data = bus_passes.get(token)
    
    if not pass_data:
        return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invalid Pass</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #fee2e2;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            max-width: 400px;
            background: white;
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .error-icon {
            font-size: 80px;
            margin-bottom: 20px;
            animation: shake 0.5s;
        }
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
        h1 { 
            color: #dc2626; 
            margin-bottom: 15px;
            font-size: 1.8em;
        }
        p { 
            color: #6b7280; 
            line-height: 1.6;
            margin-bottom: 20px;
        }
        .btn {
            background: #dc2626;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            display: inline-block;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-icon">❌</div>
        <h1>Invalid or Expired Pass</h1>
        <p>This bus pass is not valid. It may have expired or been deleted.</p>
        <p>Please generate a new pass from your student dashboard.</p>
        <a href="/student/dashboard" class="btn">Go to Dashboard</a>
    </div>
</body>
</html>''', 404
    
    # Check if expired
    valid_until = datetime.fromisoformat(pass_data['valid_until'])
    is_expired = datetime.now() > valid_until
    
    # Calculate time since generation
    generated_at = datetime.fromisoformat(pass_data['generated_at'])
    time_ago = datetime.now() - generated_at
    hours = int(time_ago.total_seconds() / 3600)
    minutes = int((time_ago.total_seconds() % 3600) / 60)
    
    # Return mobile-friendly verification page
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bus Pass Verification</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            max-width: 500px;
            width: 100%;
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            animation: slideUp 0.5s ease;
        }}
        @keyframes slideUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .status-badge {{
            display: inline-block;
            padding: 15px 30px;
            border-radius: 30px;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 30px;
            animation: pulse 2s infinite;
        }}
        .status-badge.valid {{
            background: #d1fae5;
            color: #065f46;
        }}
        .status-badge.expired {{
            background: #fee2e2;
            color: #991b1b;
        }}
        h1 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2em;
        }}
        .student-photo {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea, #764ba2);
            margin: 20px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 60px;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }}
        .info-card {{
            background: #f9fafb;
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            text-align: left;
        }}
        .info-row {{
            padding: 15px 0;
            border-bottom: 2px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .info-row:last-child {{
            border-bottom: none;
        }}
        .info-label {{
            font-weight: 600;
            color: #6b7280;
            font-size: 14px;
        }}
        .info-value {{
            color: #111827;
            font-weight: 700;
            font-size: 16px;
        }}
        .verification-time {{
            color: #6b7280;
            font-size: 14px;
            margin-top: 20px;
            padding: 15px;
            background: #f3f4f6;
            border-radius: 10px;
        }}
        .btn {{
            padding: 15px 40px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin: 10px 5px;
            color: white;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
        }}
        .btn-success {{
            background: linear-gradient(135deg, #10b981, #059669);
        }}
        .btn-primary {{
            background: linear-gradient(135deg, #667eea, #764ba2);
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }}
        .checkmark {{
            font-size: 80px;
            margin: 20px 0;
            animation: scaleIn 0.5s ease;
        }}
        @keyframes scaleIn {{
            from {{ transform: scale(0); }}
            to {{ transform: scale(1); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="status-badge {'valid' if not is_expired else 'expired'}">
            {'✅ Pass Granted' if not is_expired else '❌ Pass Denied'}
        </div>
        
        <div class="checkmark">{'✓' if not is_expired else '✗'}</div>
        
        <h1>Bus Pass Verification</h1>
        
        <div class="student-photo">
            👤
        </div>
        
        <div class="info-card">
            <div class="info-row">
                <span class="info-label">🆔 Student ID</span>
                <span class="info-value">{pass_data['student_id']}</span>
            </div>
            <div class="info-row">
                <span class="info-label">👤 Student Name</span>
                <span class="info-value">{pass_data['student_name']}</span>
            </div>
            <div class="info-row">
                <span class="info-label">📚 Class</span>
                <span class="info-value">{pass_data['class']}</span>
            </div>
            <div class="info-row">
                <span class="info-label">🔢 Roll No</span>
                <span class="info-value">{pass_data['roll_no']}</span>
            </div>
            <div class="info-row">
                <span class="info-label">🏢 Department</span>
                <span class="info-value">{pass_data['department']}</span>
            </div>
            <div class="info-row">
                <span class="info-label">📅 Semester</span>
                <span class="info-value">{pass_data['semester']}</span>
            </div>
            <div class="info-row">
                <span class="info-label">📍 Status</span>
                <span class="info-value" style="color: {'#10b981' if not is_expired else '#ef4444'}">
                    {'Pass Granted' if not is_expired else 'Pass Denied'}
                </span>
            </div>
        </div>
        
        <div class="verification-time">
            🕐 Generated: {hours}h {minutes}m ago<br>
            ⏰ Verified: {datetime.now().strftime('%I:%M %p, %d %b %Y')}<br>
            {'⏳ Time Validity: ' + valid_until.strftime('%I:%M %p, %d %b %Y') if not is_expired else '⚠️ Pass has expired'}
        </div>
        
        {'<button class="btn btn-success" onclick="markEntry()">✅ Allow Bus Entry</button>' if not is_expired else '<p style="color: #ef4444; margin-top: 20px; font-weight: bold;">❌ Pass has expired. Student must generate a new pass.</p>'}
        
        <button class="btn btn-primary" onclick="window.location.reload()">
            🔄 Refresh
        </button>
    </div>
    
    <script>
        function markEntry() {{
            if (confirm('Allow student to board the bus?')) {{
                const btn = event.target;
                btn.disabled = true;
                btn.textContent = '⏳ Processing...';
                
                fetch('/bus-pass/mark-entry/{token}', {{
                    method: 'POST'
                }})
                .then(res => res.json())
                .then(data => {{
                    if (data.success) {{
                        btn.textContent = '✅ Entry Marked!';
                        btn.style.background = '#059669';
                        
                        // Show success message
                        alert('✅ Bus entry marked successfully!\\nStudent: ' + data.student_name);
                        
                        // Reload after 2 seconds
                        setTimeout(() => {{
                            window.location.reload();
                        }}, 2000);
                    }} else {{
                        alert('❌ Error: ' + data.message);
                        btn.disabled = false;
                        btn.textContent = '✅ Allow Bus Entry';
                    }}
                }})
                .catch(err => {{
                    alert('❌ Error marking entry');
                    btn.disabled = false;
                    btn.textContent = '✅ Allow Bus Entry';
                    console.error(err);
                }});
            }}
        }}
    </script>
</body>
</html>'''
    
    return html


@bp.route('/mark-entry/<token>', methods=['POST'])
def mark_entry(token):
    """Mark bus entry when pass is verified"""
    try:
        pass_data = bus_passes.get(token)
        
        if not pass_data:
            return jsonify({'success': False, 'message': 'Invalid pass'})
        
        # Check if expired
        valid_until = datetime.fromisoformat(pass_data['valid_until'])
        if datetime.now() > valid_until:
            return jsonify({'success': False, 'message': 'Pass has expired'})
        
        # Save to database
        from utils.database import mark_bus_attendance
        
        mark_bus_attendance(
            student_id=pass_data['student_id'],
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        return jsonify({
            'success': True,
            'message': 'Entry marked',
            'student_id': pass_data['student_id'],
            'student_name': pass_data['student_name'],
            'timestamp': datetime.now().strftime('%I:%M %p')
        })
        
    except Exception as e:
        print(f"Error marking entry: {e}")
        return jsonify({'success': False, 'message': str(e)})


@bp.route('/scanner')
def scanner():
    """QR Code scanner page for guards/staff - Opens camera to scan"""
    html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bus Pass Scanner</title>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #1f2937;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
        }
        h1 { 
            color: #667eea; 
            text-align: center; 
            margin-bottom: 30px;
            font-size: 2em;
        }
        #reader {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .result {
            margin-top: 20px;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
        }
        .result.success { 
            background: #d1fae5; 
            color: #065f46;
            border: 2px solid #10b981;
        }
        .result.error { 
            background: #fee2e2; 
            color: #991b1b;
            border: 2px solid #ef4444;
        }
        .instructions {
            background: #f3f4f6;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
        }
        .instructions h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .instructions ul {
            margin-left: 20px;
            color: #6b7280;
        }
        .instructions li {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📱 Bus Pass Scanner</h1>
        
        <div class="instructions">
            <h3>📋 Instructions:</h3>
            <ul>
                <li>Point camera at student's QR code</li>
                <li>Wait for automatic detection</li>
                <li>Student details will display instantly</li>
                <li>Click "Allow Entry" to mark attendance</li>
            </ul>
        </div>
        
        <div id="reader"></div>
        <div id="result"></div>
    </div>
    
    <script>
        const scanner = new Html5Qrcode("reader");
        
        function onScanSuccess(decodedText, decodedResult) {
            // Stop scanning
            scanner.stop();
            
            // Show loading
            document.getElementById('result').innerHTML = 
                '<div class="result">⏳ Loading student details...</div>';
            
            // Redirect to verification page
            window.location.href = decodedText;
        }
        
        function onScanError(errorMessage) {
            // Ignore errors (continuous scanning)
        }
        
        // Start scanning
        scanner.start(
            { facingMode: "environment" },
            { fps: 10, qrbox: 250 },
            onScanSuccess,
            onScanError
        ).catch(err => {
            document.getElementById('result').innerHTML = 
                '<div class="result error">❌ Camera access denied or not available</div>';
            console.error('Scanner error:', err);
        });
    </script>
</body>
</html>'''
    return Response(html, mimetype='text/html')