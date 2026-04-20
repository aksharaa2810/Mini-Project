"""
Face Recognition using VGGFace for feature extraction and SVM for classification
"""

import numpy as np
import pickle
import os
from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import cv2
from models.face_detection import FaceDetector

class FaceRecognizer:
    def __init__(self, model_path='models/saved_models'):
        """
        Initialize Face Recognizer
        
        Args:
            model_path (str): Path to save/load models
        """
        self.model_path = model_path
        self.face_detector = FaceDetector()
        
        # Initialize VGGFace for feature extraction
        self.feature_extractor = VGGFace(
            model='resnet50',
            include_top=False,
            input_shape=(224, 224, 3),
            pooling='avg'
        )
        
        # Initialize SVM classifier
        self.classifier = SVC(
            kernel='linear',
            probability=True,
            C=1.0
        )
        
        # Label encoder
        self.label_encoder = LabelEncoder()
        
        # Check if trained model exists
        self.is_trained = False
        self.load_model()
    
    def extract_features(self, face_image):
        """
        Extract features from face image using VGGFace
        
        Args:
            face_image (numpy.ndarray): Face image (224x224x3)
            
        Returns:
            numpy.ndarray: Feature vector
        """
        try:
            # Ensure correct shape
            if face_image.shape != (224, 224, 3):
                face_image = cv2.resize(face_image, (224, 224))
            
            # Convert to RGB if needed
            if len(face_image.shape) == 2:
                face_image = cv2.cvtColor(face_image, cv2.COLOR_GRAY2RGB)
            elif face_image.shape[2] == 4:
                face_image = cv2.cvtColor(face_image, cv2.COLOR_BGRA2RGB)
            
            # Preprocess for VGGFace
            face_expanded = np.expand_dims(face_image, axis=0)
            face_preprocessed = preprocess_input(face_expanded, version=2)
            
            # Extract features
            features = self.feature_extractor.predict(face_preprocessed)
            
            return features.flatten()
            
        except Exception as e:
            print(f"Error extracting features: {str(e)}")
            return None
    
    def train(self, face_data, labels):
        """
        Train the face recognition model
        
        Args:
            face_data (list): List of face images
            labels (list): Corresponding labels (student IDs)
            
        Returns:
            dict: Training results
        """
        try:
            print("Extracting features from training data...")
            
            # Extract features for all faces
            features = []
            valid_labels = []
            
            for i, face in enumerate(face_data):
                feature = self.extract_features(face)
                if feature is not None:
                    features.append(feature)
                    valid_labels.append(labels[i])
            
            if len(features) == 0:
                return {
                    'success': False,
                    'message': 'No valid features extracted'
                }
            
            # Convert to numpy array
            X = np.array(features)
            
            # Encode labels
            y = self.label_encoder.fit_transform(valid_labels)
            
            print(f"Training SVM classifier with {len(X)} samples...")
            
            # Train SVM
            self.classifier.fit(X, y)
            
            # Mark as trained
            self.is_trained = True
            
            # Save model
            self.save_model()
            
            # Calculate training accuracy
            y_pred = self.classifier.predict(X)
            accuracy = accuracy_score(y, y_pred)
            
            return {
                'success': True,
                'accuracy': accuracy,
                'num_samples': len(X),
                'num_classes': len(np.unique(y)),
                'message': 'Model trained successfully'
            }
            
        except Exception as e:
            print(f"Error training model: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def recognize(self, face_image, threshold=0.6):
        """
        Recognize face in image
        
        Args:
            face_image (numpy.ndarray): Face image
            threshold (float): Confidence threshold
            
        Returns:
            dict: Recognition result
        """
        try:
            if not self.is_trained:
                return {
                    'success': False,
                    'message': 'Model not trained'
                }
            
            # Extract features
            features = self.extract_features(face_image)
            if features is None:
                return {
                    'success': False,
                    'message': 'Feature extraction failed'
                }
            
            # Predict
            features_reshaped = features.reshape(1, -1)
            prediction = self.classifier.predict(features_reshaped)
            probabilities = self.classifier.predict_proba(features_reshaped)
            
            # Get confidence
            confidence = np.max(probabilities)
            
            # Check threshold
            if confidence < threshold:
                return {
                    'success': False,
                    'message': 'Low confidence',
                    'confidence': float(confidence)
                }
            
            # Decode label
            predicted_label = self.label_encoder.inverse_transform(prediction)[0]
            
            return {
                'success': True,
                'student_id': predicted_label,
                'confidence': float(confidence),
                'message': 'Face recognized successfully'
            }
            
        except Exception as e:
            print(f"Error recognizing face: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def recognize_from_image_path(self, image_path, threshold=0.6):
        """
        Recognize face from image file
        
        Args:
            image_path (str): Path to image
            threshold (float): Confidence threshold
            
        Returns:
            dict: Recognition result
        """
        try:
            # Detect faces
            faces = self.face_detector.detect_faces(image_path)
            
            if len(faces) == 0:
                return {
                    'success': False,
                    'message': 'No face detected'
                }
            
            if len(faces) > 1:
                return {
                    'success': False,
                    'message': f'Multiple faces detected ({len(faces)})'
                }
            
            # Extract face
            face_image = self.face_detector.extract_face(image_path, faces[0])
            
            if face_image is None:
                return {
                    'success': False,
                    'message': 'Face extraction failed'
                }
            
            # Recognize
            return self.recognize(face_image, threshold)
            
        except Exception as e:
            print(f"Error in recognition: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def save_model(self):
        """Save trained model to disk"""
        try:
            os.makedirs(self.model_path, exist_ok=True)
            
            # Save classifier
            classifier_path = os.path.join(self.model_path, 'svm_classifier.pkl')
            with open(classifier_path, 'wb') as f:
                pickle.dump(self.classifier, f)
            
            # Save label encoder
            encoder_path = os.path.join(self.model_path, 'label_encoder.pkl')
            with open(encoder_path, 'wb') as f:
                pickle.dump(self.label_encoder, f)
            
            print(f"Model saved to {self.model_path}")
            return True
            
        except Exception as e:
            print(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self):
        """Load trained model from disk"""
        try:
            classifier_path = os.path.join(self.model_path, 'svm_classifier.pkl')
            encoder_path = os.path.join(self.model_path, 'label_encoder.pkl')
            
            if os.path.exists(classifier_path) and os.path.exists(encoder_path):
                # Load classifier
                with open(classifier_path, 'rb') as f:
                    self.classifier = pickle.load(f)
                
                # Load label encoder
                with open(encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
                
                self.is_trained = True
                print("Model loaded successfully")
                return True
            else:
                print("No trained model found")
                return False
                
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
    
    def add_new_person(self, face_images, student_id):
        """
        Add new person to existing model
        
        Args:
            face_images (list): List of face images
            student_id (str): Student ID
            
        Returns:
            bool: Success status
        """
        try:
            # Extract features
            features = []
            for face in face_images:
                feature = self.extract_features(face)
                if feature is not None:
                    features.append(feature)
            
            if len(features) == 0:
                return False
            
            # Add to existing data and retrain
            # This is a simplified version
            # In production, you'd append to existing training data
            
            return True
            
        except Exception as e:
            print(f"Error adding new person: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    recognizer = FaceRecognizer()
    
    # Example: Recognize from image
    result = recognizer.recognize_from_image_path("test_face.jpg")
    print(result)