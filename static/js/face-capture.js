// Face Capture and Recognition JavaScript

let video = null;
let canvas = null;
let context = null;
let stream = null;

// Initialize Camera
async function initCamera() {
    try {
        video = document.getElementById('video');
        canvas = document.getElementById('canvas');
        context = canvas.getContext('2d');
        
        // Request camera access
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: 640, 
                height: 480 
            } 
        });
        
        video.srcObject = stream;
        video.play();
        
        console.log('Camera initialized successfully');
        return true;
    } catch (error) {
        console.error('Error accessing camera:', error);
        alert('Unable to access camera. Please check permissions.');
        return false;
    }
}

// Stop Camera
function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    
    if (video) {
        video.srcObject = null;
    }
}

// Capture Photo
function capturePhoto() {
    if (!video || !canvas || !context) {
        alert('Camera not initialized');
        return null;
    }
    
    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Convert to base64
    const imageData = canvas.toDataURL('image/jpeg', 0.9);
    
    console.log('Photo captured');
    return imageData;
}

// Mark Attendance via Face Recognition
async function markAttendance() {
    const captureBtn = document.getElementById('captureBtn');
    const statusDiv = document.getElementById('status');
    
    try {
        // Disable button
        captureBtn.disabled = true;
        captureBtn.textContent = 'Processing...';
        statusDiv.textContent = 'Capturing face...';
        statusDiv.className = 'alert alert-info';
        
        // Capture photo
        const imageData = capturePhoto();
        
        if (!imageData) {
            throw new Error('Failed to capture image');
        }
        
        // Send to server for recognition
        statusDiv.textContent = 'Recognizing face...';
        
        const response = await fetch('/api/mark-attendance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: imageData,
                timestamp: new Date().toISOString()
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            statusDiv.textContent = result.message;
            statusDiv.className = 'alert alert-success';
            
            // Show success animation
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            throw new Error(result.message || 'Attendance marking failed');
        }
        
    } catch (error) {
        console.error('Error marking attendance:', error);
        statusDiv.textContent = error.message;
        statusDiv.className = 'alert alert-error';
    } finally {
        // Re-enable button
        captureBtn.disabled = false;
        captureBtn.textContent = 'Mark Attendance';
    }
}

// Register Student Face
async function registerFace() {
    const nameInput = document.getElementById('studentName');
    const idInput = document.getElementById('