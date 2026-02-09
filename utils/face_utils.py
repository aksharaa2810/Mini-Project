import cv2
import numpy as np

def detect_face_simple(image_np):
    """
    Simple face detection using Haar Cascade
    
    Args:
        image_np (numpy.ndarray): Image array in BGR format
        
    Returns:
        list: List of detected faces (rectangles)
    """
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if face_cascade.empty():
            print("❌ Failed to load face cascade classifier")
            return []
        
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))
        
        print(f"Detected {len(faces)} face(s)")
        return faces
        
    except Exception as e:
        print(f"❌ Face detection error: {e}")
        return []
