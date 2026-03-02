import cv2
import numpy as np

from models.face_detection import FaceDetector
from utils.hybrid_face_detection import hybrid_face_detection, HybridDetectionConfig


_HYBRID_DETECTOR = None


def _get_detector():
    global _HYBRID_DETECTOR
    if _HYBRID_DETECTOR is None:
        # Fast proposals (Haar) + accurate refine (MTCNN) + fallback to full MTCNN.
        _HYBRID_DETECTOR = FaceDetector(
            mode="hybrid",
            min_confidence=0.85,
            min_face_size=20,
            haar_min_size=(100, 100),
        )
    return _HYBRID_DETECTOR


def detect_face_simple(image_np):
    """
    Fast + accurate face detection (Haar + MTCNN hybrid).
    
    Args:
        image_np (numpy.ndarray): Image array in BGR format
        
    Returns:
        list: List of detected faces (rectangles)
    """
    try:
        # Prefer the explicit hybrid pipeline (Haar proposals + ROI MTCNN refine).
        # Falls back to Haar-only automatically if mtcnn isn't installed.
        config = HybridDetectionConfig(min_confidence=0.90, min_box_size=40, draw_landmarks=False)
        _, faces = hybrid_face_detection(image_np, config=config)
        rects = [tuple(f["box"]) for f in faces]
        print(f"Detected {len(rects)} face(s)")
        return rects
        
    except Exception as e:
        print(f"❌ Face detection error: {e}")
        return []
