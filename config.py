import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    # File upload settings
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    
    # Attendance settings
    ATTENDANCE_TIME_WINDOW = 5  # minutes
    
    # Face recognition settings
    FACE_DETECTION_CONFIDENCE = 0.9
    FACE_RECOGNITION_THRESHOLD = 0.6
    
    # CSV file paths
    STUDENTS_CSV = 'data/students.csv'
    STAFF_CSV = 'data/staff.csv'
    ATTENDANCE_CSV = 'data/attendance.csv'
    OD_REQUESTS_CSV = 'data/od_requests.csv'
    HOSTEL_PASS_CSV = 'data/hostel_pass.csv'
    BUS_ATTENDANCE_CSV = 'data/bus_attendance.csv'
    
    # Model paths
    FACE_EMBEDDINGS_PATH = 'models/saved_models/face_embeddings.pkl'
    SVM_CLASSIFIER_PATH = 'models/saved_models/svm_classifier.pkl'
    
    # Email Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    
    # Gmail Credentials
    MAIL_USERNAME = 'bloghosting34@gmail.com'
    MAIL_PASSWORD = 'fcmipzqwssucvdtv'  # App Password
    MAIL_DEFAULT_SENDER = 'bloghosting34@gmail.com'
    
    # Password Reset
    RESET_TOKEN_EXPIRY = 3600  # 1 hour in seconds