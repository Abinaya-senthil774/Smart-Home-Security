"""
DESCRIPTION: 
The main runner script for the exterior security system. It ties together the camera feed, 
motion detection (MOG2), face recognition utilities, and Tkinter UI alerts.

INPUT: 
Real-time feed from cv2.VideoCapture(0).

OUTPUT: 
Renders the live annotated video feed, prints console logs, and triggers UI alerts 
based on occupancy and verification logic.
"""

import cv2
import numpy as np

# Import our custom modules
from ui_alerts import ask_user
from vision_utils import detect_faces, verify_and_annotate_faces

# Load the reference images of family members for face recognition
family_images = {
    "Family Member 1": r"C:\Users\sabin\OneDrive\Pictures\Camera Roll\WIN_20250320_19_37_38_Pro.jpg",
    "Family Member 2": r"C:\Users\sabin\OneDrive\Pictures\Camera Roll\WIN_20250320_19_37_38_Pro.jpg"
    # Add as many family members as needed
}

# Initialize video capture (camera feed)
video_capture = cv2.VideoCapture(0)

# Load OpenCV face detector (Haar Cascade)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# State Tracking Variables
room_occupancy_count = 0
alert_sent = False
faces_asked = set()          # Track faces that have already been asked
recognized_people = set()    # Keep track of recognized people
previous_occupancy_count = 0 # Track the previous occupancy count to avoid redundant alerts

# Motion detection setup
fgbg = cv2.createBackgroundSubtractorMOG2()
motion_detected = False      # Flag to track if motion was detected

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    # 1. Detect Faces
    faces = detect_faces(frame, face_cascade)
    
    # Count the number of detected faces and update the occupancy count
    room_occupancy_count = len(faces)

    # 2. Verify Faces & Annotate Frame
    current_frame_recognized_faces = verify_and_annotate_faces(frame, faces, family_images)

    # 3. Logic based on Occupancy Count
    
    # IF 0 PEOPLE: Enable motion detection
    if room_occupancy_count == 0:
        fgmask = fgbg.apply(frame)  # Apply the background subtractor to detect motion
        motion_pixels = np.count_nonzero(fgmask)

        if motion_pixels > 5000:  # If significant motion is detected
            motion_detected = True
            cv2.putText(frame, "ALERT: Motion Detected from Unknown Person!", (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            if not alert_sent:
                print("⚠️ ALERT: Suspicious activity detected!")
                response = ask_user()  # Ask the user if they recognize the person
                if response == 'yes':
                    print("No further alerts will be sent.")
                    alert_sent = True
                elif response == 'no':
                    print("⚠️ ALERT: Unknown person is in the house!")
                    alert_sent = True

    # IF 1 PERSON: Check for face verification
    if room_occupancy_count == 1 and room_occupancy_count != previous_occupancy_count:
        print("One person detected.")
        for face_member in current_frame_recognized_faces:
            if face_member in family_images:
                print(f"Family member {face_member} recognized. No alert needed.")
            else:
                if face_member not in faces_asked:
                    print(f"Unrecognized person: {face_member}. Asking user.")
                    response = ask_user()
                    faces_asked.add(face_member)
                    if response == 'yes':
                        print(f"{face_member} is known. No further alerts needed.")
                    elif response == 'no':
                        print(f"⚠️ ALERT: Unknown person detected!")
                        alert_sent = True
                        break
        previous_occupancy_count = room_occupancy_count

    # IF 2 PEOPLE: Check for new faces
    if room_occupancy_count == 2 and room_occupancy_count != previous_occupancy_count:
        print("Two people detected.")
        for face_member in current_frame_recognized_faces:
            if face_member in family_images:
                print(f"Family member {face_member} recognized. No alert needed.")
            else:
                if face_member not in faces_asked:
                    print(f"Unrecognized person: {face_member}. Asking user.")
                    response = ask_user()
                    faces_asked.add(face_member)
                    if response == 'yes':
                        print(f"{face_member} is known. No further alerts needed.")
                    elif response == 'no':
                        print(f"⚠️ ALERT: Unknown person detected!")
                        alert_sent = True
                        break
        previous_occupancy_count = room_occupancy_count

    # IF > 2 PEOPLE: Ask owner about new faces
    if room_occupancy_count > 2 and room_occupancy_count != previous_occupancy_count:
        print(f"⚠️ ALERT: {room_occupancy_count} people detected!")
        for (x, y, w, h) in faces:
            response = ask_user()  # Ask owner if they know the person
            if response == 'yes':
                print("Person recognized. No further alerts needed.")
            elif response == 'no':
                print(f"⚠️ ALERT: Unknown person detected!")
                alert_sent = True
        previous_occupancy_count = room_occupancy_count

    # 4. Display Info & Render
    
    # Display the current room occupancy count in a fixed position (bottom left corner)
    cv2.putText(frame, f"Occupancy Count: {room_occupancy_count}", (10, 450), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    # Show the live feed
    cv2.imshow("Video Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
