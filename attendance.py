"""
Attendance Marking Module
Real-time face recognition and attendance tracking.
"""

import cv2
import os
import pickle
from datetime import datetime
from database import AttendanceDatabase


class AttendanceSystem:
    def __init__(self, db):
        """
        Initialize Attendance System.
        
        Args:
            db: AttendanceDatabase instance
        """
        self.db = db
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.recognizer = None
        self.label_map = None
        self.recognition_threshold = 70  # Lower is more strict (0-100)
        self.marked_today = set()  # Track who has been marked today
    
    def load_recognizer(self):
        """Load the trained face recognizer model."""
        if not os.path.exists('face_recognizer.yml'):
            print("✗ No trained model found. Please register faces first.")
            return False
        
        try:
            # Load recognizer
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
            self.recognizer.read('face_recognizer.yml')
            
            # Build label map from database
            self.label_map = {}
            users = self.db.get_all_users()
            for user_id, roll_number, name in users:
                self.label_map[user_id] = {
                    'roll_number': roll_number,
                    'name': name
                }
            
            print(f"✓ Recognizer loaded with {len(self.label_map)} registered users")
            return True
        except Exception as e:
            print(f"✗ Error loading recognizer: {e}")
            return False
    
    def start_attendance(self):
        """
        Start real-time attendance marking system.
        Recognizes faces and marks attendance automatically.
        """
        if not self.load_recognizer():
            return
        
        print("\n📹 Starting Attendance System...")
        print("━" * 50)
        print("Instructions:")
        print("  • Look at the camera for face recognition")
        print("  • Attendance will be marked automatically")
        print("  • Press 'q' to quit")
        print("━" * 50 + "\n")
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("✗ Error: Could not open webcam")
            return
        
        # Get today's date for duplicate check
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Track already marked attendances
        self.marked_today = set()
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("✗ Error: Failed to capture frame")
                break
            
            frame_count += 1
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100)
            )
            
            # Process each detected face
            for (x, y, w, h) in faces:
                # Extract face region
                face_roi = gray[y:y+h, x:x+w]
                
                # Recognize face
                label, confidence = self.recognizer.predict(face_roi)
                
                # Determine if face is recognized
                if confidence < self.recognition_threshold:
                    # Face recognized
                    user_info = self.label_map.get(label, None)
                    
                    if user_info:
                        name = user_info['name']
                        roll_number = user_info['roll_number']
                        
                        # Draw green rectangle for recognized face
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        
                        # Display name and confidence
                        text = f"{name} ({100-confidence:.1f}%)"
                        cv2.putText(
                            frame,
                            text,
                            (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2
                        )
                        
                        # Mark attendance (only once per day)
                        if label not in self.marked_today:
                            success = self.db.mark_attendance(label)
                            
                            if success:
                                self.marked_today.add(label)
                                current_time = datetime.now().strftime("%H:%M:%S")
                                print(f"✓ Attendance marked: {name} (Roll: {roll_number}) at {current_time}")
                                
                                # Display success message on frame
                                cv2.putText(
                                    frame,
                                    "Attendance Marked!",
                                    (x, y+h+25),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.6,
                                    (0, 255, 0),
                                    2
                                )
                            else:
                                # Already marked today
                                cv2.putText(
                                    frame,
                                    "Already Marked",
                                    (x, y+h+25),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.6,
                                    (0, 200, 200),
                                    2
                                )
                else:
                    # Unknown face
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.putText(
                        frame,
                        "Unknown",
                        (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )
            
            # Display attendance info
            info_text = f"Marked Today: {len(self.marked_today)}"
            cv2.putText(
                frame,
                info_text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
            
            # Display the frame
            cv2.imshow('Attendance System - Press q to quit', frame)
            
            # Check for quit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"\n✓ Attendance session ended")
        print(f"  Total marked today: {len(self.marked_today)}\n")
    
    def view_today_attendance(self):
        """Display attendance records for today."""
        today = datetime.now().strftime("%Y-%m-%d")
        records = self.db.get_attendance_by_date(today)
        
        print(f"\n📊 Attendance for {today}")
        print("━" * 60)
        
        if not records:
            print("No attendance records for today.")
        else:
            print(f"{'Name':<25} {'Roll Number':<15} {'Time':<12} {'Status':<10}")
            print("─" * 60)
            for name, roll, time, status in records:
                print(f"{name:<25} {roll:<15} {time:<12} {status:<10}")
        
        print("━" * 60 + "\n")
        
        def process_frame(frame):
            global registration_active, current_user

            if registration_active:
                face_register.capture_face_samples(
                    frame,
                    current_user["roll_number"],
                    current_user["name"]
                )

            if face_register.is_done():
                registration_active = False

