"""
DESCRIPTION: 
This module contains the computer vision helper functions for face detection 
and deep learning-based face verification (DeepFace).

INPUT: 
Video frames from the main script, the Haar Cascade classifier object, and 
the dictionary of known family member images.

OUTPUT: 
Returns detected faces (bounding boxes), the list of recognized individuals 
in the current frame, and applies bounding boxes/text annotations directly to the frame.
"""

import cv2
import os
from deepface import DeepFace

def detect_faces(frame, face_cascade):
    # Convert the frame to grayscale (required for Haar Cascade face detection)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces using OpenCV's Haar Cascade face detector
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return faces

def verify_and_annotate_faces(frame, faces, family_images):
    current_frame_recognized_faces = []
    
    for (x, y, w, h) in faces:
        # Draw rectangles around the detected faces
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Try to recognize the face
        rgb_face = cv2.cvtColor(frame[y:y+h, x:x+w], cv2.COLOR_BGR2RGB)
        try:
            # Analyze face for age, gender, emotion
            result = DeepFace.analyze(rgb_face, actions=['age', 'gender', 'emotion'], enforce_detection=False)
            
            # Display the recognized face's details (preserving original empty string logic)
            cv2.putText(frame, f"", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            # Verify face against known family members
            for member, image_path in family_images.items():
                if os.path.exists(image_path):
                    verify_result = DeepFace.verify(image_path, rgb_face, enforce_detection=False)
                    if verify_result["verified"]:
                        current_frame_recognized_faces.append(member)
                        
        except Exception as e:
            print(f"Error analyzing face: {e}")
            
    return current_frame_recognized_faces
