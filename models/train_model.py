"""
Training script for Face Recognition System
Handles data collection, preprocessing, and model training
"""

import os
import cv2
import numpy as np
import pandas as pd
from models.face_detection import FaceDetector
from models.face_recognition import FaceRecognizer
import json
from datetime import datetime

class ModelTrainer:
    def __init__(self, data_path='static/uploads/student_faces', model_path='models/saved_models'):
        """
        Initialize Model Trainer
        
        Args:
            data_path (str): Path to face images
            model_path (str): Path to save trained model
        """
        self.data_path = data_path
        self.model_path = model_path
        self.face_detector = FaceDetector()
        self.face_recognizer = FaceRecognizer(model_path=model_path)
        
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(model_path, exist_ok=True)
    
    def collect_face_data(self, student_id, name, num_images=5, camera_index=0):
        """
        Collect face images from camera for a student
        
        Args:
            student_id (str): Student ID
            name (str): Student name
            num_images (int): Number of images to collect
            camera_index (int): Camera device index
            
        Returns:
            dict: Collection result
        """
        try:
            print(f"Collecting face data for {name} ({student_id})")
            
            # Create student directory
            student_dir = os.path.join(self.data_path, student_id)
            os.makedirs(student_dir, exist_ok=True)
            
            # Open camera
            cap = cv2.VideoCapture(camera_index)
            
            if not cap.isOpened():
                return {
                    'success': False,
                    'message': 'Cannot open camera'
                }
            
            collected = 0
            print("Press SPACE to capture image, ESC to cancel")
            
            while collected < num_images:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Display frame
                cv2.putText(frame, f"Captured: {collected}/{num_images}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, "Press SPACE to capture", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.imshow('Face Collection', frame)
                
                key = cv2.waitKey(1)
                
                # Capture on SPACE
                if key == 32:  # SPACE
                    # Detect face
                    temp_path = 'temp_frame.jpg'
                    cv2.imwrite(temp_path, frame)
                    
                    faces = self.face_detector.detect_faces(temp_path)
                    
                    if len(faces) == 1:
                        # Extract and save face
                        face_image = self.face_detector.extract_face(temp_path, faces[0])
                        
                        if face_image is not None:
                            image_path = os.path.join(student_dir, f"{student_id}_{collected+1}.jpg")
                            cv2.imwrite(image_path, face_image)
                            collected += 1
                            print(f"Captured {collected}/{num_images}")
                        else:
                            print("Failed to extract face")
                    elif len(faces) == 0:
                        print("No face detected. Try again.")
                    else:
                        print("Multiple faces detected. Ensure only one person in frame.")
                    
                    os.remove(temp_path)
                
                # Cancel on ESC
                elif key == 27:  # ESC
                    print("Collection cancelled")
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            if collected == num_images:
                # Save metadata
                metadata = {
                    'student_id': student_id,
                    'name': name,
                    'num_images': collected,
                    'collection_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                metadata_path = os.path.join(student_dir, 'metadata.json')
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=4)
                
                return {
                    'success': True,
                    'message': f'Collected {collected} images successfully',
                    'images_collected': collected
                }
            else:
                return {
                    'success': False,
                    'message': f'Only collected {collected}/{num_images} images'
                }
                
        except Exception as e:
            print(f"Error collecting face data: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def load_training_data(self):
        """
        Load all face images and labels from data directory
        
        Returns:
            tuple: (face_images, labels)
        """
        face_images = []
        labels = []
        
        try:
            # Iterate through student directories
            for student_id in os.listdir(self.data_path):
                student_dir = os.path.join(self.data_path, student_id)
                
                if not os.path.isdir(student_dir):
                    continue
                
                print(f"Loading data for student: {student_id}")
                
                # Load all images for this student
                for image_file in os.listdir(student_dir):
                    if image_file.endswith(('.jpg', '.jpeg', '.png')):
                        image_path = os.path.join(student_dir, image_file)
                        
                        # Read image
                        image = cv2.imread(image_path)
                        
                        if image is not None:
                            # Resize to standard size
                            image_resized = cv2.resize(image, (224, 224))
                            face_images.append(image_resized)
                            labels.append(student_id)
            
            print(f"Loaded {len(face_images)} images for {len(set(labels))} students")
            
            return face_images, labels
            
        except Exception as e:
            print(f"Error loading training data: {str(e)}")
            return [], []
    
    def train_model(self):
        """
        Train the face recognition model
        
        Returns:
            dict: Training results
        """
        try:
            print("="*50)
            print("Starting Model Training")
            print("="*50)
            
            # Load training data
            print("\n[1/3] Loading training data...")
            face_images, labels = self.load_training_data()
            
            if len(face_images) == 0:
                return {
                    'success': False,
                    'message': 'No training data found'
                }
            
            print(f"Loaded {len(face_images)} images")
            print(f"Number of students: {len(set(labels))}")
            
            # Train model
            print("\n[2/3] Training face recognition model...")
            result = self.face_recognizer.train(face_images, labels)
            
            if result['success']:
                print("\n[3/3] Saving model...")
                
                # Save training log
                log_data = {
                    'training_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'num_samples': result['num_samples'],
                    'num_classes': result['num_classes'],
                    'accuracy': result['accuracy'],
                    'students': list(set(labels))
                }
                
                log_path = os.path.join(self.model_path, 'training_log.json')
                with open(log_path, 'w') as f:
                    json.dump(log_data, f, indent=4)
                
                print("\n" + "="*50)
                print("Training Completed Successfully!")
                print("="*50)
                print(f"Accuracy: {result['accuracy']:.2%}")
                print(f"Students Trained: {result['num_classes']}")
                print(f"Total Samples: {result['num_samples']}")
                print("="*50)
            
            return result
            
        except Exception as e:
            print(f"Error training model: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def test_model(self, test_image_path):
        """
        Test the trained model with a test image
        
        Args:
            test_image_path (str): Path to test image
            
        Returns:
            dict: Test results
        """
        try:
            print(f"\nTesting model with: {test_image_path}")
            
            result = self.face_recognizer.recognize_from_image_path(test_image_path)
            
            if result['success']:
                print(f"Recognized: {result['student_id']}")
                print(f"Confidence: {result['confidence']:.2%}")
            else:
                print(f"Recognition failed: {result['message']}")
            
            return result
            
        except Exception as e:
            print(f"Error testing model: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def retrain_model(self):
        """
        Retrain model with existing and new data
        
        Returns:
            dict: Retraining results
        """
        print("Retraining model with updated data...")
        return self.train_model()
    
    def delete_student_data(self, student_id):
        """
        Delete training data for a specific student
        
        Args:
            student_id (str): Student ID
            
        Returns:
            bool: Success status
        """
        try:
            student_dir = os.path.join(self.data_path, student_id)
            
            if os.path.exists(student_dir):
                import shutil
                shutil.rmtree(student_dir)
                print(f"Deleted data for student: {student_id}")
                
                # Retrain model
                print("Retraining model...")
                self.retrain_model()
                
                return True
            else:
                print(f"No data found for student: {student_id}")
                return False
                
        except Exception as e:
            print(f"Error deleting student data: {str(e)}")
            return False
    
    def get_training_statistics(self):
        """
        Get statistics about training data
        
        Returns:
            dict: Training statistics
        """
        try:
            stats = {
                'total_students': 0,
                'total_images': 0,
                'students': []
            }
            
            for student_id in os.listdir(self.data_path):
                student_dir = os.path.join(self.data_path, student_id)
                
                if os.path.isdir(student_dir):
                    image_count = len([f for f in os.listdir(student_dir) 
                                      if f.endswith(('.jpg', '.jpeg', '.png'))])
                    
                    stats['total_students'] += 1
                    stats['total_images'] += image_count
                    
                    # Load metadata if exists
                    metadata_path = os.path.join(student_dir, 'metadata.json')
                    if os.path.exists(metadata_path):
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                            stats['students'].append({
                                'student_id': student_id,
                                'name': metadata.get('name', 'Unknown'),
                                'num_images': image_count,
                                'collection_date': metadata.get('collection_date', 'Unknown')
                            })
            
            return stats
            
        except Exception as e:
            print(f"Error getting statistics: {str(e)}")
            return {}
    
    def export_embeddings(self, output_path='models/saved_models/face_embeddings.pkl'):
        """
        Export face embeddings for all students
        
        Args:
            output_path (str): Output file path
            
        Returns:
            bool: Success status
        """
        try:
            print("Extracting and exporting face embeddings...")
            
            face_images, labels = self.load_training_data()
            
            if len(face_images) == 0:
                return False
            
            embeddings = {}
            
            for face, label in zip(face_images, labels):
                features = self.face_recognizer.extract_features(face)
                
                if label not in embeddings:
                    embeddings[label] = []
                
                embeddings[label].append(features)
            
            # Save embeddings
            import pickle
            with open(output_path, 'wb') as f:
                pickle.dump(embeddings, f)
            
            print(f"Embeddings exported to {output_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting embeddings: {str(e)}")
            return False


# CLI Interface
def main():
    """Command line interface for model training"""
    trainer = ModelTrainer()
    
    print("\n" + "="*50)
    print("Face Recognition Model Training System")
    print("="*50)
    
    while True:
        print("\nOptions:")
        print("1. Collect face data for new student")
        print("2. Train model")
        print("3. Test model")
        print("4. View training statistics")
        print("5. Delete student data")
        print("6. Export embeddings")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ")
        
        if choice == '1':
            student_id = input("Enter Student ID: ")
            name = input("Enter Student Name: ")
            num_images = int(input("Number of images to collect (default 5): ") or "5")
            
            result = trainer.collect_face_data(student_id, name, num_images)
            print(result['message'])
            
        elif choice == '2':
            result = trainer.train_model()
            if not result['success']:
                print(f"Training failed: {result['message']}")
                
        elif choice == '3':
            test_image = input("Enter path to test image: ")
            trainer.test_model(test_image)
            
        elif choice == '4':
            stats = trainer.get_training_statistics()
            print(f"\nTotal Students: {stats['total_students']}")
            print(f"Total Images: {stats['total_images']}")
            print("\nStudents:")
            for student in stats['students']:
                print(f"  - {student['name']} ({student['student_id']}): {student['num_images']} images")
                
        elif choice == '5':
            student_id = input("Enter Student ID to delete: ")
            confirm = input(f"Are you sure you want to delete data for {student_id}? (yes/no): ")
            if confirm.lower() == 'yes':
                trainer.delete_student_data(student_id)
                
        elif choice == '6':
            trainer.export_embeddings()
            
        elif choice == '7':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()