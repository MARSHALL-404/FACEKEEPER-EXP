"""
Face Registration Module
Captures face images from webcam and stores them for recognition.
"""

import cv2
import os
import numpy as np
from database import AttendanceDatabase


class FaceRegistration:
    def __init__(self, db):
        """
        Initialize Face Registration system.
        
        Args:
            db: AttendanceDatabase instance
        """
        self.db = db
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.known_faces_dir = "known_faces"
        
        if not os.path.exists(self.known_faces_dir):
            os.makedirs(self.known_faces_dir)
    
    def capture_face_samples(self, roll_number, name, num_samples=30):
        """
        Capture multiple face samples for a user.
        
        Args:
            roll_number (str): Unique roll number/ID
            name (str): Full name of the user
            num_samples (int): Number of face samples to capture
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if user already exists
        existing_user = self.db.get_user_by_roll(roll_number)
        if existing_user:
            print(f"\n✗ User with roll number {roll_number} already exists!")
            return False
        
        # Add user to database
        user_id = self.db.add_user(roll_number, name)
        if user_id is None:
            return False
        
        # Create directory for user's face images
        user_dir = os.path.join(self.known_faces_dir, f"{roll_number}_{name.replace(' ', '_')}")
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        
        print(f"\n📸 Starting face capture for {name}...")
        print(f"Please look at the camera. Capturing {num_samples} samples...")
        print("Press 'q' to quit early\n")
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("✗ Error: Could not open webcam")
            return False
        
        count = 0
        
        while count < num_samples:
            ret, frame = cap.read()
            
            if not ret:
                print("✗ Error: Failed to capture frame")
                break
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100)
            )
            
            # Process detected faces
            for (x, y, w, h) in faces:
                # Draw rectangle around face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Save face sample
                face_img = gray[y:y+h, x:x+w]
                face_filename = os.path.join(user_dir, f"face_{count}.jpg")
                cv2.imwrite(face_filename, face_img)
                count += 1
                
                # Display progress
                cv2.putText(
                    frame,
                    f"Captured: {count}/{num_samples}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )
                
                print(f"✓ Captured sample {count}/{num_samples}", end='\r')
            
            # Display the frame
            cv2.imshow('Face Registration - Press q to quit', frame)
            
            # Check for quit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"\n\n✓ Face registration complete for {name}!")
        print(f"  Total samples captured: {count}")
        print(f"  Samples saved in: {user_dir}\n")
        
        # Set the global flag to indicate registration is complete
        try:
            from web.app1 import registration_active
            import web.app1 as app_module
            app_module.registration_active = False
        except:
            pass  # If running without Flask, just skip
        
        return True
    
    def train_recognizer(self):
        """
        Train the face recognizer with all registered faces.
        
        Returns:
            tuple: (recognizer, label_map) if successful, (None, None) otherwise
        """
        faces = []
        labels = []
        label_map = {}
        
        print("\n🔄 Training face recognizer...")
        
        # Get all users from database
        users = self.db.get_all_users()
        
        if not users:
            print("✗ No users found in database")
            return None, None
        
        # Load face samples for each user
        for user_id, roll_number, name in users:
            user_dir = os.path.join(
                self.known_faces_dir,
                f"{roll_number}_{name.replace(' ', '_')}"
            )
            
            if not os.path.exists(user_dir):
                print(f"⚠ Warning: No face samples found for {name}")
                continue
            
            # Store user info in label map
            label_map[user_id] = {'roll_number': roll_number, 'name': name}
            
            # Load all face images for this user
            for img_name in os.listdir(user_dir):
                if img_name.endswith('.jpg'):
                    img_path = os.path.join(user_dir, img_name)
                    face_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    
                    if face_img is not None:
                        faces.append(face_img)
                        labels.append(user_id)
        
        if len(faces) == 0:
            print("✗ No face samples found to train")
            return None, None
        
        # Create and train LBPH Face Recognizer
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces, np.array(labels))
        
        # Save the trained model
        recognizer.write('face_recognizer.yml')
        
        print(f"✓ Training complete!")
        print(f"  Total faces trained: {len(faces)}")
        print(f"  Total users: {len(label_map)}\n")
        
        return recognizer, label_map
