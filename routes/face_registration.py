# routes/face_registration.py - USES CENTRALIZED DATABASE
from flask import Blueprint, request, jsonify, Response
import os
import base64
from datetime import datetime
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import hashlib
import traceback

# Import ONLY from centralized database - NO LOCAL FUNCTIONS
from utils.database import get_user_by_id, add_student, ensure_data_directory

bp = Blueprint('face_registration', __name__, url_prefix='/face-registration')

MAX_IMAGE_SIZE = 10 * 1024 * 1024
REQUIRED_IMAGES = 3

from utils.face_utils import detect_face_simple


@bp.route('/register')
def register():
    """Face registration page with camera interface"""
    return Response('''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Face Registration System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            padding: 14px 32px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin: 5px;
            color: white;
            transition: all 0.3s ease;
        }
        
        .btn-primary { background: linear-gradient(135deg, #667eea, #764ba2); }
        .btn-success { background: linear-gradient(135deg, #10b981, #059669); }
        .btn-danger { background: linear-gradient(135deg, #ef4444, #dc2626); }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .camera-section {
            background: #000;
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
        }
        
        video {
            width: 100%;
            max-width: 640px;
            display: block;
            margin: 0 auto;
            border-radius: 10px;
        }
        
        canvas { display: none; }
        
        .controls {
            text-align: center;
            margin-top: 20px;
        }
        
        .alert {
            padding: 16px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
            font-weight: 600;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .alert-success { background: #d1fae5; color: #065f46; border-left: 5px solid #10b981; }
        .alert-error { background: #fee2e2; color: #991b1b; border-left: 5px solid #ef4444; }
        .alert-info { background: #dbeafe; color: #1e40af; border-left: 5px solid #3b82f6; }
        
        .progress {
            margin: 20px 0;
            text-align: center;
        }
        
        .progress h3 {
            color: #333;
            margin-bottom: 15px;
        }
        
        .progress-bar {
            height: 35px;
            background: #e5e7eb;
            border-radius: 17px;
            overflow: hidden;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #10b981, #059669);
            width: 0%;
            transition: width 0.3s ease;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 14px;
        }
        
        .slots {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin: 20px 0;
        }
        
        .slot {
            width: 130px;
            height: 130px;
            border: 3px dashed #cbd5e1;
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5em;
            font-weight: bold;
            color: #cbd5e1;
            transition: all 0.3s ease;
        }
        
        .slot.done {
            border-color: #10b981;
            background: #d1fae5;
            color: #10b981;
            border-style: solid;
        }
        
        .hidden { display: none !important; }
        
        .required { color: #ef4444; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📸 Face Registration</h1>
        
        <div id="alertBox"></div>
        
        <!-- REGISTRATION FORM -->
        <div id="formSection">
            <div class="form-group">
                <label>Student ID <span class="required">*</span></label>
                <input type="text" id="studentId" placeholder="e.g., CS2023001" required>
            </div>
            
            <div class="form-group">
                <label>Full Name <span class="required">*</span></label>
                <input type="text" id="studentName" placeholder="Enter your full name" required>
            </div>
            
            <div class="form-group">
                <label>Email <span class="required">*</span></label>
                <input type="email" id="studentEmail" placeholder="student@example.com" required>
            </div>
            
            <div class="form-group">
                <label>Parent Email</label>
                <input type="email" id="parentEmail" placeholder="parent@example.com (optional)">
            </div>
            
            <div class="form-group">
                <label>Department <span class="required">*</span></label>
                <select id="studentDepartment">
                    <option>Computer Science</option>
                    <option>Electrical Engineering</option>
                    <option>Mechanical Engineering</option>
                    <option>Civil Engineering</option>
                    <option>Electronics Engineering</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Class</label>
                <input type="text" id="studentClass" placeholder="e.g., 3rd Year CSE-A">
            </div>
            
            <div class="form-group">
                <label>Semester</label>
                <select id="studentSemester">
                    <option>1</option>
                    <option>2</option>
                    <option selected>3</option>
                    <option>4</option>
                    <option>5</option>
                    <option>6</option>
                    <option>7</option>
                    <option>8</option>
                </select>
            </div>
            
            <div class="controls">
                <button class="btn btn-primary" onclick="startRegistration()">
                    🚀 Start Face Registration
                </button>
            </div>
        </div>
        
        <!-- PROGRESS SECTION -->
        <div id="progressSection" class="hidden">
            <div class="progress">
                <h3>Registration Progress</h3>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill">0/3 Images</div>
                </div>
                <div class="slots">
                    <div class="slot" id="slot1">1</div>
                    <div class="slot" id="slot2">2</div>
                    <div class="slot" id="slot3">3</div>
                </div>
            </div>
        </div>
        
        <!-- CAMERA SECTION -->
        <div id="cameraSection" class="camera-section hidden">
            <video id="video" autoplay playsinline></video>
            <canvas id="canvas"></canvas>
            <div class="controls">
                <button class="btn btn-success" id="captureBtn" onclick="captureFace()">
                    📷 Capture Photo (0/3)
                </button>
                <button class="btn btn-danger" onclick="stopCamera()">
                    ⏹️ Stop Camera
                </button>
            </div>
        </div>
        
        <!-- COMPLETE SECTION -->
        <div id="completeSection" class="controls hidden">
            <button class="btn btn-success" onclick="completeRegistration()">
                ✅ Complete Registration
            </button>
        </div>
    </div>
    
    <script>
        let video, canvas, stream;
        let capturedCount = 0;
        let studentData = {};
        
        window.onload = () => {
            video = document.getElementById('video');
            canvas = document.getElementById('canvas');
        };
        
        function showAlert(msg, type) {
            const alertBox = document.getElementById('alertBox');
            alertBox.innerHTML = `<div class="alert alert-${type}">${msg}</div>`;
            setTimeout(() => {
                alertBox.innerHTML = '';
            }, 5000);
        }
        
        async function startRegistration() {
            // Validate required fields
            const id = document.getElementById('studentId').value.trim();
            const name = document.getElementById('studentName').value.trim();
            const email = document.getElementById('studentEmail').value.trim();
            
            if (!id || !name || !email) {
                showAlert('❌ Please fill in all required fields (Student ID, Name, Email)', 'error');
                return;
            }
            
            // Email validation
            const emailRegex = /^[a-zA-Z0-9._%+-]+@srec\.ac\.in$/;
            if (!emailRegex.test(email)) {
                showAlert('❌ Email must belong to @srec.ac.in domain', 'error');
                return;
            }
            
            // Store student data
            studentData = {
                student_id: id,
                student_name: name,
                student_email: email,
                parent_email: document.getElementById('parentEmail').value.trim(),
                student_department: document.getElementById('studentDepartment').value,
                student_class: document.getElementById('studentClass').value.trim() || 'Not Assigned',
                student_semester: document.getElementById('studentSemester').value
            };
            
            // Hide form, show progress
            const formSection = document.getElementById('formSection');
            const progressSection = document.getElementById('progressSection');
            const cameraSection = document.getElementById('cameraSection');
            
            if (formSection) formSection.classList.add('hidden');
            if (progressSection) progressSection.classList.remove('hidden');
            
            // Start camera
            try {
                stream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: 'user', width: 1280, height: 720 }
                });
                video.srcObject = stream;
                if (cameraSection) cameraSection.classList.remove('hidden');
                showAlert('✅ Camera started! Position your face in the frame.', 'success');
            } catch (error) {
                showAlert('❌ Camera access denied: ' + error.message, 'error');
                console.error('Camera error:', error);
            }
        }
        
        function stopCamera() {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
                video.srcObject = null;
                stream = null;
            }
            const cameraSection = document.getElementById('cameraSection');
            if (cameraSection) {
                cameraSection.classList.add('hidden');
            }
            showAlert('Camera stopped', 'info');
        }
        
        async function captureFace() {
            if (capturedCount >= 3) {
                showAlert('✅ All 3 photos captured!', 'success');
                return;
            }
            
            const btn = document.getElementById('captureBtn');
            btn.disabled = true;
            btn.textContent = '⏳ Processing...';
            
            try {
                // Capture image from video
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0);
                
                // Convert to base64
                const imageData = canvas.toDataURL('image/jpeg', 0.9);
                
                // Send to server
                const response = await fetch('/face-registration/capture-face', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        ...studentData,
                        image: imageData
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    capturedCount = result.images_captured;
                    updateProgress();
                    showAlert(`✅ ${result.message}`, 'success');
                    
                    if (capturedCount >= 3) {
                        stopCamera();
                        const completeSection = document.getElementById('completeSection');
                        if (completeSection) {
                            completeSection.classList.remove('hidden');
                        }
                        showAlert('🎉 All photos captured! Click "Complete Registration" to finish.', 'success');
                    }
                } else {
                    showAlert('❌ ' + result.message, 'error');
                }
                
            } catch (error) {
                showAlert('❌ Error: ' + error.message, 'error');
                console.error('Capture error:', error);
            } finally {
                btn.disabled = false;
                btn.textContent = `📷 Capture Photo (${capturedCount}/3)`;
            }
        }
        
        function updateProgress() {
            const percentage = (capturedCount / 3) * 100;
            const progressFill = document.getElementById('progressFill');
            progressFill.style.width = percentage + '%';
            progressFill.textContent = `${capturedCount}/3 Images`;
            
            // Update slots
            for (let i = 1; i <= capturedCount; i++) {
                const slot = document.getElementById(`slot${i}`);
                slot.classList.add('done');
                slot.textContent = '✓';
            }
        }
        
        async function completeRegistration() {
            try {
                const response = await fetch('/face-registration/complete-registration', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(studentData)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showAlert('🎉 ' + result.message, 'success');
                    setTimeout(() => {
                        window.location.href = '/face-attendance/mark';
                    }, 2000);
                } else {
                    showAlert('❌ ' + result.message, 'error');
                }
                
            } catch (error) {
                showAlert('❌ Error: ' + error.message, 'error');
                console.error('Registration error:', error);
            }
        }
    </script>
</body>
</html>''', mimetype='text/html')


@bp.route('/capture-face', methods=['POST'])
def capture_face():
    """Capture and save face image"""
    try:
        ensure_data_directory()
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data received'})
        
        # Extract student data
        student_id = data.get('student_id', '').strip()
        student_name = data.get('student_name', '').strip()
        student_email = data.get('student_email', '').strip()
        parent_email = data.get('parent_email', '').strip()
        student_class = data.get('student_class', 'Not Assigned').strip()
        department = data.get('student_department', 'Computer Science').strip()
        semester = data.get('student_semester', '3').strip()
        image_data = data.get('image')
        
        # Validate required fields
        if not student_id or not student_name or not student_email or not image_data:
            return jsonify({
                'success': False,
                'message': 'Missing required fields (ID, Name, Email, or Image)'
            })

        if not student_email.endswith('@srec.ac.in'):
            return jsonify({
                'success': False,
                'message': 'Email must belong to @srec.ac.in domain'
            })
        
        # Decode image
        try:
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            image_np = np.array(image)
            
            # Convert to BGR for OpenCV
            if len(image_np.shape) == 3:
                image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Invalid image data: {str(e)}'
            })
        
        # Detect face
        faces = detect_face_simple(image_np)
        
        if len(faces) == 0:
            return jsonify({
                'success': False,
                'message': '❌ No face detected. Please ensure your face is clearly visible.'
            })
        
        if len(faces) > 1:
            return jsonify({
                'success': False,
                'message': '❌ Multiple faces detected. Please ensure only one person is in frame.'
            })
        
        # Save image
        student_dir = os.path.join('static', 'uploads', 'student_faces', student_id)
        os.makedirs(student_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{student_id}_{timestamp}.jpg"
        filepath = os.path.join(student_dir, filename)
        
        cv2.imwrite(filepath, image_np)
        print(f"✅ Image saved: {filepath}")
        
        # Count existing images
        existing_images = [f for f in os.listdir(student_dir) 
                          if f.endswith(('.jpg', '.jpeg', '.png'))]
        images_count = len(existing_images)
        
        print(f"📊 Total images for {student_id}: {images_count}")
        
        # Create student account on first image
        if images_count == 1:
            print(f"\n{'='*60}")
            print(f"CREATING STUDENT ACCOUNT")
            print(f"{'='*60}")
            print(f"Student ID: {student_id}")
            print(f"Name: {student_name}")
            print(f"Email: {student_email}")
            print(f"Department: {department}")
            
            # Check if student already exists
            existing_student = get_user_by_id(student_id, 'student')
            
            if not existing_student:
                # Create new student account
                hashed_password = hashlib.sha256('password'.encode()).hexdigest()
                
                student_account_data = {
                    'user_id': student_id,
                    'name': student_name,
                    'email': student_email,
                    'parent_email': parent_email,
                    'password': hashed_password,
                    'class': student_class,
                    'roll_no': student_id[-3:] if len(student_id) >= 3 else '001',
                    'department': department,
                    'semester': semester
                }
                
                success, message = add_student(student_account_data)
                
                if not success:
                    print(f"❌ Failed to create account: {message}")
                    print(f"{'='*60}\n")
                    # Delete the saved image since account creation failed
                    os.remove(filepath)
                    return jsonify({
                        'success': False,
                        'message': f'Failed to create account: {message}'
                    })
                
                print(f"✅ Student account created successfully!")
                print(f"Default password: password")
            else:
                print(f"ℹ️ Student account already exists")
            
            print(f"{'='*60}\n")
        
        return jsonify({
            'success': True,
            'message': f'Photo {images_count} of 3 captured successfully!',
            'images_captured': images_count,
            'need_more': images_count < REQUIRED_IMAGES
        })
        
    except Exception as e:
        print(f"❌ ERROR in capture_face: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        })


@bp.route('/complete-registration', methods=['POST'])
def complete_registration():
    """Complete the registration process"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data received'})
        
        student_id = data.get('student_id')
        if not student_id:
            return jsonify({'success': False, 'message': 'Student ID is required'})
        
        # Verify student exists in database
        student = get_user_by_id(student_id, 'student')
        if not student:
            return jsonify({
                'success': False,
                'message': '❌ Student account not found in database. Please try registration again.'
            })
        
        # Check if required images exist
        student_dir = os.path.join('static', 'uploads', 'student_faces', student_id)
        if not os.path.exists(student_dir):
            return jsonify({
                'success': False,
                'message': '❌ No face images found. Please capture images first.'
            })
        
        images = [f for f in os.listdir(student_dir) 
                 if f.endswith(('.jpg', '.jpeg', '.png'))]
        
        if len(images) < REQUIRED_IMAGES:
            return jsonify({
                'success': False,
                'message': f'❌ Need {REQUIRED_IMAGES} photos. Only {len(images)} captured.'
            })
        
        print(f"\n{'='*60}")
        print(f"REGISTRATION COMPLETED")
        print(f"{'='*60}")
        print(f"Student ID: {student_id}")
        print(f"Name: {student.get('name', 'Unknown')}")
        print(f"Images: {len(images)}")
        print(f"✅ Ready for attendance marking!")
        print(f"{'='*60}\n")
        
        return jsonify({
            'success': True,
            'message': '🎉 Registration completed successfully! Redirecting to attendance...',
            'student_id': student_id,
            'student_name': student.get('name', 'Unknown'),
            'images_count': len(images)
        })
        
    except Exception as e:
        print(f"❌ ERROR in complete_registration: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        })


@bp.route('/check-student/<student_id>')
def check_student(student_id):
    """Check if student exists and registration status"""
    try:
        # Check if student exists in database
        student = get_user_by_id(student_id, 'student')
        
        # Check face images
        student_dir = os.path.join('static', 'uploads', 'student_faces', student_id)
        images_count = 0
        
        if os.path.exists(student_dir):
            images = [f for f in os.listdir(student_dir) 
                     if f.endswith(('.jpg', '.jpeg', '.png'))]
            images_count = len(images)
        
        return jsonify({
            'success': True,
            'exists': student is not None,
            'student_name': student.get('name', '') if student else '',
            'images_count': images_count,
            'registration_complete': images_count >= REQUIRED_IMAGES and student is not None
        })
        
    except Exception as e:
        print(f"❌ ERROR in check_student: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        })