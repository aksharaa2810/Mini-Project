"""
Face Detection using MTCNN (Multi-task Cascaded Convolutional Networks)
Detects faces in images with high accuracy
"""

import cv2
import numpy as np
from mtcnn import MTCNN
from PIL import Image
import base64
from io import BytesIO

class FaceDetector:
    def __init__(self, min_confidence=0.9):
        """
        Initialize MTCNN face detector
        
        Args:
            min_confidence (float): Minimum confidence threshold for detection
        """
        self.detector = MTCNN(min_face_size=20)
        self.min_confidence = min_confidence
    
    def detect_faces(self, image_path):
        """
        Detect faces in an image file
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            list: List of detected face bounding boxes and landmarks
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                print(f"Error: Unable to load image from {image_path}")
                return []
            
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            faces = self.detector.detect_faces(image_rgb)
            
            # Filter by confidence
            filtered_faces = [
                face for face in faces 
                if face['confidence'] >= self.min_confidence
            ]
            
            return filtered_faces
            
        except Exception as e:
            print(f"Error in face detection: {str(e)}")
            return []
    
    def detect_faces_from_base64(self, base64_string):
        """
        Detect faces from base64 encoded image
        
        Args:
            base64_string (str): Base64 encoded image string
            
        Returns:
            list: List of detected faces
        """
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_string)
            image = Image.open(BytesIO(image_data))
            
            # Convert to numpy array
            image_np = np.array(image)
            
            # Convert to RGB if needed
            if len(image_np.shape) == 2:  # Grayscale
                image_np = cv2.cvtColor(image_np, cv2.COLOR_GRAY2RGB)
            elif image_np.shape[2] == 4:  # RGBA
                image_np = cv2.cvtColor(image_np, cv2.COLOR_RGBA2RGB)
            
            # Detect faces
            faces = self.detector.detect_faces(image_np)
            
            # Filter by confidence
            filtered_faces = [
                face for face in faces 
                if face['confidence'] >= self.min_confidence
            ]
            
            return filtered_faces
            
        except Exception as e:
            print(f"Error detecting faces from base64: {str(e)}")
            return []
    
    def extract_face(self, image_path, face_box, target_size=(224, 224)):
        """
        Extract and resize a face from image
        
        Args:
            image_path (str): Path to image
            face_box (dict): Face bounding box from detection
            target_size (tuple): Target size for face image
            
        Returns:
            numpy.ndarray: Extracted and resized face image
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # Get bounding box coordinates
            x, y, w, h = face_box['box']
            
            # Add margin
            margin = 20
            x = max(0, x - margin)
            y = max(0, y - margin)
            w = w + 2 * margin
            h = h + 2 * margin
            
            # Extract face
            face = image[y:y+h, x:x+w]
            
            # Resize to target size
            face_resized = cv2.resize(face, target_size)
            
            return face_resized
            
        except Exception as e:
            print(f"Error extracting face: {str(e)}")
            return None
    
    def extract_face_from_base64(self, base64_string, face_box, target_size=(224, 224)):
        """
        Extract face from base64 encoded image
        
        Args:
            base64_string (str): Base64 encoded image
            face_box (dict): Face bounding box
            target_size (tuple): Target size for face
            
        Returns:
            numpy.ndarray: Extracted face image
        """
        try:
            # Remove data URL prefix
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_string)
            image = Image.open(BytesIO(image_data))
            image_np = np.array(image)
            
            # Convert to BGR for OpenCV
            if len(image_np.shape) == 3:
                image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            
            # Get bounding box
            x, y, w, h = face_box['box']
            
            # Add margin
            margin = 20
            x = max(0, x - margin)
            y = max(0, y - margin)
            w = min(image_np.shape[1] - x, w + 2 * margin)
            h = min(image_np.shape[0] - y, h + 2 * margin)
            
            # Extract and resize face
            face = image_np[y:y+h, x:x+w]
            face_resized = cv2.resize(face, target_size)
            
            return face_resized
            
        except Exception as e:
            print(f"Error extracting face from base64: {str(e)}")
            return None
    
    def draw_faces(self, image_path, output_path):
        """
        Draw bounding boxes around detected faces
        
        Args:
            image_path (str): Input image path
            output_path (str): Output image path
            
        Returns:
            bool: Success status
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return False
            
            # Detect faces
            faces = self.detect_faces(image_path)
            
            # Draw rectangles
            for face in faces:
                x, y, w, h = face['box']
                confidence = face['confidence']
                
                # Draw rectangle
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Draw confidence
                text = f"{confidence:.2f}"
                cv2.putText(image, text, (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Draw landmarks
                for key, point in face['keypoints'].items():
                    cv2.circle(image, point, 2, (0, 0, 255), 2)
            
            # Save image
            cv2.imwrite(output_path, image)
            return True
            
        except Exception as e:
            print(f"Error drawing faces: {str(e)}")
            return False
    
    def count_faces(self, image_path):
        """
        Count number of faces in image
        
        Args:
            image_path (str): Path to image
            
        Returns:
            int: Number of faces detected
        """
        faces = self.detect_faces(image_path)
        return len(faces)
    
    def get_face_landmarks(self, image_path):
        """
        Get facial landmarks (eyes, nose, mouth)
        
        Args:
            image_path (str): Path to image
            
        Returns:
            list: List of landmarks for each face
        """
        faces = self.detect_faces(image_path)
        landmarks = [face['keypoints'] for face in faces]
        return landmarks
    
    def is_face_frontal(self, face_box, threshold=0.3):
        """
        Check if face is frontal based on landmarks
        
        Args:
            face_box (dict): Face detection result
            threshold (float): Threshold for frontal check
            
        Returns:
            bool: True if face is frontal
        """
        try:
            keypoints = face_box['keypoints']
            
            # Get eye positions
            left_eye = keypoints['left_eye']
            right_eye = keypoints['right_eye']
            
            # Calculate eye distance
            eye_distance = abs(left_eye[0] - right_eye[0])
            
            # Get nose and mouth positions
            nose = keypoints['nose']
            
            # Check if nose is centered between eyes
            eye_center = (left_eye[0] + right_eye[0]) / 2
            nose_offset = abs(nose[0] - eye_center)
            
            # Face is frontal if nose is centered
            is_frontal = (nose_offset / eye_distance) < threshold
            
            return is_frontal
            
        except Exception as e:
            print(f"Error checking frontal face: {str(e)}")
            return False


# Utility functions
def preprocess_face(face_image):
    """
    Preprocess face image for recognition
    
    Args:
        face_image (numpy.ndarray): Face image
        
    Returns:
        numpy.ndarray: Preprocessed face
    """
    # Normalize pixel values
    face_normalized = face_image.astype('float32') / 255.0
    
    # Expand dimensions for model input
    face_expanded = np.expand_dims(face_normalized, axis=0)
    
    return face_expanded


def save_face_image(face_image, output_path):
    """
    Save face image to file
    
    Args:
        face_image (numpy.ndarray): Face image
        output_path (str): Output file path
        
    Returns:
        bool: Success status
    """
    try:
        cv2.imwrite(output_path, face_image)
        return True
    except Exception as e:
        print(f"Error saving face image: {str(e)}")
        return False


# Example usage
if __name__ == "__main__":
    # Initialize detector
    detector = FaceDetector(min_confidence=0.9)
    
    # Test detection
    test_image = "test_image.jpg"
    faces = detector.detect_faces(test_image)
    
    print(f"Detected {len(faces)} faces")
    
    for i, face in enumerate(faces):
        print(f"Face {i+1}:")
        print(f"  Confidence: {face['confidence']:.2f}")
        print(f"  Box: {face['box']}")
        print(f"  Landmarks: {face['keypoints']}")