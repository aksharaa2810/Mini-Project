"""
Face Detection using MTCNN
Detects multiple faces in images with high accuracy using Multi-task Cascaded
Convolutional Networks. Supports tuning for better multi-face and small-face detection.
"""

import cv2
import numpy as np
from mtcnn import MTCNN
from PIL import Image
import base64
from io import BytesIO
import os


def _iou(box1, box2):
    """Compute Intersection over Union of two boxes [x, y, w, h]."""
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    xi1 = max(x1, x2)
    yi1 = max(y1, y2)
    xi2 = min(x1 + w1, x2 + w2)
    yi2 = min(y1 + h1, y2 + h2)
    if xi2 <= xi1 or yi2 <= yi1:
        return 0.0
    inter = (xi2 - xi1) * (yi2 - yi1)
    a1 = w1 * h1
    a2 = w2 * h2
    return inter / (a1 + a2 - inter + 1e-6)


def _nms(faces, iou_threshold=0.5):
    """Non-maximum suppression: keep one box per face, prefer higher confidence."""
    if not faces:
        return []
    boxes = [f["box"] for f in faces]
    confs = [f["confidence"] for f in faces]
    keep = []
    order = np.argsort(confs)[::-1]
    used = [False] * len(faces)
    for i in order:
        if used[i]:
            continue
        keep.append(i)
        for j in range(len(faces)):
            if used[j]:
                continue
            if _iou(boxes[i], boxes[j]) > iou_threshold:
                used[j] = True
    return [faces[k] for k in sorted(keep)]


class FaceDetector:
    def __init__(self, min_confidence=0.9, min_face_size=20, use_nms=True, nms_iou_threshold=0.5,
                 mtcnn_kwargs=None):
        """
        Initialize MTCNN face detector for high-accuracy multiple face detection.

        Args:
            min_confidence (float): Minimum confidence threshold for detection (0–1).
            min_face_size (int): Minimum face size in pixels (smaller = detect more/distant faces).
            use_nms (bool): Apply NMS to remove overlapping duplicate boxes.
            nms_iou_threshold (float): IoU threshold for NMS (overlapping boxes above this are merged).
            mtcnn_kwargs (dict): Optional kwargs passed to MTCNN.detect_faces() for tuning, e.g.:
                scale_factor (float): Image pyramid scale (default 0.709; lower = more scales, slower).
                threshold_pnet, threshold_rnet, threshold_onet (float): Stage thresholds.
        """
        self.detector = MTCNN()
        self.min_confidence = min_confidence
        self.min_face_size = min_face_size
        self.use_nms = use_nms
        self.nms_iou_threshold = nms_iou_threshold
        self.mtcnn_kwargs = mtcnn_kwargs or {}

    def _filter_and_sort(self, results):
        """Filter by confidence, optionally NMS, and sort by confidence descending."""
        faces = []
        for res in results:
            conf = res.get("confidence", 0)
            if conf >= self.min_confidence:
                faces.append({
                    "box": res["box"],
                    "confidence": conf,
                    "keypoints": res.get("keypoints", {})
                })
        if self.use_nms and len(faces) > 1:
            faces = _nms(faces, self.nms_iou_threshold)
        faces.sort(key=lambda f: f["confidence"], reverse=True)
        return faces

    def detect_faces(self, image_path):
        """
        Detect all faces in an image file using MTCNN (multiple faces, high accuracy).

        Args:
            image_path (str): Path to image file.

        Returns:
            list: List of detected face dicts with 'box', 'confidence', 'keypoints'.
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return []

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            kwargs = {"min_face_size": self.min_face_size, **self.mtcnn_kwargs}
            try:
                results = self.detector.detect_faces(image_rgb, **kwargs)
            except TypeError:
                results = self.detector.detect_faces(image_rgb)

            faces = self._filter_and_sort(results)
            print(f"Detected {len(faces)} face(s) using MTCNN")
            return faces

        except Exception as e:
            print(f"Error in MTCNN detection: {str(e)}")
            return []
    
    def detect_faces_from_base64(self, base64_string):
        """
        Detect all faces from base64 encoded image (multiple faces, high accuracy).

        Args:
            base64_string (str): Base64 encoded image string.

        Returns:
            list: List of detected face dicts with 'box', 'confidence', 'keypoints'.
        """
        try:
            if "," in base64_string:
                base64_string = base64_string.split(",")[1]

            image_data = base64.b64decode(base64_string)
            image = Image.open(BytesIO(image_data))
            image_np = np.array(image.convert("RGB"))

            kwargs = {"min_face_size": self.min_face_size, **self.mtcnn_kwargs}
            try:
                results = self.detector.detect_faces(image_np, **kwargs)
            except TypeError:
                results = self.detector.detect_faces(image_np)

            return self._filter_and_sort(results)

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
            
            # Ensure coordinates are within image bounds
            img_h, img_w = image.shape[:2]
            x, y = max(0, x), max(0, y)
            w = min(w, img_w - x)
            h = min(h, img_h - y)
            
            # Extract face
            face = image[y:y+h, x:x+w]
            
            if face.size == 0:
                return None
            
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
            
            # Ensure coordinates are within image bounds
            img_h, img_w = image_np.shape[:2]
            x, y = max(0, x), max(0, y)
            w = min(w, img_w - x)
            h = min(h, img_h - y)
            
            # Extract and resize face
            face = image_np[y:y+h, x:x+w]
            
            if face.size == 0:
                return None
                
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
                if 'keypoints' in face:
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
            keypoints = face_box.get('keypoints', {})
            if not keypoints:
                return True
            
            # Get eye positions
            left_eye = keypoints.get('left_eye')
            right_eye = keypoints.get('right_eye')
            nose = keypoints.get('nose')
            
            if not all([left_eye, right_eye, nose]):
                return True
            
            # Calculate eye distance
            eye_distance = abs(left_eye[0] - right_eye[0])
            if eye_distance == 0:
                return True
            
            # Check if nose is centered between eyes
            eye_center = (left_eye[0] + right_eye[0]) / 2
            nose_offset = abs(nose[0] - eye_center)
            
            # Face is frontal if nose is centered
            is_frontal = (nose_offset / eye_distance) < threshold
            
            return is_frontal
            
        except Exception as e:
            print(f"Error checking frontal face: {str(e)}")
            return True


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
    if os.path.exists(test_image):
        faces = detector.detect_faces(test_image)
        
        print(f"Detected {len(faces)} faces")
        
        for i, face in enumerate(faces):
            print(f"Face {i+1}:")
            print(f"  Confidence: {face['confidence']:.2f}")
            print(f"  Box: {face['box']}")
            print(f"  Landmarks: {face['keypoints']}")
    else:
        print(f"Test image {test_image} not found")